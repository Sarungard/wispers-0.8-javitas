"""Parse the 0.8 working text into layout blocks (headings, paragraphs, bullets, notes, tables)."""
import re
from dataclasses import dataclass, field
from pathlib import Path

RPG = Path(__file__).resolve().parents[2]
SOURCE = RPG / "homebrewery" / "wispers-0.8-javitott.txt"

PART_TITLES = {"Bevezetés", "I. rész", "II. rész", "III. rész"}
HEADING_STYLE = {2: "Cimsor1", 3: "Cimsor2", 4: "Cimsor3", 5: "Cimsor4"}
INLINE = re.compile(r"\*\*(.+?)\*\*|\*(.+?)\*|\^(.+?)\^")
INLINE_STYLE = ("Felkover", "Dolt", "Felso")


@dataclass
class Block:
    kind: str
    style: str
    text: str = ""
    line: int = 0
    rows: list = field(default_factory=list)
    aligns: list = field(default_factory=list)


def runs(text):
    """Split inline Markdown (**bold**, *italic*, ^superscript^) into (character style or None, text) pairs."""
    out, pos = [], 0
    for m in INLINE.finditer(text):
        if m.start() > pos:
            out.append((None, text[pos:m.start()]))
        group = next(g for g in range(1, 4) if m.group(g) is not None)
        out.append((INLINE_STYLE[group - 1], m.group(group)))
        pos = m.end()
    if pos < len(text):
        out.append((None, text[pos:]))
    return out


def plain(text):
    return "".join(chunk for _, chunk in runs(text))


def split_row(line):
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_rule_row(cells):
    return all(re.fullmatch(r":?-+:?", c) for c in cells)


def alignment(rule):
    if rule.startswith(":") and rule.endswith(":"):
        return "center"
    return "right" if rule.endswith(":") else "left"


def table_block(lines, line_no):
    rows = [split_row(l) for l in lines]
    aligns = [alignment(c) for c in rows[1]] if len(rows) > 1 and is_rule_row(rows[1]) else ["left"] * len(rows[0])
    body = [rows[0]] + [r for r in rows[1:] if not is_rule_row(r)]
    width = max(len(r) for r in body)
    body = [r + [""] * (width - len(r)) for r in body]
    aligns = aligns + ["left"] * (width - len(aligns))
    return Block("table", "Tablazat", line=line_no, rows=body, aligns=aligns)


def heading_block(level, text, blocks, line_no):
    previous = blocks[-1].style if blocks else None
    if level == 1 and not blocks:
        style = "Cimlap"
    elif level == 2 and previous == "Cimlap":
        style = "CimlapAlcim"
    elif level == 1 and text in PART_TITLES:
        style = "Resz"
    elif level == 2 and previous == "Resz":
        style = "ReszAlcim"
    elif level == 1:
        style = "Fejezet"
    else:
        style = HEADING_STYLE[level]
    return Block("heading", style, text, line_no)


def first_heading(lines):
    return next(i for i, l in enumerate(lines) if l.startswith("# "))


def parse(text):
    lines = text.split("\n")
    i = first_heading(lines)
    blocks = []
    while i < len(lines):
        line, line_no = lines[i], i + 1
        if not line.strip():
            i += 1
            continue
        if line.startswith("|"):
            j = i
            while j < len(lines) and lines[j].startswith("|"):
                j += 1
            blocks.append(table_block(lines[i:j], line_no))
            i = j
            continue
        heading = re.match(r"(#{1,5}) (.*)", line)
        bullet = re.match(r"( *)- (.*)", line)
        if heading:
            blocks.append(heading_block(len(heading.group(1)), heading.group(2).strip(), blocks, line_no))
        elif bullet:
            style = "Felsorolas2" if len(bullet.group(1)) >= 2 else "Felsorolas"
            blocks.append(Block("bullet", style, bullet.group(2).strip(), line_no))
        elif re.fullmatch(r"\[.*\]", line.strip()):
            blocks.append(Block("para", "Megjegyzes", line.strip()[1:-1], line_no))
        else:
            blocks.append(Block("para", "Torzs", line.strip(), line_no))
        i += 1
    return blocks


def load():
    return parse(SOURCE.read_text(encoding="utf-8"))
