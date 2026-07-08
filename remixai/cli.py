import argparse
import sys
from pathlib import Path
from .pipeline import run_pipeline
from .engine import THEMES


def main():
    parser = argparse.ArgumentParser(
        prog="remixai",
        description="RemixAI - Automatic music video generator for YouTube Shorts",
    )
    parser.add_argument("input", help="Input audio file path")
    parser.add_argument(
        "-t", "--theme",
        choices=THEMES,
        default="original",
        help=f"Remix theme ({', '.join(THEMES)})",
    )
    parser.add_argument(
        "-o", "--output",
        default="output",
        help="Output directory (default: output)",
    )
    parser.add_argument(
        "-d", "--duration",
        type=int,
        default=30,
        help="Short video duration in seconds (default: 30)",
    )
    parser.add_argument(
        "--list-themes",
        action="store_true",
        help="List available themes and exit",
    )

    args = parser.parse_args()

    if args.list_themes:
        print("Available themes:")
        for t in THEMES:
            print(f"  - {t}")
        sys.exit(0)

    if not Path(args.input).exists():
        print(f"Error: file not found: {args.input}")
        sys.exit(1)

    run_pipeline(args.input, args.theme, args.output, args.duration)


if __name__ == "__main__":
    main()
