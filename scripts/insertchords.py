import re
import argparse
import itertools
from .chords import Chord


CHORD_RE = re.compile(r"\\\[([\w\d]+)\]")
BEGINSONG_LINE = re.compile(r"\\beginsong.*+\n", re.M)


def parse_chords(tex: str) -> list[Chord]:
    found = []
    for chord_match in CHORD_RE.finditer(tex):
        if (chord := Chord.parse(chord_match[1])) not in found:
            found.append(chord)
    return found


def generate_latex_chords(chords: list[Chord], chords_per_line: int = 5) -> str:
    lines = []
    for chord_batch in itertools.batched(chords, n=chords_per_line):
        for chord in chord_batch:
            lines.append(chord.latex_command)
        lines.append("\\newline")
    lines.pop()
    return "\n".join(lines)


def insert_after_pattern(song: str, text: str, pattern: re.Pattern = BEGINSONG_LINE) -> str:
    match = pattern.search(song)
    return "\n".join((
        song[:match.end()],
        text,
        song[match.end():],
    ))


def main():
    psr = argparse.ArgumentParser()
    psr.add_argument("song", type=argparse.FileType("r"))
    psr.add_argument("-n", "--chords-per-line", default=5, type=int)
    args = psr.parse_args()
    song_tex = args.song.read()
    chords = parse_chords(song_tex)
    print(
        insert_after_pattern(
            song_tex,
            text=generate_latex_chords(
                chords=chords,
                chords_per_line=args.chords_per_line,
            )
        )
    )


if __name__ == "__main__":
    main()
