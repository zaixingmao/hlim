def xs_fb(m):
    return {500: 9330.0,
            1000:  468.0,
            1500:   72.3,
            2000:   17.3,
            2500:   5.54,
            3000:   1.29,
            3500:   0.49,
            4000:   0.255,
            4500:   0.17,
            }.get(m)


def xs_pb(m):
    s = xs_fb(m)
    if s:
        return s / 1000.
    else:
        return None
