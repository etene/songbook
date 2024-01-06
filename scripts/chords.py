import io
import re

from argparse import ArgumentParser, FileType
from configparser import ConfigParser
from enum import StrEnum, auto
from pathlib import Path
from typing import ClassVar, NamedTuple


class NoteName(StrEnum):
    A = "A"
    A_SHARP = "A#"
    B = "B"
    C = "C"
    C_SHARP = "C#"
    D = "D"
    D_SHARP = "D#"
    E = "E"
    E_SHARP = "E#"
    F = "F"
    F_SHARP = "F#"
    G = "G"
    G_SHARP = "G#"


note_aliases: dict[str, NoteName] = {
    "Ab": NoteName.G_SHARP,
    "Bb": NoteName.A_SHARP,
    "Db": NoteName.C_SHARP,
    "Eb": NoteName.D_SHARP,
    "Fb": NoteName.E_SHARP,
    "Gb": NoteName.F_SHARP,
}


class NoteType(StrEnum):
    major = auto()
    minor = auto()
    dominant = auto()
    diminished = auto()
    maj = major
    M = major
    m = min = minor
    dom = dominant
    dim = diminished


CHORD_PATTERN: re.Pattern = re.compile(
    r"(?P<root_note>[A-G]\#?)(?P<short_type>[a-z]*)(?P<add>\d*)"
)


class Chord(NamedTuple):
    root: NoteName
    type: NoteType = NoteType.major
    add: int | None = None

    @classmethod
    def parse(cls, shortname: str) -> 'Chord':
        if match := CHORD_PATTERN.match(shortname):
            raw_note = match["root_note"]
            raw_note_type = match["short_type"]
            raw_add = match["add"]
            return cls(
                root=NoteName(note_aliases.get(raw_note, raw_note)),
                type=NoteType[raw_note_type] if raw_note_type else NoteType.major,
                add=int(raw_add) if raw_add else None
            )
        raise ValueError(f"Cannot parse note {shortname!r}")

    def __str__(self) -> str:
        if self.type is NoteType.major:
            type_ = ""
        elif self.type is NoteType.minor:
            type_ = "m"
        else:
            type_ = self.type[:3]
        add = str(self.add) if self.add else ""
        return f"{self.root}{type_}{add}"

    def to_latex(self, finger_positions: list[int]) -> str:
        return (
            "\\newcommand{"
            + self.latex_command
            + "}{\\gtab{"
            + str(self).replace("#", r"\#")
            + "}{"
            + ''.join(map(str, finger_positions))
            + "}}"
        )

    @property
    def latex_command(self) -> str:
        def replace_numbers(match: re.Match) -> str:
            return {
                "7": "seven",
                "9": "nine",
                "11": "eleven",
                "13": "thirteen",
            }[match.group(0)]
        return "\\print" + re.sub(r"\d+", replace_numbers, str(self).replace("#", "sharp"))


def parse_chord_data(data: io.TextIOWrapper) -> dict[Chord, list[int]]:
    parser = ConfigParser()
    parser.optionxform = str  # makes it case sensitive
    parser.read_file(data)
    parsed_chords: dict[Chord, list[int]] = {}
    seen_notes: set[NoteName] = set()
    for raw_note in parser.sections():
        note_name = NoteName(note_aliases.get(raw_note, raw_note))
        if note_name in seen_notes:
            raise ValueError(f"Already seen a section for {note_name}")
        seen_notes.add(note_name)
        for chordname, finger_positions in parser[raw_note].items():
            parsed_chords[Chord.parse(note_name + chordname)] = list(map(int, finger_positions))
    return parsed_chords


def get_parser() -> ArgumentParser:
    psr = ArgumentParser()
    psr.add_argument("instrument", type=FileType("r"))
    return psr


def main():
    args = get_parser().parse_args()
    all_chords = parse_chord_data(args.instrument)
    for chord, finger_positions in all_chords.items():
        print(chord.to_latex(finger_positions))


if __name__ == "__main__":
    main()
