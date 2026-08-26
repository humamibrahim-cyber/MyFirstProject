"""Supermarket shopping list -> illustrated PDF checklist.

Ask for the items you need, match each one to a picture, and print a tidy
PDF you can tick off in the aisle.

    python shopping_list.py                        # interactive
    python shopping_list.py --items "2 x milk, bread, apples"
    python shopping_list.py --file my_list.txt --out groceries.pdf
"""

from __future__ import annotations

import argparse
import datetime as _dt
import os
import re
import sys
from typing import Iterable, NamedTuple

from PIL import Image, ImageDraw, ImageFont

# --------------------------------------------------------------------------
# The picture catalogue: keyword -> (emoji, category)
# --------------------------------------------------------------------------

FRUIT_VEG = "Fruit & Vegetables"
DAIRY = "Dairy & Eggs"
BAKERY = "Bakery"
MEAT = "Meat & Fish"
PANTRY = "Pantry"
FROZEN = "Frozen"
SNACKS = "Snacks & Sweets"
DRINKS = "Drinks"
HOUSE = "Household"
OTHER = "Other"

CATEGORIES = [FRUIT_VEG, DAIRY, BAKERY, MEAT, PANTRY, FROZEN, SNACKS, DRINKS, HOUSE, OTHER]

CATALOGUE: dict[str, tuple[str, str]] = {
    # Fruit & vegetables
    "apple": ("\U0001F34E", FRUIT_VEG),
    "banana": ("\U0001F34C", FRUIT_VEG),
    "orange": ("\U0001F34A", FRUIT_VEG),
    "tangerine": ("\U0001F34A", FRUIT_VEG),
    "lemon": ("\U0001F34B", FRUIT_VEG),
    "lime": ("\U0001F34B", FRUIT_VEG),
    "grape": ("\U0001F347", FRUIT_VEG),
    "strawberry": ("\U0001F353", FRUIT_VEG),
    "blueberry": ("\U0001FAD0", FRUIT_VEG),
    "berries": ("\U0001FAD0", FRUIT_VEG),
    "watermelon": ("\U0001F349", FRUIT_VEG),
    "melon": ("\U0001F348", FRUIT_VEG),
    "pineapple": ("\U0001F34D", FRUIT_VEG),
    "mango": ("\U0001F96D", FRUIT_VEG),
    "peach": ("\U0001F351", FRUIT_VEG),
    "pear": ("\U0001F350", FRUIT_VEG),
    "cherry": ("\U0001F352", FRUIT_VEG),
    "kiwi": ("\U0001F95D", FRUIT_VEG),
    "coconut": ("\U0001F965", FRUIT_VEG),
    "avocado": ("\U0001F951", FRUIT_VEG),
    "tomato": ("\U0001F345", FRUIT_VEG),
    "potato": ("\U0001F954", FRUIT_VEG),
    "sweet potato": ("\U0001F360", FRUIT_VEG),
    "carrot": ("\U0001F955", FRUIT_VEG),
    "corn": ("\U0001F33D", FRUIT_VEG),
    "cucumber": ("\U0001F952", FRUIT_VEG),
    "broccoli": ("\U0001F966", FRUIT_VEG),
    "lettuce": ("\U0001F96C", FRUIT_VEG),
    "cabbage": ("\U0001F96C", FRUIT_VEG),
    "spinach": ("\U0001F96C", FRUIT_VEG),
    "pepper": ("\U0001FAD1", FRUIT_VEG),
    "capsicum": ("\U0001FAD1", FRUIT_VEG),
    "chili": ("\U0001F336", FRUIT_VEG),
    "onion": ("\U0001F9C5", FRUIT_VEG),
    "garlic": ("\U0001F9C4", FRUIT_VEG),
    "mushroom": ("\U0001F344", FRUIT_VEG),
    "eggplant": ("\U0001F346", FRUIT_VEG),
    "aubergine": ("\U0001F346", FRUIT_VEG),
    "olive": ("\U0001FAD2", FRUIT_VEG),
    "salad": ("\U0001F957", FRUIT_VEG),
    "herbs": ("\U0001F33F", FRUIT_VEG),
    "parsley": ("\U0001F33F", FRUIT_VEG),
    "mint": ("\U0001F33F", FRUIT_VEG),
    "fruit": ("\U0001F34E", FRUIT_VEG),
    "vegetable": ("\U0001F955", FRUIT_VEG),
    # Dairy & eggs
    "milk": ("\U0001F95B", DAIRY),
    "cheese": ("\U0001F9C0", DAIRY),
    "butter": ("\U0001F9C8", DAIRY),
    "egg": ("\U0001F95A", DAIRY),
    "yogurt": ("\U0001F963", DAIRY),
    "yoghurt": ("\U0001F963", DAIRY),
    "cream": ("\U0001F95B", DAIRY),
    "labneh": ("\U0001F963", DAIRY),
    # Bakery
    "bread": ("\U0001F35E", BAKERY),
    "baguette": ("\U0001F956", BAKERY),
    "toast": ("\U0001F35E", BAKERY),
    "croissant": ("\U0001F950", BAKERY),
    "bagel": ("\U0001F96F", BAKERY),
    "pita": ("\U0001FAD3", BAKERY),
    "flatbread": ("\U0001FAD3", BAKERY),
    "tortilla": ("\U0001FAD3", BAKERY),
    "pretzel": ("\U0001F968", BAKERY),
    "cake": ("\U0001F370", BAKERY),
    "cupcake": ("\U0001F9C1", BAKERY),
    "pie": ("\U0001F967", BAKERY),
    "donut": ("\U0001F369", BAKERY),
    "doughnut": ("\U0001F369", BAKERY),
    "pancake": ("\U0001F95E", BAKERY),
    "waffle": ("\U0001F9C7", BAKERY),
    # Meat & fish
    "chicken": ("\U0001F357", MEAT),
    "turkey": ("\U0001F983", MEAT),
    "beef": ("\U0001F969", MEAT),
    "steak": ("\U0001F969", MEAT),
    "lamb": ("\U0001F356", MEAT),
    "meat": ("\U0001F969", MEAT),
    "mince": ("\U0001F969", MEAT),
    "bacon": ("\U0001F953", MEAT),
    "ham": ("\U0001F356", MEAT),
    "sausage": ("\U0001F32D", MEAT),
    "fish": ("\U0001F41F", MEAT),
    "salmon": ("\U0001F41F", MEAT),
    "tuna": ("\U0001F41F", MEAT),
    "shrimp": ("\U0001F990", MEAT),
    "prawn": ("\U0001F990", MEAT),
    "crab": ("\U0001F980", MEAT),
    "lobster": ("\U0001F99E", MEAT),
    "squid": ("\U0001F991", MEAT),
    # Pantry
    "rice": ("\U0001F35A", PANTRY),
    "pasta": ("\U0001F35D", PANTRY),
    "spaghetti": ("\U0001F35D", PANTRY),
    "macaroni": ("\U0001F35D", PANTRY),
    "noodle": ("\U0001F35C", PANTRY),
    "flour": ("\U0001F33E", PANTRY),
    "wheat": ("\U0001F33E", PANTRY),
    "sugar": ("\U0001F36C", PANTRY),
    "salt": ("\U0001F9C2", PANTRY),
    "spice": ("\U0001F9C2", PANTRY),
    "oil": ("\U0001FAD2", PANTRY),
    "vinegar": ("\U0001F9F4", PANTRY),
    "sauce": ("\U0001F9F4", PANTRY),
    "ketchup": ("\U0001F345", PANTRY),
    "mayonnaise": ("\U0001F9F4", PANTRY),
    "mustard": ("\U0001F9F4", PANTRY),
    "honey": ("\U0001F36F", PANTRY),
    "jam": ("\U0001F36F", PANTRY),
    "peanut butter": ("\U0001F95C", PANTRY),
    "tahini": ("\U0001F95C", PANTRY),
    "hummus": ("\U0001F96B", PANTRY),
    "bean": ("\U0001F96B", PANTRY),
    "lentil": ("\U0001F96B", PANTRY),
    "chickpea": ("\U0001F96B", PANTRY),
    "canned": ("\U0001F96B", PANTRY),
    "soup": ("\U0001F96B", PANTRY),
    "cereal": ("\U0001F963", PANTRY),
    "oats": ("\U0001F963", PANTRY),
    "granola": ("\U0001F963", PANTRY),
    "nuts": ("\U0001F95C", PANTRY),
    "peanut": ("\U0001F95C", PANTRY),
    "almond": ("\U0001F95C", PANTRY),
    "tea": ("\U0001F375", PANTRY),
    "coffee": ("\u2615", PANTRY),
    # Frozen
    "ice cream": ("\U0001F368", FROZEN),
    "ice": ("\U0001F9CA", FROZEN),
    "frozen": ("\U0001F9CA", FROZEN),
    "pizza": ("\U0001F355", FROZEN),
    "fries": ("\U0001F35F", FROZEN),
    # Snacks & sweets
    "chips": ("\U0001F35F", SNACKS),
    "crisps": ("\U0001F35F", SNACKS),
    "popcorn": ("\U0001F37F", SNACKS),
    "candy": ("\U0001F36C", SNACKS),
    "sweets": ("\U0001F36C", SNACKS),
    "chocolate": ("\U0001F36B", SNACKS),
    "biscuit": ("\U0001F36A", SNACKS),
    "cookie": ("\U0001F36A", SNACKS),
    "cracker": ("\U0001F358", SNACKS),
    "snack": ("\U0001F37F", SNACKS),
    # Drinks
    "water": ("\U0001F4A7", DRINKS),
    "juice": ("\U0001F9C3", DRINKS),
    "soda": ("\U0001F964", DRINKS),
    "cola": ("\U0001F964", DRINKS),
    "pepsi": ("\U0001F964", DRINKS),
    "drink": ("\U0001F964", DRINKS),
    "beer": ("\U0001F37A", DRINKS),
    "wine": ("\U0001F377", DRINKS),
    # Household
    "toilet paper": ("\U0001F9FB", HOUSE),
    "tissue": ("\U0001F9FB", HOUSE),
    "napkin": ("\U0001F9FB", HOUSE),
    "kitchen roll": ("\U0001F9FB", HOUSE),
    "soap": ("\U0001F9FC", HOUSE),
    "shampoo": ("\U0001F9F4", HOUSE),
    "conditioner": ("\U0001F9F4", HOUSE),
    "lotion": ("\U0001F9F4", HOUSE),
    "deodorant": ("\U0001F9F4", HOUSE),
    "toothpaste": ("\U0001FAA5", HOUSE),
    "toothbrush": ("\U0001FAA5", HOUSE),
    "detergent": ("\U0001F9FA", HOUSE),
    "laundry": ("\U0001F9FA", HOUSE),
    "sponge": ("\U0001F9FD", HOUSE),
    "dish soap": ("\U0001F9FD", HOUSE),
    "trash bag": ("\U0001F5D1", HOUSE),
    "bin bag": ("\U0001F5D1", HOUSE),
    "garbage bag": ("\U0001F5D1", HOUSE),
    "broom": ("\U0001F9F9", HOUSE),
    "battery": ("\U0001F50B", HOUSE),
    "bulb": ("\U0001F4A1", HOUSE),
    "razor": ("\U0001FA92", HOUSE),
    "bag": ("\U0001F6CD", HOUSE),
    "dog food": ("\U0001F415", HOUSE),
    "cat food": ("\U0001F408", HOUSE),
}

DEFAULT_EMOJI = "\U0001F6D2"  # shopping trolley

# Longest keyword first, so "peanut butter" wins over "peanut".
_KEYWORDS = sorted(CATALOGUE, key=len, reverse=True)


class Item(NamedTuple):
    name: str
    quantity: str
    emoji: str
    category: str


# --------------------------------------------------------------------------
# Parsing what the user typed
# --------------------------------------------------------------------------

_UNITS = r"(?:x|pcs?|kg|kgs|g|gr|lb|lbs|l|ml|pack|packs|box|boxes|bottles?|cans?|bags?|loa(?:f|ves))"

_QTY_PATTERNS = (
    # "2 milk", "2x milk", "500g rice", "3 x apples"
    re.compile(rf"^(?P<qty>\d+(?:[.,]\d+)?\s*{_UNITS}?)\s*[-*:]?\s+(?P<name>.+)$", re.I),
    re.compile(rf"^(?P<qty>\d+(?:[.,]\d+)?\s*{_UNITS})\s*(?P<name>[A-Za-z].+)$", re.I),
    # "milk x2", "rice 1kg", "eggs (12)"
    re.compile(rf"^(?P<name>.+?)[\s(]+(?:x\s*)?(?P<qty>\d+(?:[.,]\d+)?\s*{_UNITS}?)\)?$", re.I),
)


def _singularise(text: str) -> str:
    """Rough plural stripping so 'batteries' still finds 'battery'.

    Most plurals ('onions', 'tomatoes') already match on their own because the
    keyword is a prefix; this only has to rescue the ones that change spelling.
    """
    def one(word: str) -> str:
        if len(word) > 4 and word.endswith("ies"):
            return word[:-3] + "y"
        if len(word) > 4 and word.endswith("ves"):
            return word[:-3] + "f"
        return word

    return re.sub(r"[a-z]+", lambda m: one(m.group()), text)


def lookup(name: str) -> tuple[str, str]:
    """Find the best picture and aisle for an item name.

    English puts the head noun last, so the match that reaches furthest right
    wins: "orange juice" is a drink, "tomato sauce" is a pantry item. Ties go
    to the longer keyword, keeping "peanut butter" out of the dairy aisle.
    """
    for text in (name.lower(), _singularise(name.lower())):
        best: tuple[int, int, str] | None = None
        for keyword in _KEYWORDS:
            match = re.search(rf"(?<![a-z]){re.escape(keyword)}", text)
            if match:
                score = (match.end(), len(keyword), keyword)
                if best is None or score > best:
                    best = score
        if best:
            return CATALOGUE[best[2]]
    return DEFAULT_EMOJI, OTHER


def _tidy_quantity(raw: str) -> str:
    """'2 x' -> '2', 'x6' -> '6', '500 g' -> '500g' ('1 box' keeps its space)."""
    text = re.sub(r"(?<![a-z])x(?![a-z])", " ", raw.strip(), flags=re.I)
    text = " ".join(text.split())
    return re.sub(r"^(\d+(?:[.,]\d+)?)\s+(g|gr|kg|kgs|mg|ml|l|lb|lbs|oz)$", r"\1\2",
                  text, flags=re.I)


def parse_line(line: str) -> Item | None:
    """Turn one typed line such as '2 x milk' into an Item."""
    text = line.strip().lstrip("-*\u2022").strip()
    if not text:
        return None

    quantity = ""
    name = text
    for pattern in _QTY_PATTERNS:
        match = pattern.match(text)
        if match:
            candidate = match.group("name").strip(" -x*:()")
            if candidate and not candidate.isdigit():
                quantity = _tidy_quantity(match.group("qty"))
                name = candidate
                break

    emoji, category = lookup(name)
    return Item(name=name.strip(), quantity=quantity, emoji=emoji, category=category)


def parse_items(lines: Iterable[str]) -> list[Item]:
    items: list[Item] = []
    for line in lines:
        for part in re.split(r"[,;\n]", line):
            item = parse_line(part)
            if item:
                items.append(item)
    return items


# --------------------------------------------------------------------------
# Fonts and pictures
# --------------------------------------------------------------------------

_FONT_DIR = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
EMOJI_FONT_PATH = os.path.join(_FONT_DIR, "seguiemj.ttf")
EMOJI_NATIVE_SIZE = 109  # Segoe UI Emoji ships its colour layers around this size


def _load_font(candidates: Iterable[str], size: int) -> ImageFont.FreeTypeFont:
    for name in candidates:
        try:
            return ImageFont.truetype(os.path.join(_FONT_DIR, name), size)
        except OSError:
            continue
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default(size)


def regular(size: int) -> ImageFont.FreeTypeFont:
    return _load_font(("segoeui.ttf", "arial.ttf"), size)


def bold(size: int) -> ImageFont.FreeTypeFont:
    return _load_font(("segoeuib.ttf", "arialbd.ttf"), size)


_emoji_cache: dict[tuple[str, int], Image.Image | None] = {}


def emoji_image(char: str, size: int) -> Image.Image | None:
    """Render a colour emoji into a transparent RGBA image."""
    key = (char, size)
    if key in _emoji_cache:
        return _emoji_cache[key]

    glyph = None
    try:
        font = ImageFont.truetype(EMOJI_FONT_PATH, EMOJI_NATIVE_SIZE)
    except OSError:
        font = None

    if font is not None:
        side = EMOJI_NATIVE_SIZE * 2
        canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
        ImageDraw.Draw(canvas).text((side // 2, side // 2), char, font=font,
                                    embedded_color=True, anchor="mm")
        box = canvas.getbbox()
        if box is not None:
            glyph = canvas.crop(box)
            glyph.thumbnail((size, size), Image.LANCZOS)

    _emoji_cache[key] = glyph
    return glyph


# --------------------------------------------------------------------------
# PDF drawing
# --------------------------------------------------------------------------

DPI = 150
PAGE_W, PAGE_H = 1240, 1754  # A4 at 150 dpi
MARGIN = 80
COL_GAP = 40
ROW_H = 96
HEADER_H = 62

INK = (32, 36, 44)
MUTED = (122, 130, 142)
LINE = (223, 227, 234)
ACCENT = (26, 122, 92)
BAND = (240, 246, 243)


def _new_page() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    page = Image.new("RGB", (PAGE_W, PAGE_H), "white")
    return page, ImageDraw.Draw(page)


def _draw_title(draw: ImageDraw.ImageDraw, title: str, subtitle: str) -> int:
    draw.text((MARGIN, MARGIN), title, font=bold(58), fill=INK)
    draw.text((MARGIN, MARGIN + 78), subtitle, font=regular(26), fill=MUTED)
    y = MARGIN + 132
    draw.line((MARGIN, y, PAGE_W - MARGIN, y), fill=ACCENT, width=4)
    return y + 36


def _draw_category(draw: ImageDraw.ImageDraw, y: int, name: str, count: int) -> int:
    band_h = HEADER_H - 12
    draw.rounded_rectangle((MARGIN, y, PAGE_W - MARGIN, y + band_h), radius=10, fill=BAND)
    draw.text((MARGIN + 20, y + band_h // 2), name.upper(), font=bold(24),
              fill=ACCENT, anchor="lm")
    draw.text((PAGE_W - MARGIN - 20, y + band_h // 2),
              f"{count} item{'s' if count != 1 else ''}", font=regular(22),
              fill=MUTED, anchor="rm")
    return y + HEADER_H + 10


def _draw_item(draw: ImageDraw.ImageDraw, page: Image.Image, x: int, y: int,
               width: int, item: Item) -> None:
    mid = y + ROW_H // 2
    right = x + width

    box = 34
    bx, by = x + 6, mid - box // 2
    draw.rounded_rectangle((bx, by, bx + box, by + box), radius=7, outline=ACCENT, width=3)

    picture = emoji_image(item.emoji, 60)
    px = x + 62
    if picture is not None:
        page.paste(picture, (px + (60 - picture.width) // 2, mid - picture.height // 2), picture)

    qty_w = 0
    if item.quantity:
        qty_font = bold(26)
        qty_w = int(draw.textlength(item.quantity, font=qty_font)) + 24
        draw.text((right - 8, mid), item.quantity, font=qty_font, fill=ACCENT, anchor="rm")

    name = item.name[:1].upper() + item.name[1:]
    name_font = bold(30)
    text_x = px + 76
    max_w = right - text_x - qty_w
    while len(name) > 4 and draw.textlength(name, font=name_font) > max_w:
        name = name[:-2] + "\u2026"
    draw.text((text_x, mid), name, font=name_font, fill=INK, anchor="lm")

    draw.line((x + 6, y + ROW_H - 6, right - 6, y + ROW_H - 6), fill=LINE, width=2)


def build_pdf(items: list[Item], out_path: str = "shopping_list.pdf",
              title: str = "Shopping List") -> str:
    """Lay the items out over as many A4 pages as needed and save a PDF."""
    if not items:
        raise ValueError("no items to print")

    grouped: dict[str, list[Item]] = {}
    for item in items:
        grouped.setdefault(item.category, []).append(item)

    col_w = (PAGE_W - 2 * MARGIN - COL_GAP) // 2
    columns = (MARGIN, MARGIN + col_w + COL_GAP)
    bottom = PAGE_H - MARGIN - 40

    stamp = _dt.datetime.now().strftime("%A, %d %B %Y")
    subtitle = f"{len(items)} item{'s' if len(items) != 1 else ''}  \u00b7  {stamp}"

    pages: list[Image.Image] = []
    page, draw = _new_page()
    y = _draw_title(draw, title, subtitle)

    def start_page() -> int:
        nonlocal page, draw
        pages.append(page)
        page, draw = _new_page()
        return MARGIN

    for category in (c for c in CATEGORIES if c in grouped):
        members = grouped[category]
        # Never leave a heading stranded at the foot of a page.
        if y + HEADER_H + ROW_H > bottom:
            y = start_page()
        y = _draw_category(draw, y, category, len(members))

        for index in range(0, len(members), 2):
            if y + ROW_H > bottom:
                y = start_page()
                y = _draw_category(draw, y, f"{category} (continued)", len(members))
            for column, item in enumerate(members[index:index + 2]):
                _draw_item(draw, page, columns[column], y, col_w, item)
            y += ROW_H
        y += 24

    pages.append(page)

    footer = regular(20)
    for number, sheet in enumerate(pages, start=1):
        ImageDraw.Draw(sheet).text(
            (PAGE_W // 2, PAGE_H - MARGIN + 12),
            f"Page {number} of {len(pages)}  \u00b7  tick as you shop",
            font=footer, fill=MUTED, anchor="mm")

    out_path = os.path.abspath(out_path)
    pages[0].save(out_path, "PDF", resolution=DPI, save_all=True, append_images=pages[1:])
    return out_path


# --------------------------------------------------------------------------
# Command line
# --------------------------------------------------------------------------

def _use_utf8_console() -> None:
    """Windows terminals still default to cp1252, which cannot print emoji."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass


def _say(text: str = "") -> None:
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("ascii", "replace").decode("ascii"))


def ask_for_items() -> list[Item]:
    _say("\n\U0001F6D2  Supermarket list builder")
    _say("Type one item per line, e.g. '2 x milk' or 'rice 1kg'.")
    _say("Press Enter on an empty line when you are done.\n")

    items: list[Item] = []
    while True:
        try:
            line = input(f"  {len(items) + 1:>2}. ")
        except (EOFError, KeyboardInterrupt):
            _say()
            break
        if not line.strip():
            break
        for item in parse_items([line]):
            items.append(item)
            extra = f" ({item.quantity})" if item.quantity else ""
            _say(f"      {item.emoji}  {item.name}{extra}  \u2192  {item.category}")
    return items


def read_file(path: str) -> list[Item]:
    with open(path, encoding="utf-8") as handle:
        return parse_items(handle.readlines())


def main(argv: list[str] | None = None) -> int:
    _use_utf8_console()
    parser = argparse.ArgumentParser(
        description="Build an illustrated supermarket checklist as a PDF.")
    parser.add_argument("--items", help="comma separated items instead of the prompt")
    parser.add_argument("--file", help="read the items from a text file, one per line")
    parser.add_argument("--out", default="shopping_list.pdf", help="PDF to write")
    parser.add_argument("--title", default="Shopping List", help="heading for the first page")
    parser.add_argument("--open", dest="open_pdf", action="store_true",
                        help="open the PDF once it is ready")
    args = parser.parse_args(argv)

    if args.file:
        items = read_file(args.file)
    elif args.items:
        items = parse_items([args.items])
    else:
        items = ask_for_items()

    if not items:
        _say("\nNothing on the list \u2014 no PDF written.")
        return 1

    path = build_pdf(items, args.out, args.title)
    _say(f"\n\u2705 {len(items)} items saved to {path}")

    if args.open_pdf and hasattr(os, "startfile"):
        os.startfile(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
