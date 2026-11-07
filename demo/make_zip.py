"""Zip demo/loja into demo/loja.zip (cross-platform; run with `npm run demo:zip`)."""

import zipfile
from pathlib import Path

DEMO = Path(__file__).resolve().parent
SOURCE = DEMO / "loja"
TARGET = DEMO / "loja.zip"
SKIP = {"node_modules", "dist", ".DS_Store"}


def main() -> None:
    files = sorted(
        path
        for path in SOURCE.rglob("*")
        if path.is_file() and not SKIP.intersection(path.relative_to(SOURCE).parts)
    )
    with zipfile.ZipFile(TARGET, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, Path("loja") / path.relative_to(SOURCE))
    print(f"{TARGET.relative_to(DEMO.parent)}: {len(files)} arquivos")


if __name__ == "__main__":
    main()
