"""Page geometry, colours, fonts and the style sheet of the Wispers 0.8 layout (A4, two columns)."""
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

MM = 72 / 25.4
PAGE_W, PAGE_H = 210 * MM, 297 * MM
TOP, BOTTOM, INSIDE, OUTSIDE = 18 * MM, 20 * MM, 18 * MM, 18 * MM
BLEED = 3 * MM
GUTTER = 6 * MM
TEXT_W = PAGE_W - INSIDE - OUTSIDE
TEXT_H = PAGE_H - TOP - BOTTOM
COLUMN_W = (TEXT_W - GUTTER) / 2

BODY, DISPLAY = "Cambria", "Monotype Corsiva"
EN_SPACE = "\u2002"
RED, GREY, PARCHMENT, RULE = "Color/WispersVoros", "Color/Sotetszurke", "Color/Pergamen", "Color/Vonal"

COLORS = {
    "WispersVoros": ("Wispers vörös", (122, 24, 20)),
    "Sotetszurke": ("Sötétszürke", (72, 64, 56)),
    "Pergamen": ("Pergamen", (244, 237, 224)),
    "Vonal": ("Táblázatvonal", (176, 156, 136)),
}

FONT_FILES = {
    (BODY, "Regular"): ("cambria.ttc", "Cambria"),
    (BODY, "Bold"): ("cambriab.ttf", "Cambria-Bold"),
    (BODY, "Italic"): ("cambriai.ttf", "Cambria-Italic"),
    (BODY, "Bold Italic"): ("cambriaz.ttf", "Cambria-BoldItalic"),
    (DISPLAY, "Regular"): ("MTCORSVA.TTF", "MonotypeCorsiva"),
}

BASE = dict(font=BODY, style="Regular", size=9.5, leading=12.5, align="LeftJustified", color="Color/Black",
            hyphenate=True, space_before=0, space_after=0, left=0, right=0, first=0, keep_next=0,
            keep_together=False, caps="Normal", rule_below=None, bullet=None)

CELL_PAD_X, CELL_PAD_Y = 2.5, 1.2
TABLE_TEXT = dict(size=8, leading=9.6, align="LeftAlign", hyphenate=False, left=CELL_PAD_X, right=CELL_PAD_X,
                  space_before=CELL_PAD_Y, space_after=CELL_PAD_Y)
TABLE_SMALL = dict(size=7, leading=8.4)
HEAD = dict(style="Bold", color="Color/Paper")
ALIGN = {"left": "LeftAlign", "center": "CenterAlign", "right": "RightAlign"}
ALIGN_SUFFIX = {"left": "", "center": "Kozep", "right": "Jobb"}
ALIGN_NAME = {"left": "", "center": " (középre)", "right": " (jobbra)"}


def table_styles():
    """Header and body cell styles for every alignment, in normal and small size."""
    styles = []
    for small, key_size, name_size in ((False, "", ""), (True, "Kicsi", ", kicsi")):
        for align in ("left", "center", "right"):
            for head, key_kind, name_kind in ((True, "TablaFej", "Táblázat: fejléc"), (False, "TablaSzoveg", "Táblázat: szöveg")):
                spec = dict(TABLE_TEXT, align=ALIGN[align], **(HEAD if head else {}), **(TABLE_SMALL if small else {}))
                key = key_kind + ALIGN_SUFFIX[align] + key_size
                styles.append((key, name_kind + name_size + ALIGN_NAME[align], "Alap", spec))
    return styles


PARAGRAPH_STYLES = [
    ("Alap", "Alap", None, {}),
    ("Torzs", "Törzsszöveg", "Alap", dict(space_after=4)),
    ("Felsorolas", "Felsorolás", "Torzs", dict(space_after=2, bullet="•")),
    ("Felsorolas2", "Felsorolás 2", "Felsorolas", dict(bullet="–")),
    ("Megjegyzes", "Szerkesztői megjegyzés", "Alap", dict(style="Italic", size=8.5, leading=11, color=GREY, left=8,
                                                           right=8, space_before=3, space_after=6, align="LeftAlign")),
    ("Cimlap", "Címlap: cím", "Alap", dict(font=DISPLAY, size=84, leading=90, color=RED, align="CenterAlign",
                                          space_after=26, hyphenate=False)),
    ("CimlapAlcim", "Címlap: alcím", "Alap", dict(size=14, leading=18, caps="SmallCaps", color=GREY,
                                                 align="CenterAlign", hyphenate=False)),
    ("CimlapInfo", "Címlap: megjegyzés", "Torzs", dict(size=8.5, leading=11, color=GREY)),
    ("Resz", "Rész", "Alap", dict(font=DISPLAY, size=52, leading=58, color=RED, align="CenterAlign",
                                 space_after=4, hyphenate=False)),
    ("ReszAlcim", "Rész: alcím", "Alap", dict(font=DISPLAY, size=28, leading=34, color=GREY, align="CenterAlign",
                                             hyphenate=False)),
    ("Fejezet", "Fejezetcím", "Alap", dict(font=DISPLAY, size=32, leading=36, color=RED, align="LeftAlign",
                                          rule_below=(1.0, RED, 7), hyphenate=False)),
    ("Cimsor1", "Címsor 1", "Alap", dict(font=DISPLAY, size=20, leading=23, color=RED, align="LeftAlign",
                                        space_before=12, space_after=5, keep_next=2, keep_together=True,
                                        rule_below=(0.5, RED, 3), hyphenate=False)),
    ("Cimsor2", "Címsor 2", "Alap", dict(font=DISPLAY, size=15.5, leading=18, color=RED, align="LeftAlign",
                                        space_before=9, space_after=3, keep_next=2, keep_together=True,
                                        hyphenate=False)),
    ("Cimsor3", "Címsor 3", "Alap", dict(style="Bold", size=10, leading=12.5, color=RED, align="LeftAlign",
                                        space_before=7, space_after=2, keep_next=2, keep_together=True,
                                        hyphenate=False)),
    ("Cimsor4", "Címsor 4", "Alap", dict(style="Bold Italic", size=9.5, leading=12, align="LeftAlign",
                                        space_before=6, space_after=3, keep_next=2, keep_together=True,
                                        hyphenate=False)),
    ("Tablazat", "Táblázat", "Alap", dict(space_before=3, space_after=9, align="LeftAlign", hyphenate=False)),
    ("Oldalszam", "Oldalszám", "Alap", dict(size=8, leading=10, align="LeftAlign", color=GREY, hyphenate=False)),
    ("OldalszamJobb", "Oldalszám (jobbra)", "Oldalszam", dict(align="RightAlign")),
] + table_styles()

CHARACTER_STYLES = [
    ("Felkover", "Félkövér", dict(FontStyle="Bold")),
    ("Dolt", "Dőlt", dict(FontStyle="Italic")),
    ("Felso", "Felső index", dict(Position="Superscript")),
]


def resolved_styles():
    """Every paragraph style with its full, inherited attribute set; bullets get a hanging indent."""
    resolved = {}
    for key, name, based_on, overrides in PARAGRAPH_STYLES:
        parent = resolved[based_on]["spec"] if based_on else BASE
        spec = dict(parent, **overrides)
        if "bullet" in overrides:
            marker = text_width(bullet_prefix(spec["bullet"]), spec["font"], spec["style"], spec["size"])
            spec["left"] = parent["left"] + marker
            spec["first"] = -marker
        resolved[key] = dict(name=name, based_on=based_on, spec=spec)
    return resolved


def bullet_prefix(marker):
    return marker + EN_SPACE


_registered = set()


def font_name(family, style):
    file_name, ps_name = FONT_FILES[(family, style)]
    if ps_name not in _registered:
        path = f"C:/Windows/Fonts/{file_name}"
        font = TTFont(ps_name, path, subfontIndex=0) if file_name.endswith(".ttc") else TTFont(ps_name, path)
        pdfmetrics.registerFont(font)
        _registered.add(ps_name)
    return ps_name


def text_width(text, family, style, size):
    return pdfmetrics.stringWidth(text, font_name(family, style), size)
