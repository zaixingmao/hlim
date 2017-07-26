def _fb_lo_2016(m):
    return { 500: 5751.0,
             750: 1236.0,
            1000:  386.5,
            1250:  149.0,
            1500:   64.8,
            1750:   31.0,
            2000:   15.8,
            2500:   4.68,
            3000:   1.59,
            3500:   0.597,
            4000:   0.245,
            }.get(m)


def _fb_lo_2015(m):
    return { 500: 9330.0,
            1000:  468.0,
            1500:   72.3,
            2000:   17.3,
            2500:   5.54,
            3000:   1.29,
            }.get(m)


def pb_lo(m, year=None):
    assert year in [2015, 2016]
    if year == 2015:
        s = _fb_lo_2015(m)
    if year == 2016:
        s = _fb_lo_2016(m)
    if s:
        return s / 1000.
    else:
        return None


def pb_nlo(m, year):
    k_factor = 1.3
    lo = pb_lo(m, year)
    if lo is None:
        return lo
    return k_factor * lo
