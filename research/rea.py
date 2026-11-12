#!/usr/bin/env python3
"""Local REA launcher and private product investigation workspace (stdlib only)."""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
import unicodedata
from uuid import uuid4

ROOT = Path(__file__).resolve().parent
VERSION = "6.8.0"
RUNTIME = ROOT / ".runtime"
PACKAGE = RUNTIME / "node_modules" / "rea-agents"
CASES = ROOT / "cases"


def supported(version):
    match = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)", version.strip())
    if not match:
        return False
    major, minor, patch = map(int, match.groups())
    return ((major == 22 and (minor, patch) >= (23, 4)) or
            (major == 24 and (minor, patch) >= (22, 1)) or
            (major, minor, patch) >= (26, 12, 1))


def select_node():
    override = os.environ.get("REA_NODE")
    candidates = [override] if override else [
        shutil.which("node"),
        "/usr/local/bin/node",
        "/Applications/ChatGPT.app/Contents/Resources/cua_node/bin/node",
        *map(str, sorted((Path.home() / ".nvm/versions/node").glob("*/bin/node"), reverse=True)),
    ]
    for candidate in dict.fromkeys(candidates):
        if not candidate:
            continue
        try:
            result = subprocess.run([candidate, "--version"], capture_output=True,
                                    text=True, timeout=5, check=False)
            if result.returncode == 0 and supported(result.stdout):
                return str(Path(candidate).resolve()), result.stdout.strip()
        except (OSError, subprocess.TimeoutExpired):
            continue
    raise RuntimeError("Uyumlu Node bulunamadı. Node 22.23.4+, 24.22.1+ veya 26.12.1+ kullan; "
                       "23 ve 25 desteklenmez. Mevcut bir sürümü REA_NODE ile seçebilirsin.")


def rea_command():
    node, _ = select_node()
    manifest = PACKAGE / "package.json"
    if not manifest.is_file():
        raise RuntimeError("REA kurulmamış. Önce: python3 research/rea.py install")
    data = json.loads(manifest.read_text())
    if data.get("name") != "rea-agents" or data.get("version") != VERSION:
        raise RuntimeError(f"Beklenen paket rea-agents@{VERSION}; kurulu paket farklı.")
    entry = PACKAGE / "scripts/rea.mjs"
    if not entry.is_file():
        raise RuntimeError("REA giriş dosyası eksik; kurulumu tekrar çalıştır.")
    return [node, str(entry)]


def install():
    node, version = select_node()
    npm = shutil.which("npm")
    if npm is None:
        raise RuntimeError("npm bulunamadı; mevcut Node kurulumunun npm komutunu PATH'e ekle.")
    RUNTIME.mkdir(parents=True, exist_ok=True)
    manifest = RUNTIME / "package.json"
    desired = {"name": "rea-research-runtime", "private": True,
               "dependencies": {"rea-agents": VERSION}}
    if manifest.exists() and json.loads(manifest.read_text()) != desired:
        raise RuntimeError("Yerel runtime package.json farklı; mevcut yapılandırma korundu.")
    if not manifest.exists():
        with manifest.open("x") as stream:
            json.dump(desired, stream, indent=2)
            stream.write("\n")
    env = os.environ.copy()
    env["PATH"] = str(Path(node).parent) + os.pathsep + env.get("PATH", "")
    print(f"REA {VERSION} kuruluyor; {node} ({version}).", flush=True)
    # Reuse the exact dependency lock on subsequent runs. All writes stay local.
    operation = "ci" if (RUNTIME / "package-lock.json").is_file() else "install"
    result = subprocess.run([node, str(Path(npm).resolve()), operation, "--omit=dev",
                             "--no-audit", "--no-fund", "--cache", str(ROOT / ".cache/npm")],
                            cwd=RUNTIME, env=env, check=False)
    if result.returncode:
        return result.returncode
    return check()


def check():
    node, version = select_node()
    print(f"Node: {version} ({node})", flush=True)
    result = subprocess.run([*rea_command(), "--version", "--json"], check=False)
    if result.returncode == 0:
        print("REA CLI başlatıldı. Bu kontrol MCP kaydını veya analiz motorlarını doğrulamaz.")
    return result.returncode


def slug(text):
    text = text.translate(str.maketrans("ıİşŞğĞüÜöÖçÇ", "iIsSgGuUoOcC"))
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")[:64] or "urun"


def new_case(name, target, questions, root=CASES):
    if not name.strip() or not target.strip():
        raise ValueError("Ürün adı ve hedef boş olamaz.")
    stamp = datetime.now(timezone.utc)
    case_id = f"{stamp:%Y%m%d}-{slug(name)}-{uuid4().hex[:8]}"
    directory = root / case_id
    directory.mkdir(parents=True, exist_ok=False)
    (directory / "evidence").mkdir()
    record = {"schema_version": 1, "id": case_id, "product": name, "target": target,
              "created_at": stamp.isoformat(), "status": "planned",
              "questions": questions, "rea_version": None, "limitations": []}
    (directory / "case.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    report = (ROOT / "templates/report.tr.md").read_text()
    report = report.replace("{{PRODUCT}}", name).replace("{{TARGET}}", target)
    report = report.replace("{{QUESTIONS}}", "\n".join(f"- [ ] {q}" for q in questions) or
                            "- [ ] Ürünün ana kullanıcı akışı nasıl çalışıyor?")
    (directory / "report.md").write_text(report)
    print(directory)
    return directory


def list_cases(root=CASES):
    records = []
    for path in sorted(root.glob("*/case.json")):
        try:
            data = json.loads(path.read_text())
            if not isinstance(data, dict) or not all(
                isinstance(data.get(field), str) for field in ("product", "status")
            ):
                raise ValueError("case.json product ve status metin alanlarını içermeli")
            records.append({"id": path.parent.name, "product": data["product"],
                            "status": data["status"], "report": str(path.parent / "report.md")})
        except (OSError, ValueError, KeyError) as error:
            records.append({"id": path.parent.name, "status": "invalid", "error": str(error)})
    print(json.dumps(records, ensure_ascii=False, indent=2))
    return records


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("install", help="Sabit REA sürümünü yalnızca bu alana kur")
    commands.add_parser("check", help="Node ve gerçek REA CLI başlangıcını kontrol et")
    new = commands.add_parser("new", help="Ürün için özel inceleme kaydı aç")
    new.add_argument("name")
    new.add_argument("--target", required=True)
    new.add_argument("--question", action="append", default=[])
    commands.add_parser("list", help="Yerel incelemeleri listele")
    run = commands.add_parser("run", help="Argümanları REA CLI'ya aynen geçir")
    run.add_argument("args", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    try:
        if args.command == "install":
            return install()
        if args.command == "check":
            return check()
        if args.command == "new":
            new_case(args.name, args.target, args.question)
        elif args.command == "list":
            list_cases()
        else:
            forwarded = args.args[1:] if args.args[:1] == ["--"] else args.args
            return subprocess.run([*rea_command(), *forwarded], check=False).returncode
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(f"REA çalışma alanı: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
