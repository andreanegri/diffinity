import argparse
from .engine import run_diff

def parse_args():
    parser = argparse.ArgumentParser(description="Diffinity: the divine art of config comparison.")
    parser.add_argument("dir1", help="Prima directory")
    parser.add_argument("dir2", help="Seconda directory")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--includelist", help="File con lista completa di path relativi da confrontare")
    group.add_argument("--includepatterns", help="File con lista di suffissi da combinare con il nome della dir")
    
    parser.add_argument("--output", help="File di output (.txt o .html)")
    parser.add_argument("--style", choices=["compact", "verbose"], default="compact", help="Stile di output CLI")
    parser.add_argument("--ignore-paths", action="store_true", help="Ignora i path nei contenuti dei file")

    return parser.parse_args()

def main():
    args = parse_args()
    run_diff(args.dir1, args.dir2, args.includelist, args.output, args.style, args.ignore_paths, args.includepatterns)