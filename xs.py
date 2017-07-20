def xs_fb_lo_2015(m):
    return { 500: 9330.0,
             750: 1236.0,
            1000:  468.0,
            1250:  149.0,
            1500:   72.3,
            1750:   31.0,
            2000:   17.3,
            2500:   5.54,
            3000:   1.59,
            3500:   0.597,
            4000:   0.245,
            # 4500:   0.17,
            }.get(m)


def xs_pb_lo_2015(m):
    s = xs_fb_lo_2015(m)
    if s:
        return s / 1000.
    else:
        return None


def xs_pb_nlo_2015(m):
    k_factor = 1.3
    lo = xs_pb_lo_2015(m)
    if lo is None:
        return lo
    return k_factor * lo
