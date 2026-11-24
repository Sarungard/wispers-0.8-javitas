"""Split the book into stories and lay them out on pages: title, part pages, one story per chapter."""
from dataclasses import dataclass, field

from design import BOTTOM, COLUMN_W, INSIDE, PAGE_H, PAGE_W, TEXT_H, TEXT_W, TOP, resolved_styles
from paginate import TABLE_EXTRA, display_text, flow, items_for, line_count, row_heights
from source import Block
from tables import TablePlan, plan_table

STYLES = resolved_styles()
HEADING_GAP = 12
TALL_TABLE = TEXT_H * 0.9
# Checked in Affinity: a chapter that spills under 5 % of a page onto its last page fits one page shorter.
TRIM_FILL = 0.05


@dataclass
class Story:
    id: str
    blocks: list
    columns: int = 1
    plans: dict = field(default_factory=dict)

    @property
    def column_width(self):
        return COLUMN_W if self.columns == 2 else TEXT_W


@dataclass
class Frame:
    story: str
    box: tuple
    columns: int


@dataclass
class Page:
    master: str
    frames: list = field(default_factory=list)
    label: str = ""


def row_chunks(heights, limit):
    """Split body rows (index 1..) into runs whose height with the header stays under the limit."""
    chunks, current, used = [], [], heights[0] + TABLE_EXTRA
    for r in range(1, len(heights)):
        if current and used + heights[r] > limit:
            chunks.append(current)
            current, used = [], heights[0] + TABLE_EXTRA
        current.append(r)
        used += heights[r]
    return chunks + [current]


def split_table(block, plan):
    """A table taller than a column becomes several tables, each with the header row."""
    chunks = row_chunks(row_heights(block, plan), TALL_TABLE)
    parts = []
    for rows in chunks:
        part_rows = [plan.rows[0]] + [plan.rows[r] for r in rows]
        part_block = Block("table", block.style, line=block.line, rows=part_rows, aligns=block.aligns)
        parts.append((part_block, TablePlan(part_rows, plan.widths, plan.small, plan.fits)))
    return parts


def plan_tables(story):
    blocks, plans = [], {}
    for block in story.blocks:
        if block.kind != "table":
            blocks.append(block)
            continue
        for part_block, part_plan in split_table(block, plan_table(block.rows, story.column_width)):
            plans[len(blocks)] = part_plan
            blocks.append(part_block)
    story.blocks, story.plans = blocks, plans
    return story


def table_too_wide(block):
    return block.kind == "table" and not plan_table(block.rows, COLUMN_W).fits


def split_wide_section(body):
    """From the first H2 section holding a table too wide for a column, the rest goes full width."""
    section_start = None
    for i, block in enumerate(body):
        if block.style == "Cimsor1":
            section_start = i
        if table_too_wide(block):
            cut = section_start if section_start is not None else i
            return body[:cut], body[cut:]
    return body, []


def sections(blocks):
    """[('title', [...]), ('part', [...]), ('chapter', heading, body), ...]"""
    out, i = [], 0
    title = []
    while i < len(blocks) and blocks[i].style != "Resz":
        title.append(blocks[i])
        i += 1
    out.append(("title", title))
    while i < len(blocks):
        block = blocks[i]
        if block.style == "Resz":
            part = [block]
            if i + 1 < len(blocks) and blocks[i + 1].style == "ReszAlcim":
                part.append(blocks[i + 1])
                i += 1
            out.append(("part", part))
            i += 1
            continue
        body = []
        j = i + 1
        while j < len(blocks) and blocks[j].style not in ("Resz", "Fejezet"):
            body.append(blocks[j])
            j += 1
        out.append(("chapter", block, body))
        i = j
    return out


def text_box(top, bottom):
    return INSIDE, top, PAGE_W - INSIDE, bottom


def block_height(blocks, width):
    total = 0.0
    for block in blocks:
        spec = STYLES[block.style]["spec"]
        total += spec["space_before"] + line_count(display_text(block), spec, width) * spec["leading"] + spec[
            "space_after"]
    return total


def body_pages(story, first_height):
    items = items_for(story.blocks, story.plans, story.column_width)
    result = flow(items, story.columns, first_height, TEXT_H)
    if result.near_miss:
        return result.pages + 1, result
    if result.pages > 1 and result.last_fill < TRIM_FILL:
        return result.pages - 1, result
    return result.pages, result


class Book:
    def __init__(self):
        self.stories, self.pages, self.report = {}, [], []

    def add_story(self, story):
        self.stories[story.id] = plan_tables(story)
        return story

    def title_page(self, blocks):
        heading = [b for b in blocks if b.style in ("Cimlap", "CimlapAlcim")]
        info = [b for b in blocks if b not in heading]
        for b in info:
            b.style = "CimlapInfo"
        page = Page("uMasterB", label="címlap")
        title = self.add_story(Story("uStCim", heading))
        top = PAGE_H * 0.30
        page.frames.append(Frame(title.id, text_box(top, top + block_height(heading, TEXT_W) + 20), 1))
        if info:
            story = self.add_story(Story("uStCimInfo", info))
            height = block_height(info, TEXT_W) + 10
            page.frames.append(Frame(story.id, text_box(PAGE_H - BOTTOM - height, PAGE_H - BOTTOM), 1))
        self.pages.append(page)

    def part_page(self, n, blocks):
        story = self.add_story(Story(f"uStResz{n}", blocks))
        height = block_height(blocks, TEXT_W) + 20
        top = PAGE_H * 0.42 - height / 2
        self.pages.append(Page("uMasterB", [Frame(story.id, text_box(top, top + height), 1)], blocks[0].text))

    def body_story(self, story_id, blocks, columns, first_page_frames, first_top, label):
        story = self.add_story(Story(story_id, blocks, columns))
        count, result = body_pages(story, PAGE_H - BOTTOM - first_top)
        for p in range(count):
            top = first_top if p == 0 else TOP
            frames = (first_page_frames if p == 0 else []) + [Frame(story.id, text_box(top, PAGE_H - BOTTOM), columns)]
            self.pages.append(Page("uMasterA", frames, label if p == 0 else ""))
        self.report.append((label, columns, count, result))

    def chapter(self, n, heading, body):
        head = self.add_story(Story(f"uStFejezet{n}", [heading]))
        head_height = block_height([heading], TEXT_W) + 10
        head_frame = Frame(head.id, text_box(TOP, TOP + head_height), 1)
        narrow, wide = split_wide_section(body)
        first_top = TOP + head_height + HEADING_GAP
        if narrow:
            self.body_story(f"uStTorzs{n}", narrow, 2, [head_frame], first_top, heading.text)
        if wide:
            frames, top = ([], TOP) if narrow else ([head_frame], first_top)
            self.body_story(f"uStTorzs{n}b", wide, 1, frames, top, heading.text + " (teljes szélesség)")


def build_book(blocks):
    book = Book()
    for n, section in enumerate(sections(blocks)):
        kind = section[0]
        if kind == "title":
            book.title_page(section[1])
        elif kind == "part":
            book.part_page(n, section[1])
        else:
            book.chapter(n, section[1], section[2])
    return book
