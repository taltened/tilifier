'''
Shared utilities for tilification
'''
import itertools
import re
from PIL import Image
import png

def force_pos_int(value, default):
    '''Restricts a value to Z+'''
    if not value or value <= 0:
        return default
    return value


def force_perunit(value, default):
    '''Restricts a value to the interval [0,1]'''
    if not value:
        return default
    if value < 0:
        return 0
    if value > 1:
        return 1
    return value


class ImageReader(object):
    '''Texture reader that reads from a jpg file'''
    def read(self, filename):
        return Image.open(filename)

    @staticmethod
    def _bundle_rows(pixel_source, width, channels):
        iterator = iter(pixel_source)
        columns = width * channels
        if channels == 4:
            row = itertools.islice(iterator, columns)
            while row:
                yield row
                row = itertools.islice(iterator, columns)
        else:
            row = itertools.islice(iterator, columns)
            while row:
                yield JpgReader._expand_row(row, width, channels)
                row = itertools.islice(iterator, columns)

    @staticmethod
    def _expand_row(row, width, channels):
        iterator = iter(row)
        for x in xrange(width):
            pixel = iterator.next()
            for channel in pixel:
                yield channel
            for x in xrange(4-channels):
                yield 255


class PngWriter(object):
    '''Tileset writer that outputs a png file'''
    def write(self, filename, tileset, dimensions):
        filename = re.sub(r'(\..*)|$', '.png', filename)
        info = {'width': dimensions.output_width, 'height': dimensions.output_height}
        png.from_array(tileset, 'RGBA', info).save(filename)


class DebugWriter(object):
    '''Tileset writer that outputs raw data for debugging'''
    def write(self, filename, tileset, dimensions):
        for t in tileset:
            print list(t)
