from argparse import ArgumentParser
from operator import attrgetter
from pathlib import Path


def get_parser() -> ArgumentParser:
    psr = ArgumentParser()
    psr.add_argument("songdir", type=Path)
    return psr


def main():
    args = get_parser().parse_args()
    songdir: Path = args.songdir
    assert songdir.is_dir()
    for i in sorted(songdir.iterdir(), key=attrgetter("name")):
        if i.suffix == ".tex":
            print(f"\\input{{{i}}}")


if __name__ == "__main__":
    main()
