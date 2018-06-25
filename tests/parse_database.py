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


def parse_linspace(lspace):
    try:
        vmin, vmax, lvls = lspace.strip().split(':')
    except:
        raise Exception('Cannot parse {}'.format(lspace))
    else:
        vmin, vmax, lvls = float(vmin), float(vmax), int(lvls)

    return [vmin, vmax, lvls]


def parse_header_database(header):
    # composition range
    crange = OrderedDict()
    for line in header.strip().split('\n'):
        line = line.strip('# ')
        try:
            el, lspace = line.split()
            lspace = parse_linspace(lspace)
        except:
            print('Cannot parse {}'.format(line))
        else:
            crange[el] = lspace

    return crange
