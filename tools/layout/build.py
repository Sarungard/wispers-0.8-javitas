"""Build the Affinity layout (IDML) of the Wispers 0.8 working text.

    python build.py              # writes layout/wispers-0.8.idml and prints the page plan

Open the result in Affinity Publisher with File › Open.
"""
import sys
import zipfile
from pathlib import Path
from xml.dom import minidom

sys.path.insert(0, str(Path(__file__).resolve().parent))

from idml import write_package  # noqa: E402
from plan import build_book  # noqa: E402
from source import RPG, load  # noqa: E402

OUT = RPG / "layout" / "wispers-0.8.idml"


def check_package(path):
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        assert names[0] == "mimetype" and z.getinfo("mimetype").compress_type == zipfile.ZIP_STORED
        for name in names[1:]:
            minidom.parseString(z.read(name))
    return names


def report(book):
    page = 1
    for p in book.pages:
        if p.label:
            print(f"  {page:>3}. oldal  {p.label}")
        page += 1
    for label, columns, count, result in book.report:
        warn = f"  TÚL MAGAS TÁBLÁZAT: {result.too_tall}" if result.too_tall else ""
        warn += "  +1 tartalékoldal (épphogy elférő táblázat)" if result.near_miss else ""
        warn += "  -1 oldal (csak néhány sor lógna át)" if count < result.pages else ""
        print(f"  {label[:46]:<46} {columns} hasáb  {count:>2} oldal  utolsó oldal {result.last_fill:4.0%}{warn}")


def main():
    book = build_book(load())
    write_package(book, OUT)
    names = check_package(OUT)
    report(book)
    print(f"{OUT}: {len(book.pages)} oldal, {len(book.stories)} szövegfolyam, {len(names)} fájl")


if __name__ == "__main__":
    main()
