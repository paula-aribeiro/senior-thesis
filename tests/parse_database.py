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
    trange = []
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
                trange = rng
            else:
                crange[el] = VarRange(rng)

    return trange, crange
