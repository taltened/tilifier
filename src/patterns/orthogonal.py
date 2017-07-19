'''
Logic for creating tilesets on an orthogonal grid
'''
import itertools
from PIL import Image
from tileutil import copy_tile, map_tile

class OrthogonalSurvey(object):
    TOTAL = 18
    COLUMNS = 4
    ROWS = 5
    '''
    Orthogonal tilesets consist of:
    1 full tile
    1 hollow tile
    16 wall tiles (4 rotations each of 0-3 contiguous wall segments)
    '''
    def __init__(self, width, height, columns, rows):
        self.width = width
        self.height = height
        self.columns = columns
        self.rows = rows
        self.source_width = self.width * self.columns
        self.source_height = self.height * self.rows
        self.output_width = self.source_width * self.COLUMNS
        self.output_height = self.source_height * self.ROWS
        print 'width = %s' % width
        print 'height = %s' % height
        print 'columns = %s' % columns
        print 'rows = %s' % rows


class WallOptions(object):
    def __init__(self, thickness, natural):
        self.thickness = thickness
        self.natural = natural


class ShadowOptions(object):
    def __init__(self, thickness, intensity, color):
        self.thickness = thickness
        self.intensity = intensity
        self.color = (int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16))


class OrthogonalSurveyor(object):
    def __init__(self):
        self._survey = None
        self._walls = None
        self._shadows = None

    def survey(self, width, height, columns, rows):
        if not width or width <= 0:
            width = 100
        if not height or height <= 0:
            height = 100
        if not columns or columns <= 0:
            columns = 1
        if not rows or rows <= 0:
            rows = 1
        self._survey = OrthogonalSurvey(width, height, columns, rows)
        return self._survey

    def configure_walls(self, thickness, natural):
        self._walls = WallOptions(thickness, natural)
        return self._walls

    def configure_undershadows(self, thickness, intensity, color):
        self._shadows = ShadowOptions(thickness, intensity, color)
        return self._shadows


class OrthogonalTextureParser(object):

    def make_test_block(self, dimensions):
        colors = [
            (255, 0, 0, 255),
            (127, 0, 127, 255),
            (0, 0, 255, 255),
            (127, 0, 127, 255),
        ]
        for y in xrange(dimensions.height):
            yield list(itertools.chain(*((colors[(x+y)%4] for x in xrange(dimensions.width)))))

    def window(self, texture, width, height, source_width):
        rows = itertools.islice(texture, height)
        for row in rows:
            yield list(itertools.islice(row, width * 4))

    def tilify(self, texture, width, height):
        i = iter(texture.getdata())
        def expand_row():
            for x in xrange(width):
                pixel = i.next()
                for x in xrange(4):
                    yield pixel[x]
        for y in xrange(height):
            yield expand_row()

    def parse(self, texture, dimensions):
        texture.putalpha(255)
        texture = texture.resize((dimensions.source_width, dimensions.source_height), Image.LANCZOS)
        # TODO(talteneder): split into appropriate outputs
        return [self.tilify(texture, dimensions.source_width, dimensions.source_height)]


class OrthogonalTileMaker(object):
    def __init__(self):
        self.walls = None
        self.undershadows = None

    def cut_walls(self, dimensions, wall_options):
        xmax = int(dimensions.width * 0.5 * wall_options.thickness)
        ymax = int(dimensions.height * 0.5 * wall_options.thickness)
        xmin = dimensions.width - xmax - 1
        ymin = dimensions.height - ymax - 1

        self.walls = [
            # full tile
            lambda x,y: True,
            # hollow tile
            lambda x,y: x < xmax or y < ymax or x > xmin or y > ymin,
            # clockwise from top-left
            lambda x,y: y < ymax and x < xmax,
            lambda x,y: y < ymax,
            lambda x,y: y < ymax or x > xmin,
            lambda x,y: y < ymax or x > xmin or y > ymin,
            # clockwise from top-right
            lambda x,y: x > xmin and y < ymax,
            lambda x,y: x > xmin,
            lambda x,y: x > xmin or y > ymin,
            lambda x,y: x > xmin or y > ymin or x < xmax,
            # clockwise from bottom-right
            lambda x,y: y > ymin and x > xmin,
            lambda x,y: y > ymin,
            lambda x,y: y > ymin or x < xmax,
            lambda x,y: y > ymin or x < xmax or y < ymax,
            # clockwise from bottom-left
            lambda x,y: x < xmax and y > ymin,
            lambda x,y: x < xmax,
            lambda x,y: x < xmax or y < ymax,
            lambda x,y: x < xmax or y < ymax or x > xmin,
        ]


    def undershade(self, dimensions, wall_options, shadow_options):
        xmax = int(dimensions.width * 0.5 * wall_options.thickness) - 1
        ymax = int(dimensions.height * 0.5 * wall_options.thickness) - 1
        xmin = dimensions.width - xmax - 1
        ymin = dimensions.height - ymax - 1
        width = dimensions.width * 0.5 * shadow_options.thickness + 2
        height = dimensions.height * 0.5 * shadow_options.thickness + 2
        def low(start, end):
            def _t(p):
                if p < start:
                    return 1
                elif p > end:
                    return 0
                else:
                    return (end - p) / (end - start)
            return _t
        def high(start, end):
            def _t(p):
                if p < start:
                    return 0
                elif p > end:
                    return 1
                else:
                    return (p - start) / (end - start)
            return _t
        txl = low(xmax, xmax+width)
        txh = high(xmin-width, xmin)
        tyl = low(ymax, ymax+height)
        tyh = high(ymin-height, ymin)

        def darken(*args):
            return 1 - reduce(lambda t,x: t*(1-x), args, 1)
        def lighten(*args):
            return reduce(lambda t,x: t*x, args, 1)

        a = lambda t: int(255 * t * shadow_options.intensity)

        self.undershadows = [
            # full tile
            lambda x,y: 0,
            # hollow tile
            lambda x,y: a(darken(txl(x), txh(x), tyl(y), tyh(y))),
            # clockwise from top-left
            lambda x,y: a(lighten(txl(x), tyl(y))),
            lambda x,y: a(tyl(y)),
            lambda x,y: a(darken(txh(x), tyl(y))),
            lambda x,y: a(darken(txh(x), tyl(y), tyh(y))),
            # clockwise from top-right
            lambda x,y: a(lighten(txh(x), tyl(y))),
            lambda x,y: a(txh(x)),
            lambda x,y: a(darken(txh(x), tyh(y))),
            lambda x,y: a(darken(txl(x), txh(x), tyh(y))),
            # clockwise from bottom-right
            lambda x,y: a(lighten(txh(x), tyh(y))),
            lambda x,y: a(tyh(y)),
            lambda x,y: a(darken(txl(x), tyh(y))),
            lambda x,y: a(darken(txl(x), tyl(y), tyh(y))),
            # clockwise from bottom-left
            lambda x,y: a(lighten(txl(x), tyh(y))),
            lambda x,y: a(txl(x)),
            lambda x,y: a(darken(txl(x), tyl(y))),
            lambda x,y: a(darken(txl(x), txh(x), tyl(y))),
        ]

    def expand(self, tile, dimensions, wall_options, shadow_options):
        def cut_tile(is_visible, shadow_alpha):
            def _f(value, x, y, channel):
                if is_visible(x,y):
                    if channel < 3:
                        return value
                    else:
                        return 255
                else:
                    if channel < 3:
                        return shadow_options.color[channel]
                    else:
                        return shadow_alpha(x,y)
            return _f
        tiles = copy_tile(tile, 18)
        return (map_tile(tile, cut_tile(self.walls[x], self.undershadows[x])) for x, tile in enumerate(tiles))


class OrthogonalTilesetStitcher(object):

    def empty_tile(self, width, height):
        for x in xrange(height):
            yield self.empty_row(width)

    def empty_row(self, width):
        for x in xrange(width):
            for y in xrange(4): # RGBA
                yield 0

    def stitch_horizontal(self, tiles, tile_height):
        '''Places a grid of tiles in a row left-to-right'''
        iters = [iter(tile) for tile in tiles]
        for y in xrange(tile_height):
            yield itertools.chain(*[i.next() for i in iters])

    def stitch_vertical(self, tiles):
        '''Places a grid of tiles in a column top-to-bottom'''
        for tile in tiles:
            for row in tile:
                yield row

    def stitch_grid(self, iterator, columns, rows, row_height):
        return self.stitch_vertical((
            self.stitch_horizontal((iterator.next() for x in xrange(columns)), row_height)
            for y in xrange(rows)))

    def compactify(self, tilesets, columns, rows, height, count):
        '''
        Combines a list of tilesets into a single tileset
        by stitching together like tiles into larger tiles
        '''
        iters = [iter(tileset) for tileset in tilesets]
        for x in xrange(count):
            yield self.stitch_grid(iter((i.next() for i in iters)), columns, rows, height)

    def insert_empty_tiles(self, tiles, width, height, columns, rows, total):
        i = iter(tiles)
        blanks = rows * columns - total
        for x in xrange(columns - blanks):
            yield i.next()
        for x in xrange(blanks):
            yield self.empty_tile(width, height)
        for x in xrange((rows-1) * columns):
            yield i.next()

    def stitch(self, tiles, dim):
        tiles = self.compactify(tiles, dim.columns, dim.rows, dim.height, dim.TOTAL)
        tiles = self.insert_empty_tiles(tiles, dim.source_width, dim.source_height, dim.COLUMNS, dim.ROWS, dim.TOTAL)
        return self.stitch_grid(iter(tiles), dim.COLUMNS, dim.ROWS, dim.source_height)
