import json
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, List

from consulting.data_processing import sanitize_filename, read_json
from consulting.reporting import build_markdown

 


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python report_generator.py <input.json> [<output.md>]", file=sys.stderr)
        sys.exit(2)

    input_path = Path(sys.argv[1])
    output_path: Path | None = None
    if len(sys.argv) >= 3:
        output_path = Path(sys.argv[2])

    if not input_path.exists():
        print(f"Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    try:
        data = read_json(input_path)
    except (OSError, json.JSONDecodeError, ValueError) as e:
        print(f"Failed to read/parse JSON: {e}", file=sys.stderr)
        sys.exit(1)

    # Determine output filename
    if output_path is None:
        base = sanitize_filename(str(data.get("business_name") or input_path.stem))
        output_path = input_path.with_name(f"{base}_consulting_report.md")

    md = build_markdown(data)

    try:
        with output_path.open("w", encoding="utf-8") as f:
            f.write(md)
    except OSError as e:
        print(f"Failed to write markdown file '{output_path}': {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Report written to: {output_path.resolve()}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
