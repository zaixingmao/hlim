#!/usr/bin/env python

import math


def bin_search(h, rargs=(), threshold=None, iBinMax=None):
    assert threshold

    s = 0.0
    e2 = 0.0
    for iBinX in range(*rargs):
        s += h.GetBinContent(iBinX)
        e = h.GetBinError(iBinX)
        e2 += e * e
        if 0 < s and math.sqrt(e2)/s < threshold:
            # print iBinX, h.GetBinLowEdge(iBinX), s, math.sqrt(e2), math.sqrt(e2)/s
            if iBinMax is not None and iBinMax < iBinX:
                continue
            else:
                return iBinX
    return None


def binning(h, width, xn_l, x1_r):
    if xn_l <= x1_r:
        return (1, h.GetXaxis().GetXmin(), h.GetXaxis().GetXmax())

    nbins = 1 + int((xn_l - x1_r) / width)
    return (1 + nbins, xn_l - nbins * width, xn_l + width)


def fixed_width(h=None, width=0.1, threshold_r=0.2, threshold_l=0.1):
    iBin = bin_search(h, rargs=(1 + h.GetNbinsX(), 0, -1), threshold=threshold_r)
    xn_l = h.GetBinLowEdge(iBin)

    iBin = bin_search(h, rargs=(0, 2 + h.GetNbinsX()), threshold=threshold_l)
    x1_r = h.GetBinLowEdge(1 + iBin)

    return binning(h, width, xn_l, x1_r)


def variable_width(h=None, minWidth=0.1, threshold=0.2, debug=False):
    if debug:
        header = "   ".join(["iBin", "%6s" % "x", "delta", "low_edges"])
        print header
        print "-" * len(header)

    iBin = 1 + h.GetNbinsX()
    low_edges = []

    while True:
        iBinMax = None
        if low_edges:
            iBinMax = h.FindBin(low_edges[-1] - minWidth)
        iBin = bin_search(h, rargs=(iBin, -1, -1), threshold=threshold, iBinMax=iBinMax)

        if iBin is None:
            break

        x = h.GetBinLowEdge(iBin)
        if low_edges:
            if debug:
                fields = ["%5.3f" % (low_edges[-1] - x)]
            low_edges.append(x)
        else:
            if debug:
                fields = [" fake"]
            low_edges.append(x + minWidth)
            low_edges.append(x)

        if debug:
            fields = ["%4d" % iBin, "%6.3f" % x] + fields
            fields.append(str([float("%6.3f" % y) for y in low_edges]))
            print "   ".join(fields)
        iBin -= 1

    low_edges.reverse()
    return low_edges
