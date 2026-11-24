"""Write an IDML package (InDesign Markup Language) that Affinity Publisher opens with File › Open."""
import zipfile
from xml.sax.saxutils import escape, quoteattr

from design import (ALIGN_SUFFIX, BLEED, BODY, BOTTOM, CHARACTER_STYLES, COLORS, COLUMN_W, FONT_FILES, GUTTER,
                    INSIDE, OUTSIDE, PAGE_H, PAGE_W, PARCHMENT, RED, RULE, TEXT_W, TOP, resolved_styles)
from paginate import display_text, row_heights
from source import runs

PKG = 'xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="16.0"'
XML_HEAD = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
NO_CHAR = "CharacterStyle/$ID/[No character style]"
NO_PARA = "ParagraphStyle/$ID/[No paragraph style]"
LAYER = "uLayerSzoveg"
# IDML writes special characters as processing instructions; ACE 18 is the current page number.
PAGE_NUMBER = "<?ACE 18?>"
FOLIO_STORIES = {"left": "uStOldalszamBal", "right": "uStOldalszamJobb"}
MASTERS = {"uMasterA": ("A", "Alap", FOLIO_STORIES), "uMasterB": ("B", "Üres", {})}


def num(value):
    return f"{value:.4f}".rstrip("0").rstrip(".")


def attrs(mapping):
    return " ".join(f"{k}={quoteattr(str(v))}" for k, v in mapping.items())


def flag(value):
    return "true" if value else "false"


# ---------------------------------------------------------------- resources

def paragraph_style_xml(key, entry):
    s = entry["spec"]
    a = {
        "Self": f"ParagraphStyle/{key}", "Name": entry["name"], "Imported": "false",
        "NextStyle": f"ParagraphStyle/{key}", "KeyboardShortcut": "0 0",
        "FontStyle": s["style"], "PointSize": num(s["size"]), "FillColor": s["color"],
        "Justification": s["align"], "Hyphenation": flag(s["hyphenate"]),
        "SpaceBefore": num(s["space_before"]), "SpaceAfter": num(s["space_after"]),
        "LeftIndent": num(s["left"]), "RightIndent": num(s["right"]), "FirstLineIndent": num(s["first"]),
        "KeepWithNext": str(s["keep_next"]), "KeepLinesTogether": flag(s["keep_together"]),
        "KeepAllLinesTogether": flag(s["keep_together"]), "KeepFirstLines": "1", "KeepLastLines": "1",
        "Capitalization": s["caps"],
        "AppliedLanguage": "$ID/Hungarian",
    }
    if s["rule_below"]:
        weight, color, offset = s["rule_below"]
        a.update(RuleBelow="true", RuleBelowLineWeight=num(weight), RuleBelowColor=color,
                 RuleBelowOffset=num(offset), RuleBelowWidth="ColumnWidth", RuleBelowTint="100")
    based_on = (f'<BasedOn type="object">ParagraphStyle/{entry["based_on"]}</BasedOn>' if entry["based_on"]
                else '<BasedOn type="string">$ID/[No paragraph style]</BasedOn>')
    props = (f'{based_on}<Leading type="unit">{num(s["leading"])}</Leading>'
             f'<AppliedFont type="string">{escape(s["font"])}</AppliedFont>')
    return f'<ParagraphStyle {attrs(a)}><Properties>{props}</Properties></ParagraphStyle>'


def styles_xml():
    paragraph = "\n".join(paragraph_style_xml(k, e) for k, e in resolved_styles().items())
    character = "\n".join(
        f'<CharacterStyle Self="CharacterStyle/{key}" Name={quoteattr(name)} Imported="false" {attrs(props)}>'
        '<Properties><BasedOn type="string">$ID/[No character style]</BasedOn></Properties></CharacterStyle>'
        for key, name, props in CHARACTER_STYLES)
    return f"""{XML_HEAD}<idPkg:Styles {PKG}>
<RootCharacterStyleGroup Self="uCharRoot">
<CharacterStyle Self="{NO_CHAR}" Imported="false" Name="$ID/[No character style]"/>
{character}
</RootCharacterStyleGroup>
<RootParagraphStyleGroup Self="uParaRoot">
<ParagraphStyle Self="{NO_PARA}" Name="$ID/[No paragraph style]" Imported="false" FontStyle="Regular" PointSize="12" FillColor="Color/Black"><Properties><Leading type="enumeration">Auto</Leading><AppliedFont type="string">{BODY}</AppliedFont></Properties></ParagraphStyle>
<ParagraphStyle Self="ParagraphStyle/$ID/NormalParagraphStyle" Name="$ID/NormalParagraphStyle" Imported="false" NextStyle="ParagraphStyle/$ID/NormalParagraphStyle"><Properties><BasedOn type="string">$ID/[No paragraph style]</BasedOn></Properties></ParagraphStyle>
{paragraph}
</RootParagraphStyleGroup>
<RootCellStyleGroup Self="uCellRoot"><CellStyle Self="CellStyle/$ID/[None]" Name="$ID/[None]" AppliedParagraphStyle="{NO_PARA}"/></RootCellStyleGroup>
<RootTableStyleGroup Self="uTableRoot">
<TableStyle Self="TableStyle/$ID/[No table style]" Name="$ID/[No table style]"/>
<TableStyle Self="TableStyle/$ID/[Basic Table]" Name="$ID/[Basic Table]"><Properties><BasedOn type="string">$ID/[No table style]</BasedOn></Properties></TableStyle>
</RootTableStyleGroup>
<RootObjectStyleGroup Self="uObjectRoot">
<ObjectStyle Self="ObjectStyle/$ID/[None]" Name="$ID/[None]"/>
<ObjectStyle Self="ObjectStyle/$ID/[Normal Graphics Frame]" Name="$ID/[Normal Graphics Frame]"/>
<ObjectStyle Self="ObjectStyle/$ID/[Normal Text Frame]" Name="$ID/[Normal Text Frame]"/>
</RootObjectStyleGroup>
</idPkg:Styles>
"""


def graphic_xml():
    custom = "\n".join(
        f'<Color Self="Color/{key}" Model="Process" Space="RGB" ColorValue="{r} {g} {b}" ColorOverride="Normal" '
        f'AlternateSpace="NoAlternateColor" AlternateColorValue="" Name={quoteattr(name)} ColorEditable="true" '
        'ColorRemovable="true" Visible="true" SwatchCreatorID="7937"/>'
        for key, (name, (r, g, b)) in COLORS.items())
    return f"""{XML_HEAD}<idPkg:Graphic {PKG}>
<Color Self="Color/Black" Model="Process" Space="CMYK" ColorValue="0 0 0 100" ColorOverride="Specialblack" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="Black" ColorEditable="false" ColorRemovable="false" Visible="true" SwatchCreatorID="7937"/>
<Color Self="Color/Paper" Model="Process" Space="CMYK" ColorValue="0 0 0 0" ColorOverride="Specialpaper" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="Paper" ColorEditable="true" ColorRemovable="false" Visible="true" SwatchCreatorID="7937"/>
<Color Self="Color/Registration" Model="Registration" Space="CMYK" ColorValue="100 100 100 100" ColorOverride="Specialregistration" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="Registration" ColorEditable="false" ColorRemovable="false" Visible="true" SwatchCreatorID="7937"/>
{custom}
<Swatch Self="Swatch/None" Name="None" ColorEditable="false" ColorRemovable="false" Visible="true" SwatchCreatorID="7937"/>
<StrokeStyle Self="StrokeStyle/$ID/Solid" Name="$ID/Solid"/>
</idPkg:Graphic>
"""


def fonts_xml():
    families = {}
    for (family, style), (_, ps_name) in FONT_FILES.items():
        families.setdefault(family, []).append((style, ps_name))
    blocks = []
    for i, (family, faces) in enumerate(families.items()):
        fonts = "".join(
            f'<Font Self="di{i}f{j}" FontFamily={quoteattr(family)} Name={quoteattr(family + " " + style)} '
            f'PostScriptName="{ps}" Status="Installed" FontStyleName="{style}" FontType="TrueType" WritingScript="0" '
            f'FullName={quoteattr(family + " " + style)} FullNameNative={quoteattr(family + " " + style)} '
            f'FontStyleNameNative="{style}" PlatformName="$ID/" Version=""/>'
            for j, (style, ps) in enumerate(faces))
        blocks.append(f'<FontFamily Self="di{i}" Name={quoteattr(family)}>{fonts}</FontFamily>')
    return f'{XML_HEAD}<idPkg:Fonts {PKG}>\n' + "\n".join(blocks) + "\n</idPkg:Fonts>\n"


def margin_xml():
    positions = f"0 {num(COLUMN_W)} {num(COLUMN_W + GUTTER)} {num(TEXT_W)}"
    # IDML: on facing pages Left is the inside margin and Right the outside margin.
    return (f'<MarginPreference ColumnCount="2" ColumnGutter="{num(GUTTER)}" Top="{num(TOP)}" '
            f'Bottom="{num(BOTTOM)}" Left="{num(INSIDE)}" Right="{num(OUTSIDE)}" ColumnDirection="Horizontal" '
            f'ColumnsPositions="{positions}"/>')


def preferences_xml(page_count):
    return f"""{XML_HEAD}<idPkg:Preferences {PKG}>
<DocumentPreference PageHeight="{num(PAGE_H)}" PageWidth="{num(PAGE_W)}" PagesPerDocument="{page_count}" FacingPages="true" DocumentBleedTopOffset="{num(BLEED)}" DocumentBleedBottomOffset="{num(BLEED)}" DocumentBleedInsideOrLeftOffset="{num(BLEED)}" DocumentBleedOutsideOrRightOffset="{num(BLEED)}" DocumentBleedUniformSize="true" SlugTopOffset="0" SlugBottomOffset="0" SlugInsideOrLeftOffset="0" SlugRightOrOutsideOffset="0" DocumentSlugUniformSize="false" PreserveLayoutWhenShuffling="true" AllowPageShuffle="true" OverprintBlack="true" PageBinding="LeftToRight" ColumnDirection="Horizontal" ColumnGuideLocked="true" MasterTextFrame="false" SnippetImportUsesOriginalLocation="false" Intent="PrintIntent"/>
{margin_xml()}
<ViewPreference HorizontalMeasurementUnits="Millimeters" VerticalMeasurementUnits="Millimeters" TypographicMeasurementUnits="Points" TextSizeMeasurementUnits="Points" PrintDialogMeasurementUnits="Millimeters" LineMeasurementUnits="Points" CursorKeyIncrement="1" ShowRulers="true" ShowFrameEdges="true"/>
</idPkg:Preferences>
"""


# ---------------------------------------------------------------- stories

def char_range(style, xml):
    return f'<CharacterStyleRange AppliedCharacterStyle="{style}">{xml}</CharacterStyleRange>'


def inline_xml(text):
    return "".join(char_range(f"CharacterStyle/{style}" if style else NO_CHAR, f"<Content>{escape(chunk)}</Content>")
                   for style, chunk in runs(text))


def paragraph_xml(style, inner, last):
    end = "" if last else char_range(NO_CHAR, "<Br/>")
    return f'<ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/{style}">{inner}{end}</ParagraphStyleRange>'


def cell_style_key(header, align, small):
    return ("TablaFej" if header else "TablaSzoveg") + ALIGN_SUFFIX[align] + ("Kicsi" if small else "")


def cell_xml(table_id, c, r, text, align, plan):
    header = r == 0
    fill = RED if header else (PARCHMENT if r % 2 == 0 else "Color/Paper")
    a = {
        "Self": f"{table_id}i{c}_{r}", "Name": f"{c}:{r}", "RowSpan": "1", "ColumnSpan": "1",
        "AppliedCellStyle": "CellStyle/$ID/[None]", "AppliedCellStylePriority": "0",
        "TopInset": "0", "BottomInset": "0", "LeftInset": "0", "RightInset": "0",
        "VerticalJustification": "CenterAlign" if header else "TopAlign", "FillColor": fill, "FillTint": "100",
        "TopEdgeStrokeWeight": "0", "LeftEdgeStrokeWeight": "0", "RightEdgeStrokeWeight": "0",
        "BottomEdgeStrokeWeight": "0.4", "BottomEdgeStrokeColor": RULE, "BottomEdgeStrokeTint": "100",
    }
    style = cell_style_key(header, align, plan.small)
    content = paragraph_xml(style, inline_xml(text) if text else char_range(NO_CHAR, ""), last=True)
    return f"<Cell {attrs(a)}>{content}</Cell>"


def table_xml(table_id, block, plan):
    rows = plan.rows
    parts = [f'<Table Self="{table_id}" HeaderRowCount="1" FooterRowCount="0" BodyRowCount="{len(rows) - 1}" '
             f'ColumnCount="{len(plan.widths)}" AppliedTableStyle="TableStyle/$ID/[Basic Table]" '
             'TableDirection="LeftToRightDirection">']
    # Affinity keeps imported row heights as they are, so every row gets the height its text needs.
    parts += [f'<Row Self="{table_id}Row{r}" Name="{r}" SingleRowHeight="{num(h)}" MinimumHeight="{num(h)}" '
              'AutoGrow="true"/>' for r, h in enumerate(row_heights(block, plan))]
    parts += [f'<Column Self="{table_id}Column{c}" Name="{c}" SingleColumnWidth="{num(w)}"/>'
              for c, w in enumerate(plan.widths)]
    # IDML names cells "column:row"; Affinity ignores the names and fills cells in file order, row by row.
    parts += [cell_xml(table_id, c, r, rows[r][c], block.aligns[c], plan)
              for r in range(len(rows)) for c in range(len(plan.widths))]
    parts.append("</Table>")
    return "".join(parts)


def story_xml(story_id, paragraphs):
    return f"""{XML_HEAD}<idPkg:Story {PKG}>
<Story Self="{story_id}" AppliedTOCStyle="n" UserText="true" IsEndnoteStory="false" TrackChanges="false" StoryTitle="$ID/" AppliedNamedGrid="n">
<StoryPreference OpticalMarginAlignment="false" OpticalMarginSize="12" FrameType="TextFrameType" StoryOrientation="Horizontal" StoryDirection="LeftToRightDirection"/>
<InCopyExportOption IncludeGraphicProxies="true" IncludeAllResources="false"/>
{"".join(paragraphs)}
</Story>
</idPkg:Story>
"""


def story_paragraphs(story):
    out = []
    for i, block in enumerate(story.blocks):
        last = i == len(story.blocks) - 1
        if block.kind == "table":
            table = table_xml(f"{story.id}Tab{i}", block, story.plans[i])
            out.append(paragraph_xml("Tablazat", char_range(NO_CHAR, table), last))
        else:
            out.append(paragraph_xml(block.style, inline_xml(display_text(block)), last))
    return out


def folio_story(story_id, style):
    return story_xml(story_id, [paragraph_xml(style, char_range(NO_CHAR, f"<Content>{PAGE_NUMBER}</Content>"), True)])


# ---------------------------------------------------------------- spreads

def rect_path(x1, y1, x2, y2):
    points = ((x1, y1), (x1, y2), (x2, y2), (x2, y1))
    anchors = "".join(
        f'<PathPointType Anchor="{num(x)} {num(y)}" LeftDirection="{num(x)} {num(y)}" RightDirection="{num(x)} {num(y)}"/>'
        for x, y in points)
    return (f'<Properties><PathGeometry><GeometryPathType PathOpen="false"><PathPointArray>{anchors}'
            '</PathPointArray></GeometryPathType></PathGeometry></Properties>')


def text_frame_xml(frame_id, story_id, prev_id, next_id, box, columns):
    column_width = COLUMN_W if columns == 2 else box[2] - box[0]
    inset = "".join('<ListItem type="unit">0</ListItem>' for _ in range(4))
    return (f'<TextFrame Self="{frame_id}" ParentStory="{story_id}" PreviousTextFrame="{prev_id}" '
            f'NextTextFrame="{next_id}" ContentType="TextType" ItemLayer="{LAYER}" Visible="true" Name="$ID/" '
            'Locked="false" AppliedObjectStyle="ObjectStyle/$ID/[Normal Text Frame]" ItemTransform="1 0 0 1 0 0">'
            f'{rect_path(*box)}'
            f'<TextFramePreference TextColumnCount="{columns}" TextColumnGutter="{num(GUTTER)}" '
            f'TextColumnFixedWidth="{num(column_width)}" UseFixedColumnWidth="false" FirstBaselineOffset="AscentOffset" '
            'MinimumFirstBaselineOffset="0" VerticalJustification="TopAlign" IgnoreWrap="false" AutoSizingType="Off">'
            f'<Properties><InsetSpacing type="list">{inset}</InsetSpacing></Properties></TextFramePreference>'
            '</TextFrame>')


def side_of(page_number):
    return "right" if page_number % 2 else "left"


def page_origin(side):
    return (-PAGE_W if side == "left" else 0.0), -PAGE_H / 2


def on_spread(box, side):
    x0, y0 = page_origin(side)
    x1, y1, x2, y2 = box
    return x1 + x0, y1 + y0, x2 + x0, y2 + y0


def folio_box(side):
    y1 = PAGE_H - BOTTOM + 14
    if side == "left":
        return OUTSIDE, y1, OUTSIDE + 80, y1 + 14
    return PAGE_W - OUTSIDE - 80, y1, PAGE_W - OUTSIDE, y1 + 14


def page_xml(page_id, name, side, master_id, applied_master=True):
    x0, y0 = page_origin(side)
    return (f'<Page Self="{page_id}" Name="{name}" AppliedMaster="{master_id if applied_master else "n"}" '
            f'OverrideList="" TabOrder="" GeometricBounds="0 0 {num(PAGE_H)} {num(PAGE_W)}" '
            f'ItemTransform="1 0 0 1 {num(x0)} {num(y0)}" MasterPageTransform="1 0 0 1 0 0">'
            '<Properties><PageColor type="enumeration">UseMasterColor</PageColor></Properties>'
            f'{margin_xml()}</Page>')


def spread_groups(page_count):
    """Facing pages: page 1 is a lone right page, then left/right pairs."""
    groups = [[1]]
    for n in range(2, page_count + 1, 2):
        groups.append([n] + ([n + 1] if n + 1 <= page_count else []))
    return groups


def spread_xml(index, numbers, pages, frames):
    binding = "0" if side_of(numbers[0]) == "right" else "1"
    page_items = "".join(page_xml(f"uPage{n}", str(n), side_of(n), pages[n - 1].master) for n in numbers)
    return f"""{XML_HEAD}<idPkg:Spread {PKG}>
<Spread Self="uSpread{index}" PageCount="{len(numbers)}" BindingLocation="{binding}" ShowMasterItems="true" AllowPageShuffle="true" ItemTransform="1 0 0 1 0 0" FlattenerOverride="Default" PageTransitionType="None">
{page_items}
{"".join(frames)}
</Spread>
</idPkg:Spread>
"""


def master_xml(master_id, prefix, base, folio_stories):
    pages = "".join(page_xml(f"{master_id}{side}", prefix, side, master_id, applied_master=False)
                    for side in ("left", "right"))
    frames = "".join(text_frame_xml(f"{master_id}F{side}", story, "n", "n", on_spread(folio_box(side), side), 1)
                     for side, story in folio_stories.items())
    return f"""{XML_HEAD}<idPkg:MasterSpread {PKG}>
<MasterSpread Self="{master_id}" Name="{prefix}-{base}" NamePrefix="{prefix}" BaseName="{base}" ShowMasterItems="true" PageCount="2" ItemTransform="1 0 0 1 0 0" OverriddenPageItemProps="" PageColor="UseMasterColor">
{pages}
{frames}
</MasterSpread>
</idPkg:MasterSpread>
"""


def frame_links(pages):
    """Frame id of every (page, frame) and the previous and next frame of the same story."""
    ids, chains = {}, {}
    for p, page in enumerate(pages, start=1):
        for k, frame in enumerate(page.frames):
            ids[(p, k)] = f"uFr{p}_{k}"
            chains.setdefault(frame.story, []).append((p, k))
    links = {}
    for chain in chains.values():
        for i, key in enumerate(chain):
            prev_id = ids[chain[i - 1]] if i > 0 else "n"
            next_id = ids[chain[i + 1]] if i + 1 < len(chain) else "n"
            links[key] = (ids[key], prev_id, next_id)
    return links


# ---------------------------------------------------------------- package

def designmap_xml(story_ids, spread_count, page_count):
    master_refs = "\n".join(f'<idPkg:MasterSpread src="MasterSpreads/MasterSpread_{m}.xml"/>' for m in MASTERS)
    spread_refs = "\n".join(f'<idPkg:Spread src="Spreads/Spread_uSpread{i}.xml"/>' for i in range(spread_count))
    story_refs = "\n".join(f'<idPkg:Story src="Stories/Story_{s}.xml"/>' for s in story_ids)
    return f"""{XML_HEAD}<?aid style="50" type="document" readerVersion="6.0" featureSet="257" product="16.0(32)" ?>
<Document xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="16.0" Self="d" StoryList="{" ".join(story_ids)}" Name="wispers-0.8.indd" ZeroPoint="0 0" ActiveLayer="{LAYER}" CMYKProfile="Coated FOGRA39 (ISO 12647-2:2004)" RGBProfile="sRGB IEC61966-2.1" SolidColorIntent="UseColorSettings" AfterBlendingIntent="UseColorSettings" DefaultImageIntent="UseColorSettings" RGBPolicy="PreserveEmbeddedProfiles" CMYKPolicy="CombinationOfPreserveAndSafeCmyk" AccurateLABSpots="false">
<idPkg:Graphic src="Resources/Graphic.xml"/>
<idPkg:Fonts src="Resources/Fonts.xml"/>
<idPkg:Styles src="Resources/Styles.xml"/>
<idPkg:Preferences src="Resources/Preferences.xml"/>
<idPkg:Tags src="XML/Tags.xml"/>
<Layer Self="{LAYER}" Name="Szöveg" Visible="true" Locked="false" IgnoreWrap="false" ShowGuides="true" LockGuides="false" UI="true" Expendable="true" Printable="true"><Properties><LayerColor type="enumeration">LightBlue</LayerColor></Properties></Layer>
{master_refs}
{spread_refs}
<Section Self="uSection1" Length="{page_count}" Name="" ContinueNumbering="true" IncludeSectionPrefix="false" PageNumberStyle="Arabic" PageStart="uPage1" PageNumberStart="1" SectionPrefix="" Marker=""/>
<idPkg:BackingStory src="XML/BackingStory.xml"/>
{story_refs}
</Document>
"""


BACKING_STORY = f"""{XML_HEAD}<idPkg:BackingStory {PKG}>
<XmlStory Self="uBacking" AppliedTOCStyle="n" UserText="true" IsEndnoteStory="false" TrackChanges="false" StoryTitle="$ID/" AppliedNamedGrid="n">
<StoryPreference OpticalMarginAlignment="false" OpticalMarginSize="12" FrameType="TextFrameType" StoryOrientation="Horizontal" StoryDirection="LeftToRightDirection"/>
<ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/$ID/NormalParagraphStyle"><CharacterStyleRange AppliedCharacterStyle="{NO_CHAR}"><XMLElement Self="uRootElement" MarkupTag="XMLTag/Root"/></CharacterStyleRange></ParagraphStyleRange>
</XmlStory>
</idPkg:BackingStory>
"""

TAGS = f"""{XML_HEAD}<idPkg:Tags {PKG}>
<XMLTag Self="XMLTag/Root" Name="Root"><Properties><TagColor type="enumeration">LightBlue</TagColor></Properties></XMLTag>
</idPkg:Tags>
"""

CONTAINER = f"""{XML_HEAD}<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
<rootfiles><rootfile full-path="designmap.xml" media-type="text/xml"/></rootfiles>
</container>
"""


def spread_files(book):
    links = frame_links(book.pages)
    groups = spread_groups(len(book.pages))
    files = {}
    for index, numbers in enumerate(groups):
        frames = []
        for n in numbers:
            for k, frame in enumerate(book.pages[n - 1].frames):
                frame_id, prev_id, next_id = links[(n, k)]
                box = on_spread(frame.box, side_of(n))
                frames.append(text_frame_xml(frame_id, frame.story, prev_id, next_id, box, frame.columns))
        files[f"Spreads/Spread_uSpread{index}.xml"] = spread_xml(index, numbers, book.pages, frames)
    return files, len(groups)


def package_files(book):
    files = {f"Stories/Story_{s.id}.xml": story_xml(s.id, story_paragraphs(s)) for s in book.stories.values()}
    files[f"Stories/Story_{FOLIO_STORIES['left']}.xml"] = folio_story(FOLIO_STORIES["left"], "Oldalszam")
    files[f"Stories/Story_{FOLIO_STORIES['right']}.xml"] = folio_story(FOLIO_STORIES["right"], "OldalszamJobb")
    for master_id, (prefix, base, stories) in MASTERS.items():
        files[f"MasterSpreads/MasterSpread_{master_id}.xml"] = master_xml(master_id, prefix, base, stories)
    spreads, spread_count = spread_files(book)
    files.update(spreads)
    story_ids = list(book.stories) + list(FOLIO_STORIES.values())
    files["designmap.xml"] = designmap_xml(story_ids, spread_count, len(book.pages))
    files["META-INF/container.xml"] = CONTAINER
    files["Resources/Graphic.xml"] = graphic_xml()
    files["Resources/Fonts.xml"] = fonts_xml()
    files["Resources/Styles.xml"] = styles_xml()
    files["Resources/Preferences.xml"] = preferences_xml(len(book.pages))
    files["XML/BackingStory.xml"] = BACKING_STORY
    files["XML/Tags.xml"] = TAGS
    return files


def write_package(book, out_path):
    files = package_files(book)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_path, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/vnd.adobe.indesign-idml-package",
                   compress_type=zipfile.ZIP_STORED)
        for name, content in files.items():
            z.writestr(name, content.encode("utf-8"), compress_type=zipfile.ZIP_DEFLATED)
    return files
