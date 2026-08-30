#!/usr/bin/env python3
"""Create and compare deterministic result-archive inventories."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def csv_shape(path: Path) -> tuple[int | None, int | None, str | None]:
    if path.suffix.lower() != ".csv":
        return None, None, None
    with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        reader = csv.reader(handle)
        try:
            header = next(reader)
        except StopIteration:
            return 0, 0, ""
        rows = sum(1 for _ in reader)
    return len(header), rows, "|".join(header)


def inventory(root: Path) -> list[dict[str, object]]:
    rows = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        if path.name in {"ARCHIVE_MANIFEST.json", "ARCHIVE_MANIFEST.csv"}:
            continue
        columns, csv_rows, header = csv_shape(path)
        rows.append(
            {
                "path": path.relative_to(root).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "csv_columns": columns,
                "csv_rows": csv_rows,
                "csv_header": header,
            }
        )
    return rows


def write_inventory(root: Path, output: Path) -> None:
    rows = inventory(root)
    payload = {
        "root": str(root.resolve()),
        "file_count": len(rows),
        "total_bytes": sum(int(row["bytes"]) for row in rows),
        "aggregate_csv_rows": sum(int(row["csv_rows"] or 0) for row in rows),
        "files": rows,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    csv_output = output.with_suffix(".csv")
    with csv_output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else ["path"])
        writer.writeheader()
        writer.writerows(rows)


def comparable(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        "file_count": data["file_count"],
        "total_bytes": data["total_bytes"],
        "aggregate_csv_rows": data["aggregate_csv_rows"],
        "files": data["files"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    create = subparsers.add_parser("create")
    create.add_argument("root", type=Path)
    create.add_argument("output", type=Path)
    compare = subparsers.add_parser("compare")
    compare.add_argument("source", type=Path)
    compare.add_argument("destination", type=Path)
    args = parser.parse_args()
    if args.command == "create":
        write_inventory(args.root, args.output)
    else:
        if comparable(args.source) != comparable(args.destination):
            raise SystemExit("archive manifests differ")
        print("VERIFIED")


if __name__ == "__main__":
    main()
