'''Utility functions for working with tiles'''

import itertools

def map_tile(tile, f):
    for y, row in enumerate(tile):
        yield (f(v, int(x/4), y, x%4) for x, v in enumerate(row))


def copy_tile(tile, n=2):
    i = iter(tile)
    copier = TileRowCopier(i, n)
    return [generate_tile_copy(copier, x) for x in xrange(n)]


def generate_tile_copy(copier, index):
    while copier is not None:
        yield copier.copies[index]
        copier = copier.next()


class TileRowCopier(object):
    def __init__(self, i, n):
        self.i = i
        self.n = n
        self.copies = itertools.tee(i.next(), n)
        self.right = None

    def next(self):
        if not self.right:
            self.right = TileRowCopier(self.i, self.n)
        return self.right
