import argparse
from io import TextIOWrapper
from operator import attrgetter
from pathlib import Path
import subprocess
from . import chords
import re


def insert_after_pattern(song: str, text: str, pattern: re.Pattern) -> str:
    """Insert `text` after the first occurence of `pattern` in `song`."""
    match = pattern.search(song)
    assert match
    return "\n".join((
        song[:match.end()],
        text,
        song[match.end():],
    ))


def make_song_list(songdir: Path):
    """Print a Latex `\\input` command for each song in the given `songdir`."""
    assert songdir.is_dir()
    for i in sorted(songdir.iterdir(), key=attrgetter("name")):
        if i.suffix == ".tex":
            print(f"\\input{{{i}}}")


def make_chords(instrument_file: TextIOWrapper):
    """Print a Latex command that shows finger positions for each chord in `instrument_file`."""
    all_chords = chords.parse_chord_data(instrument_file)
    for chord, finger_positions in all_chords.items():
        print(chord.to_latex(finger_positions))


def make_buildinfo():
    """Print a Latex command with the current date and repo state."""
    git_hash = subprocess.check_output(["git", "describe", "--always", "--dirty", "--abbrev"]).strip().decode()
    print("\\date{compilé le \\today{} -- commit \\texttt{" + git_hash + "}}")


def insert_chords(song: TextIOWrapper, chords_per_line: int):
    """Detect chords in a song and insert commands to print their finger positions under the title."""
    song_tex = song.read()
    found_chords = chords.find_chords(song_tex)
    print(
        insert_after_pattern(
            song_tex,
            text=chords.generate_latex_chords(
                chords=found_chords,
                chords_per_line=chords_per_line,
            ),
            pattern=re.compile(r"\\beginsong.*+\n", re.M),
        )
    )


def get_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the songbook tools."""
    psr = argparse.ArgumentParser("songbook_tools")
    spsrs = psr.add_subparsers(required=True)
    songlist_psr = spsrs.add_parser("makesonglist", help=make_song_list.__doc__)
    songlist_psr.set_defaults(action=make_song_list)
    songlist_psr.add_argument("songdir", type=Path, help="Where the .tex files are located")

    makechords_psr = spsrs.add_parser("makechords", help=make_chords.__doc__)
    makechords_psr.set_defaults(action=make_chords)
    makechords_psr.add_argument("instrument_file", type=argparse.FileType("r"), help="An ini file with chords & finger positions")

    insertchords_psr = spsrs.add_parser("insertchords", help=insert_chords.__doc__)
    insertchords_psr.add_argument("song", type=argparse.FileType("r"), help="The song file to insert chords into (not modified)")
    insertchords_psr.add_argument("-n", "--chords-per-line", default=6, type=int, help="The number of chords to print per line")
    insertchords_psr.set_defaults(action=insert_chords)

    makebuildinfo_psr = spsrs.add_parser("makebuildinfo", help=make_buildinfo.__doc__)
    makebuildinfo_psr.set_defaults(action=make_buildinfo)
    return psr


def main():
    args_dict = get_parser().parse_args().__dict__
    func = args_dict.pop("action")
    func(**args_dict)


if __name__ == "__main__":
    main()
