#!/usr/bin/python

'''
Tilifier is a utility
for generating tilesets
from source textures.
'''

import argparse
import sys
from patterns.orthogonal import *
from util import PngWriter, DebugWriter, ImageReader

PATTERN_ORTHOGONAL = 'orthogonal'
PATTERN_HEX_VERTICAL = 'hexv'
PATTERN_HEX_HORIZONTAL = 'hexh'
PATTERNS = [
    PATTERN_ORTHOGONAL,
    PATTERN_HEX_HORIZONTAL,
    PATTERN_HEX_VERTICAL
]


class Tilifier(object):
    def __init__(self,
            width=None, height=None, columns=1, rows=1,
            thickness=0.2, natural=0,
            shadow_thickness=0.1, shadow_intensity='1', shadow_color='000000',
            pattern='orthogonal', debug=False):
        self.reader = ImageReader()
        if debug:
            self.writer = DebugWriter()
        else:
            self.writer = PngWriter()

        if pattern == PATTERN_ORTHOGONAL:
            surveyor = OrthogonalSurveyor()
            self.texture_parser = OrthogonalTextureParser()
            self.tile_maker = OrthogonalTileMaker()
            self.tileset_stitcher = OrthogonalTilesetStitcher()
        elif args.pattern == PATTERN_HEX_VERTICAL:
            # default dimensions for convenience
            if not width:
                width = 97
            if not height:
                height = 112
        elif args.pattern == PATTERN_HEX_HORIZONTAL:
            # default dimensions for convenience
            if not width:
                width = 112
            if not height:
                height = 97

        self.dimensions = surveyor.survey(
            width=width,
            height=height,
            columns=columns,
            rows=rows)
        self.wall_options = surveyor.configure_walls(
            thickness=thickness,
            natural=natural)
        self.shadow_options = surveyor.configure_undershadows(
            thickness=shadow_thickness,
            intensity=shadow_intensity,
            color=shadow_color)
        self.tile_maker.cut_walls(self.dimensions, self.wall_options)
        self.tile_maker.undershade(self.dimensions, self.wall_options, self.shadow_options)

    def tilify(self, file, output):
        texture = self.reader.read(file)
        full_tiles = self.texture_parser.parse(texture, self.dimensions)
        tiles = (
            self.tile_maker.expand(tile, self.dimensions, self.wall_options, self.shadow_options)
            for tile in full_tiles)
        tileset = self.tileset_stitcher.stitch(tiles, self.dimensions)
        self.writer.write(args.output, tileset, self.dimensions)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f', '--file',
        help='Path to the source texture file',
        required=True)
    parser.add_argument(
        '-o', '--output',
        help='Path to write the output tileset file (without extension)',
        required=True)
    parser.add_argument(
        '-p', '--pattern',
        help='The tesselation pattern',
        choices=PATTERNS,
        default='orthogonal')
    parser.add_argument(
        '-w', '--width',
        help='The width of generated tiles',
        type=int)
    parser.add_argument(
        '-y', '--height',
        help='The height of generated tiles',
        type=int)
    parser.add_argument(
        '-c', '--columns',
        help='The number of tiles spanned by the texture horizontally',
        type=int,
        default=1)
    parser.add_argument(
        '-r', '--rows',
        help='The number of tiles spanned by the texture vertically',
        type=int,
        default=1)
    parser.add_argument(
        '-t', '--thickness',
        help='The wall thickness as a ratio of tile size, from no wall (0) to all wall (1)',
        type=float,
        default=0.5)
    parser.add_argument(
        '-n', '--natural',
        help='The regularity of wall surfaces, from straight (0) to natural (1)',
        type=float,
        default=0)
    parser.add_argument(
        '--shadow-thickness',
        help='The thickness of the wall undershadow, from none (0) to intense (1)',
        type=float,
        default=0.1)
    parser.add_argument(
        '--shadow-intensity',
        help='The intensity of the wall undershadow, from none (0) to intense (1)',
        type=float,
        default=1.0)
    parser.add_argument(
        '--shadow-color',
        help='The color of the wall undershadow (6-digit hexadecimal)',
        default='000000')
    parser.add_argument(
        '--debug',
        help='Enable debug mode',
        action='store_true')
    args = parser.parse_args()

    reader = ImageReader()

    if args.debug:
        writer = DebugWriter()
    else:
        writer = PngWriter()

    if args.pattern == PATTERN_ORTHOGONAL:
        surveyor = OrthogonalSurveyor()
        texture_parser = OrthogonalTextureParser()
        tile_maker = OrthogonalTileMaker()
        tileset_stitcher = OrthogonalTilesetStitcher()
    elif args.pattern == PATTERN_HEX_VERTICAL:
        if not args.width:
            args.width = 97
        if not args.height:
            args.height = 112
    elif args.pattern == PATTERN_HEX_HORIZONTAL:
        if not args.width:
            args.width = 112
        if not args.height:
            args.height = 97

    dimensions = surveyor.survey(
        width=args.width,
        height=args.height,
        columns=args.columns,
        rows=args.rows)
    wall_options = surveyor.configure_walls(
        thickness=args.thickness,
        natural=args.natural)
    shadow_options = surveyor.configure_undershadows(
        thickness = args.shadow_thickness,
        intensity=args.shadow_intensity,
        color = args.shadow_color)

    texture = reader.read(args.file)
    full_tiles = texture_parser.parse(texture, dimensions)
    tile_maker.cut_walls(dimensions, wall_options)
    tile_maker.undershade(dimensions, wall_options, shadow_options)
    tiles = (
        tile_maker.expand(tile, dimensions, wall_options, shadow_options)
        for tile in full_tiles)
    tileset = tileset_stitcher.stitch(tiles, dimensions)
    writer.write(args.output, tileset, dimensions)

    return 0


if __name__ == '__main__':
    sys.exit(main())
