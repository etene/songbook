import io
import itertools
import re

from configparser import ConfigParser
from enum import StrEnum, auto
from typing import NamedTuple


# TODO: handle non memorized chords (like \[^A])
CHORD_RE = re.compile(r"\\\[([\w\d#]+)\]")


class NoteName(StrEnum):
    A_BEMOL = "Ab"
    A = "A"
    A_SHARP = "A#"
    B_BEMOL = "Bb"
    B = "B"
    C = "C"
    C_SHARP = "C#"
    D_BEMOL = "Db"
    D = "D"
    D_SHARP = "D#"
    E_BEMOL = "Eb"
    E = "E"
    E_SHARP = "E#"
    F_BEMOL = "Fb"
    F = "F"
    F_SHARP = "F#"
    G_BEMOL = "Gb"
    G = "G"
    G_SHARP = "G#"


note_aliases: dict[NoteName, NoteName] = {
    NoteName.G_SHARP: NoteName.A_BEMOL,
    NoteName.A_SHARP: NoteName.B_BEMOL,
    NoteName.C_SHARP: NoteName.D_BEMOL,
    NoteName.D_SHARP: NoteName.E_BEMOL,
    NoteName.E_SHARP: NoteName.F_BEMOL,
    NoteName.F_SHARP: NoteName.G_BEMOL,
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
    suspended = auto()
    sus = suspended


CHORD_PATTERN: re.Pattern = re.compile(
    r"(?P<root_note>[A-G][\#b]?)(?P<short_type>[a-z]*)(?P<add>\d*)"
)


class Chord(NamedTuple):
    root: NoteName
    type: NoteType | None = None
    add: int | None = None

    @classmethod
    def parse(cls, shortname: str) -> 'Chord':
        """Parse from a short chord name like F or D7 or Am7."""
        if match := CHORD_PATTERN.match(shortname):
            return cls(
                root=NoteName(match["root_note"]),
                type=NoteType[raw_note_type] if (raw_note_type := match["short_type"]) else None,
                add=int(raw_add) if (raw_add := match["add"]) else None
            )
        raise ValueError(f"Cannot parse note {shortname!r}")

    def __str__(self) -> str:
        if self.type is None or (self.type is NoteType.major and self.add is None):
            type_ = ""
        elif self.type is NoteType.minor:
            type_ = "m"
        else:
            type_ = self.type[:3]
        add = str(self.add) if self.add else ""
        return f"{self.root}{type_}{add}"

    def to_latex(self, finger_positions: list[int]) -> str:
        """The definition of the latex command used to print the finger position pattern for this chord."""
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
        """The latex command used to print the finger position pattern for this chord."""
        def replace_numbers(match: re.Match) -> str:
            return {
                "4": "fourth",
                "7": "seven",
                "9": "nine",
                "11": "eleven",
                "13": "thirteen",
            }[match.group(0)]
        return "\\print" + re.sub(r"\d+", replace_numbers, str(self).replace("#", "sharp"))


def parse_chord_data(data: io.TextIOWrapper) -> dict[Chord, list[int]]:
    """Parse fingers positions for chords from a .ini file.

    Return a mapping of chords to finger positions.
    
    The file must have a section for each note and an entry for each chord.
    """
    parser = ConfigParser()
    parser.optionxform = str  # makes it case sensitive
    parser.read_file(data)
    parsed_chords: dict[Chord, list[int]] = {}
    seen_notes: set[NoteName] = set()
    for raw_note in parser.sections():
        note_name = NoteName(raw_note)
        if note_name in seen_notes:
            raise ValueError(f"Already seen a section for {note_name}")
        seen_notes.add(note_name)
        for chordname, finger_positions in parser[raw_note].items():
            chord = Chord.parse(note_name + chordname)
            finger_pos = list(map(int, finger_positions))
            parsed_chords[chord] = finger_pos
            if (alias := note_aliases.get(chord.root)):
                alt_chord = chord._replace(root=alias)
                parsed_chords[alt_chord] = finger_positions
    return parsed_chords


def find_chords(tex: str) -> list[Chord]:
    """Find unique chords mentioned in a song, in the order in which they appear."""
    found = []
    for chord_match in CHORD_RE.finditer(tex):
        if (chord := Chord.parse(chord_match[1])) not in found:
            found.append(chord)
    return found


def generate_latex_chords(chords: list[Chord], chords_per_line: int = 5) -> str:
    """Generate comands to print finger positions for the given chord list."""
    lines: list[str] = []
    for chord_batch in itertools.batched(chords, n=chords_per_line):
        lines.extend(i.latex_command for i in chord_batch)
        lines.append("\\newline")
    if lines:
        # Remove last newline
        lines.pop()
    return "\n".join(lines)
