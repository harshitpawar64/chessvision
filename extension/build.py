import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT.parent / "dist"

EXCLUDED_PARTS = {"_metadata", "build.py"}


def build() -> None:
    DIST.mkdir(exist_ok=True)

    manifest_raw = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    version = manifest_raw["version"]

    static_files = [
        path
        for path in ROOT.rglob("*")
        if path.is_file() and path.name != "manifest.json" and not should_exclude(path)
    ]

    for target in ("chrome", "firefox"):
        zip_path = DIST / f"chessvision-{target}-v{version}.zip"
        manifest = manifest_raw.copy()

        if target == "firefox":
            manifest["background"] = {"scripts": ["src/background.js"]}

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("manifest.json", json.dumps(manifest, indent=2))
            for path in static_files:
                zf.write(path, path.relative_to(ROOT).as_posix())

        size_mb = zip_path.stat().st_size / (1024 * 1024)
        print(f"Packaged {zip_path.name} ({size_mb:.2f} MB)")


def should_exclude(path: Path) -> bool:
    return any(part.startswith(".") or part in EXCLUDED_PARTS for part in path.parts)


if __name__ == "__main__":
    build()
