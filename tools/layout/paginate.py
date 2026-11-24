"""Estimate how many pages a story fills, with the same font metrics Affinity uses.

Like Affinity, the first line of a column sits on its ascent and space before is dropped at a column top.
The model still errs on the long side: greedy line breaks only at spaces, no kerning, a generous ascent,
tables never split.
"""
import math
from dataclasses import dataclass

from design import ALIGN_SUFFIX, BODY, bullet_prefix, resolved_styles, text_width
from source import runs
from tables import SOFT_HYPHEN

STYLES = resolved_styles()
RUN_FACE = {None: (False, False), "Felkover": (True, False), "Dolt": (False, True), "Felso": (False, False)}
TABLE_EXTRA = 4.0
ROW_SAFETY = 1.0
NEAR_MISS = 15.0
ASCENT, DESCENT = 0.95, 0.25


def face(paragraph_face, run_style):
    bold = "Bold" in paragraph_face or RUN_FACE[run_style][0]
    italic = "Italic" in paragraph_face or RUN_FACE[run_style][1]
    return {(False, False): "Regular", (True, False): "Bold", (False, True): "Italic", (True, True): "Bold Italic"}[
        (bold, italic)]


def styled_chars(text, spec):
    for run_style, chunk in runs(text):
        current = face(spec["style"], run_style) if spec["font"] == BODY else "Regular"
        for ch in chunk.replace(SOFT_HYPHEN, ""):
            yield ch, current


def word_widths(text, spec):
    """(word width, width of the space after it) for every space-separated word."""
    words, width, pending = [], 0.0, []
    for ch, current in styled_chars(text, spec):
        if ch == " ":
            words.append((width, text_width(" ", spec["font"], current, spec["size"])))
            width = 0.0
        else:
            width += text_width(ch, spec["font"], current, spec["size"])
    words.append((width, 0.0))
    return [w for w in words if w[0] > 0] or [(0.0, 0.0)]


def line_count(text, spec, width):
    first = width - spec["left"] - spec["first"] - spec["right"]
    rest = width - spec["left"] - spec["right"]
    lines, used, avail, space = 1, 0.0, first, 0.0
    for word, space_after in word_widths(text, spec):
        if used and used + space + word > avail:
            lines += 1
            avail, used = rest, 0.0
        if word > avail:
            lines += math.ceil(word / avail) - 1
            used = word % avail
        else:
            used = word if not used else used + space + word
        space = space_after
    return lines


def display_text(block):
    if block.kind == "bullet":
        return bullet_prefix(STYLES[block.style]["spec"]["bullet"]) + block.text
    return block.text


def cell_spec(header, align, small):
    key = ("TablaFej" if header else "TablaSzoveg") + ALIGN_SUFFIX[align] + ("Kicsi" if small else "")
    return STYLES[key]["spec"], key


def row_heights(block, plan):
    heights = []
    for r, row in enumerate(plan.rows):
        tallest = 0.0
        for c, cell in enumerate(row):
            spec, _ = cell_spec(r == 0, block.aligns[c], plan.small)
            lines = line_count(cell, spec, plan.widths[c]) if cell else 1
            tallest = max(tallest, lines * spec["leading"] + spec["space_before"] + spec["space_after"])
        heights.append(tallest + ROW_SAFETY)
    return heights


def table_height(block, plan):
    return TABLE_EXTRA + sum(row_heights(block, plan))


@dataclass
class Item:
    space_before: float
    lines: list
    space_after: float
    keep_next: int
    keep_together: bool
    solid: bool
    ascent: float = 0.0
    descent: float = 0.0


def items_for(blocks, plans, column_width):
    items = []
    for i, block in enumerate(blocks):
        spec = STYLES["Tablazat" if block.kind == "table" else block.style]["spec"]
        if block.kind == "table":
            height = table_height(block, plans[i])
            items.append(Item(spec["space_before"], [height], spec["space_after"], 0, True, True))
            continue
        count = line_count(display_text(block), spec, column_width)
        items.append(Item(spec["space_before"], [spec["leading"]] * count, spec["space_after"],
                          spec["keep_next"], spec["keep_together"], False,
                          ASCENT * spec["size"], DESCENT * spec["size"]))
    return items


@dataclass
class Flow:
    pages: int
    last_fill: float
    too_tall: list
    near_miss: list


class Columns:
    def __init__(self, columns, first_height, height):
        self.columns, self.first_height, self.height = columns, first_height, height
        self.page, self.col, self.y = 0, 0, 0.0

    @property
    def limit(self):
        return self.first_height if self.page == 0 else self.height

    def room(self):
        return self.limit - self.y

    def next_column(self):
        self.col += 1
        self.y = 0.0
        if self.col == self.columns:
            self.page += 1
            self.col = 0


def needed_with_next(item, following):
    need = item.space_before + sum(item.lines)
    if following is not None and item.keep_next:
        need += following.space_before + sum(following.lines[:item.keep_next])
    return need


def place_solid(cols, index, item, too_tall, near_miss):
    height = sum(item.lines)
    gap = item.space_before if cols.y > 0 else 0.0
    if cols.y > 0 and gap + height > cols.room():
        cols.next_column()
        gap = 0.0
    elif cols.y > 0 and cols.room() - gap - height < NEAR_MISS:
        near_miss.append(index)
    if height > cols.room():
        too_tall.append(index)
    cols.y += gap + height


def place_lines(cols, item):
    """cols.y follows the last baseline; a column-top line sits on its ascent, space before dropped."""
    for n, leading in enumerate(item.lines):
        step = item.ascent if cols.y == 0 else (item.space_before if n == 0 else 0.0) + leading
        if cols.y > 0 and cols.y + step + item.descent > cols.limit:
            cols.next_column()
            step = item.ascent
        cols.y += step


def flow(items, columns, first_height, height):
    cols = Columns(columns, first_height, height)
    too_tall, near_miss = [], []
    for i, item in enumerate(items):
        following = items[i + 1] if i + 1 < len(items) else None
        block_need = needed_with_next(item, following) if (item.keep_together or item.keep_next) else None
        if block_need is not None and cols.y > 0 and block_need > cols.room():
            cols.next_column()
        if item.solid:
            place_solid(cols, i, item, too_tall, near_miss)
        else:
            place_lines(cols, item)
        cols.y += item.space_after
    last_fill = (cols.col + min(cols.y, cols.limit) / cols.limit) / columns
    return Flow(cols.page + 1, last_fill, too_tall, near_miss)
