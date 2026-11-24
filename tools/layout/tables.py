"""Choose each table's text size and column widths for the width it gets."""
from dataclasses import dataclass

from design import BODY, CELL_PAD_X, text_width
from source import plain

SOFT_HYPHEN = "\u00ad"
HEADER_BREAKS = {
    "Fegyverkocka": "Fegyver|kocka", "Fegyvercsoport": "Fegyver|csoport", "Páncélcsoport": "Páncél|csoport",
    "Reflexgátlás": "Reflex|gátlás", "Védőérték": "Védő|érték", "Keménység": "Kemény|ség",
    "Tapasztalt": "Tapasz|talt", "Képzetlen": "Képzet|len", "Jellemzők": "Jellem|zők",
}


@dataclass
class TablePlan:
    rows: list
    widths: list
    small: bool
    fits: bool


def with_header_breaks(rows):
    def soften(cell):
        return " ".join(HEADER_BREAKS.get(w, w).replace("|", SOFT_HYPHEN) for w in cell.split(" "))
    return [[soften(c) for c in rows[0]]] + rows[1:]


def unbreakable_width(text, style, size):
    widest = 0.0
    for word in text.split() or [""]:
        parts = word.split(SOFT_HYPHEN)
        hyphen = text_width("-", BODY, style, size) if len(parts) > 1 else 0.0
        widest = max(widest, max(text_width(p, BODY, style, size) for p in parts) + hyphen)
    return widest


def natural_widths(rows, size):
    count = len(rows[0])
    mins, wants = [0.0] * count, [0.0] * count
    for r, row in enumerate(rows):
        style = "Bold" if r == 0 else "Regular"
        for c, cell in enumerate(row):
            text = plain(cell)
            mins[c] = max(mins[c], unbreakable_width(text, style, size) + 2 * CELL_PAD_X)
            wants[c] = max(wants[c], text_width(text.replace(SOFT_HYPHEN, ""), BODY, style, size) + 2 * CELL_PAD_X)
    return mins, wants


def mirrored_halves(rows, mins, wants):
    """Tables whose header repeats (1d100 | X | 1d100 | X) get equal widths on both halves."""
    header, half = rows[0], len(rows[0]) // 2
    if len(header) % 2 or header[:half] != header[half:]:
        return mins, wants
    mins = [max(mins[i % half], mins[i % half + half]) for i in range(len(mins))]
    wants = [max(wants[i % half], wants[i % half + half]) for i in range(len(wants))]
    return mins, wants


def distribute(mins, wants, avail):
    """Narrow columns get their natural width first; the rest share what is left by need."""
    if sum(wants) <= avail:
        spare = avail - sum(wants)
        return [w + spare * w / sum(wants) for w in wants]
    widths = list(mins)
    for i in sorted(range(len(wants)), key=lambda i: wants[i]):
        if wants[i] <= avail * 0.22 and sum(widths) - widths[i] + wants[i] <= avail:
            widths[i] = wants[i]
    hungry = [i for i in range(len(wants)) if widths[i] < wants[i]]
    spare = avail - sum(widths)
    need = sum(wants[i] - widths[i] for i in hungry)
    for i in hungry:
        widths[i] += spare * (wants[i] - widths[i]) / need
    return widths


def plan_table(rows, avail):
    candidates = [(rows, 8), (with_header_breaks(rows), 8), (with_header_breaks(rows), 7)]
    for cand_rows, size in candidates:
        mins, wants = mirrored_halves(cand_rows, *natural_widths(cand_rows, size))
        if sum(mins) <= avail:
            return TablePlan(cand_rows, distribute(mins, wants, avail), size == 7, True)
    cand_rows, size = candidates[-1]
    mins, _ = natural_widths(cand_rows, size)
    return TablePlan(cand_rows, [m * avail / sum(mins) for m in mins], True, False)
