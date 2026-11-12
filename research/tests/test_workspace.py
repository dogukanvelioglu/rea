import contextlib
import importlib.util
import io
import json
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit

spec = importlib.util.spec_from_file_location("rea_workspace", Path(__file__).parents[1] / "rea.py")
workspace = importlib.util.module_from_spec(spec)
spec.loader.exec_module(workspace)


class WorkspaceTests(unittest.TestCase):
    def test_node_security_patch_boundaries(self):
        for version in ["22.23.4", "24.22.1", "26.12.1", "v28.0.0"]:
            self.assertTrue(workspace.supported(version), version)
        for version in ["20.20.2", "22.23.3", "24.22.0", "25.9.0", "26.12.0", "v24.22.1-rc.1", "nonsense"]:
            self.assertFalse(workspace.supported(version), version)

    def test_cases_preserve_inputs_without_path_traversal_or_overwrite(self):
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()):
            root = Path(temp)
            name = "../../Ürün Şirketi"
            target = "https://example.com/a?x=1&y=2"
            first = workspace.new_case(name, target, ["Arama nasıl?"], root)
            second = workspace.new_case(name, target, [], root)
            self.assertEqual(first.parent, root)
            self.assertNotEqual(first, second)
            record = json.loads((first / "case.json").read_text())
            self.assertEqual(record["product"], name)
            self.assertEqual(record["target"], target)
            self.assertEqual(record["status"], "planned")
            self.assertIsNone(record["rea_version"])
            self.assertIn("Arama nasıl?", (first / "report.md").read_text())
            self.assertTrue((first / "evidence").is_dir())
            default_record = json.loads((second / "case.json").read_text())
            self.assertEqual(default_record["questions"], [workspace.DEFAULT_QUESTION])
            self.assertIn(workspace.DEFAULT_QUESTION, (second / "report.md").read_text())
            if workspace.os.name == "posix":
                self.assertEqual(stat.S_IMODE(first.stat().st_mode), 0o700)

    def test_report_keeps_inputs_as_text_and_preserves_raw_case_values(self):
        name = "Ürün {{TARGET}}\n## Diğer başlık"
        target = "https://example.com/?q={{QUESTIONS}}"
        questions = ["[Bağlantı](https://example.com)\n- [ ] başka madde"]
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()):
            directory = workspace.new_case(name, target, questions, Path(temp))
            record = json.loads((directory / "case.json").read_text())
            report = (directory / "report.md").read_text()
        self.assertEqual([record["product"], record["target"], record["questions"]],
                         [name, target, questions])
        self.assertNotIn("\n## Diğer başlık", report)
        self.assertIn(r"\{\{TARGET\}\}", report)
        self.assertIn(r"\{\{QUESTIONS\}\}", report)
        self.assertEqual(sum(line.startswith("- [ ]") for line in report.splitlines()), 1)
        self.assertIn(r"\[Bağlantı\]", report)

    def test_empty_input_does_not_create_a_case(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with self.assertRaises(ValueError):
                workspace.new_case("  ", "https://example.com", [], root)
            self.assertEqual(list(root.iterdir()), [])

    def test_corrupt_record_does_not_hide_other_cases(self):
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()):
            root = Path(temp)
            valid = workspace.new_case("Valid", "https://example.com", [], root)
            (root / "bad").mkdir()
            (root / "bad/case.json").write_text("not json")
            (root / "wrong-shape").mkdir()
            (root / "wrong-shape/case.json").write_text("[]")
            records = workspace.list_cases(root)
            self.assertEqual(len(records), 3)
            self.assertTrue(any(r["id"] == valid.name and r["status"] == "planned" for r in records))
            self.assertTrue(any(r["id"] == "bad" and r["status"] == "invalid" for r in records))
            self.assertTrue(any(r["id"] == "wrong-shape" and r["status"] == "invalid" for r in records))

    def test_wrong_runtime_is_not_silently_launched(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package = root / workspace.PACKAGE_PATH
            package.mkdir(parents=True)
            (package / "package.json").write_text(json.dumps({"name": "rea-agents", "version": "0.0.0"}))
            with patch.object(workspace, "RUNTIME", root), patch.object(workspace, "select_node", return_value=("/node", "v24.22.1")):
                with self.assertRaisesRegex(RuntimeError, "farklı"):
                    workspace.rea_command()

    def test_missing_runtime_check_fails_without_success_claim(self):
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
            with patch.object(workspace, "RUNTIME", Path(temp)), patch.object(workspace, "select_node", return_value=("/node", "v24.22.1")):
                self.assertEqual(workspace.main(["check"]), 1)
            self.assertNotIn("CLI başlatıldı", out.getvalue())

    def test_failed_install_keeps_prior_runtime_and_cleans_staging(self):
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()):
            root = Path(temp)
            legacy = root / workspace.PACKAGE_PATH
            legacy.mkdir(parents=True)
            marker = legacy / "existing"
            marker.write_text("keep")
            with (
                patch.object(workspace, "RUNTIME", root),
                patch.object(workspace, "select_node", return_value=("/node", "v24.22.1")),
                patch.object(workspace.shutil, "which", return_value="/npm"),
                patch.object(workspace.subprocess, "run") as run,
            ):
                run.return_value.returncode = 12
                self.assertEqual(workspace.install(), 12)
            self.assertIn("ci", run.call_args.args[0])
            self.assertIn("--ignore-scripts", run.call_args.args[0])
            self.assertEqual(marker.read_text(), "keep")
            self.assertEqual(list(root.iterdir()), [root / "node_modules"])

    def test_runtime_lock_pins_registry_packages_with_integrity(self):
        version, lock, _ = workspace.runtime_pin()
        lock = json.loads(lock)
        self.assertEqual(lock["lockfileVersion"], 3)
        self.assertEqual(lock["packages"][""]["dependencies"], {"rea-agents": version})
        self.assertEqual(lock["packages"]["node_modules/rea-agents"]["version"], version)
        for name, package in lock["packages"].items():
            if name:
                with self.subTest(package=name):
                    url = urlsplit(package["resolved"])
                    self.assertEqual((url.scheme, url.netloc), ("https", "registry.npmjs.org"))
                    self.assertRegex(package["integrity"], r"^sha512-[A-Za-z0-9+/]+={0,2}$")

    def test_cli_preserves_literal_arguments_and_exit_status(self):
        args = ["analyze-javascript-application", "/some app/$(literal)", "--json"]
        with patch.object(workspace, "rea_command", return_value=["/node", "/rea.mjs"]), patch.object(workspace.subprocess, "run") as run:
            run.return_value.returncode = 7
            self.assertEqual(workspace.main(["run", "--", *args]), 7)
            run.assert_called_once_with(["/node", "/rea.mjs", *args], check=False)


if __name__ == "__main__":
    unittest.main()
