import argparse
from .engine import run_diff

def parse_args():
    parser = argparse.ArgumentParser(description="Diffinity: the divine art of config comparison.")
    parser.add_argument("dir1", help="First directory")
    parser.add_argument("dir2", help="Second directory")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--includelist", nargs="+", help="Relative file paths to compare")
    group.add_argument("--includepatterns", nargs="+", help="Suffix patterns combined with each directory basename to locate files")

    parser.add_argument("--output", help="Output file (.txt or .html)")
    parser.add_argument("--style", choices=["sidebyside", "compact", "verbose"], default="sidebyside", help="Output verbosity")
    parser.add_argument("--ignore-paths", action="store_true", help="Ignore filesystem paths in file contents")

    return parser.parse_args()

def main():
    args = parse_args()
    run_diff(args.dir1, args.dir2, args.includelist, args.output, args.style, args.ignore_paths, args.includepatterns)