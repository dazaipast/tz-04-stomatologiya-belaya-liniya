# -*- coding: utf-8 -*-
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    if len(sys.argv) < 2:
        print("Пример: python tools/set_public_url.py https://name.vercel.app G-ABCDE12345 https://script.google.com/macros/s/.../exec")
        raise SystemExit(1)
    config_path = ROOT / "tools" / "site_config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["publicOrigin"] = sys.argv[1].rstrip("/")
    if len(sys.argv) >= 3 and sys.argv[2].strip():
        config["gaMeasurementId"] = sys.argv[2].strip()
    if len(sys.argv) >= 4:
        config["appsScriptUrl"] = sys.argv[3].strip()
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    subprocess.check_call([sys.executable, str(ROOT / "tools" / "render_site.py")])
    subprocess.check_call([sys.executable, str(ROOT / "tools" / "build_assets.py")])


if __name__ == "__main__":
    main()
