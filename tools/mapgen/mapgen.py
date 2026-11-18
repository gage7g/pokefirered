#!/usr/bin/env python3
"""
Turn a text grid into a map layout (map.bin + border.bin) for this decomp.

Usage (from the project root):
    python3 tools/mapgen/mapgen.py data/mapgrids/TestIsland.txt

A grid file is plain text. Lines starting with '#' are comments. Every other
non-empty line is one row of the map, one character per 16x16 tile. All rows
must be the same length. Output goes to data/layouts/<GridFileName>/.

Each map block is 2 bytes (little endian):
    bits 0-9   metatile id (which tile picture to use)
    bits 10-11 collision (1 = blocked)
    bits 12-15 elevation (3 = normal ground, 1 = water)

The legend below only uses tiles from the shared general tileset, so any map
that uses gTileset_General as its primary tileset can use them. Add new
characters here as we find more tile ids.
"""
import os
import struct
import sys

# char -> (metatile id or [[row0 tiles],[row1 tiles]] indexed by [y%2][x%2], collision, elevation)
LEGEND = {
    ".": (0x00D, 0, 3),                                  # plain grass
    "~": (0x12B, 0, 1),                                  # calm water (needs Surf)
    "T": ([[0x01C, 0x01D], [0x014, 0x015]], 1, 0),       # tree wall, place in 2x2 groups
}
BORDER_CHAR = "~"


def block(ch, x, y):
    if ch not in LEGEND:
        sys.exit(f"Unknown character {ch!r} at x={x}, y={y}. Add it to LEGEND.")
    tile, col, elev = LEGEND[ch]
    if isinstance(tile, list):
        tile = tile[y % 2][x % 2]
    return (tile & 0x3FF) | ((col & 3) << 10) | ((elev & 0xF) << 12)


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    path = sys.argv[1]
    name = os.path.splitext(os.path.basename(path))[0]
    rows = [l.rstrip("\n") for l in open(path, encoding="utf-8")
            if l.strip() and not l.lstrip().startswith("#")]
    if not rows:
        sys.exit("Grid has no rows.")
    width = len(rows[0])
    for i, r in enumerate(rows):
        if len(r) != width:
            sys.exit(f"Row {i} is {len(r)} wide but row 0 is {width} wide.")
    out_dir = os.path.join("data", "layouts", name)
    os.makedirs(out_dir, exist_ok=True)
    data = b"".join(struct.pack("<H", block(c, x, y))
                    for y, r in enumerate(rows) for x, c in enumerate(r))
    open(os.path.join(out_dir, "map.bin"), "wb").write(data)
    b = struct.pack("<H", block(BORDER_CHAR, 0, 0))
    open(os.path.join(out_dir, "border.bin"), "wb").write(b * 4)
    print(f"{name}: {width}x{len(rows)} -> {out_dir}/map.bin ({len(data)} bytes)")
    print(f"layouts.json needs: \"width\": {width}, \"height\": {len(rows)}")


main()
