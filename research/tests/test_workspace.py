import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

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
            (root / "package.json").write_text(json.dumps({"name": "rea-agents", "version": "0.0.0"}))
            with patch.object(workspace, "PACKAGE", root), patch.object(workspace, "select_node", return_value=("/node", "v24.22.1")):
                with self.assertRaisesRegex(RuntimeError, "farklı"):
                    workspace.rea_command()

    def test_missing_runtime_check_fails_without_success_claim(self):
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
            with patch.object(workspace, "PACKAGE", Path(temp)), patch.object(workspace, "select_node", return_value=("/node", "v24.22.1")):
                self.assertEqual(workspace.main(["check"]), 1)
            self.assertNotIn("CLI başlatıldı", out.getvalue())

    def test_cli_preserves_literal_arguments_and_exit_status(self):
        args = ["analyze-javascript-application", "/some app/$(literal)", "--json"]
        with patch.object(workspace, "rea_command", return_value=["/node", "/rea.mjs"]), patch.object(workspace.subprocess, "run") as run:
            run.return_value.returncode = 7
            self.assertEqual(workspace.main(["run", "--", *args]), 7)
            run.assert_called_once_with(["/node", "/rea.mjs", *args], check=False)


if __name__ == "__main__":
    unittest.main()
