import numpy as np
from collections import OrderedDict


def read_header_database(fname):
    header = ''
    with open(fname, 'r') as f:
        for line in f:
            if line[0] == '#':
                header += line
            else:
                break
    return header


class VarRange:
    def __init__(self, rng):
        self.min = rng[0]
        self.max = rng[1]
        self.step = rng[2]
        self.lvls = rng[3]

        self._array = None

    @property
    def array(self):
        if self._array is None:
            if self.step > 0:
                self._array = np.arange(self.min, self.max, self.step)
            else:
                self._array = np.linspace(self.min, self.max, self.lvls)
        return self._array


def parse_range(rng):
    try:
        vmin, vmax, vstep = rng.strip().split(':')
    except:
        raise Exception('Cannot parse {}'.format(rng))
    else:
        vmin, vmax, vstep = float(vmin), float(vmax), complex(vstep)
        vlvls = int(vstep.imag)
        vstep = int(vstep.real)

    return [vmin, vmax, vstep, vlvls]


def parse_header_database(header):
    # composition range
    Trange = []
    crange = OrderedDict()

    for line in header.strip().split('\n'):
        line = line.strip('# ')
        try:
            el, rng = line.split()
            rng = parse_range(rng)
        except:
            print('Cannot parse {}'.format(line))
        else:
            if el == 'T':
                Trange = VarRange(rng)
            else:
                crange[el] = VarRange(rng)

    return Trange, crange
