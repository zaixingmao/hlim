#!/usr/bin/env python

import math
import cfg
import ROOT as r


def histo(fileName, subdir="", name=""):
    f = r.TFile(fileName)
    h = f.Get("%s/%s" % (subdir, name)).Clone()
    h.SetDirectory(0)
    f.Close()
    return h


def bin_search(h, rargs=(), threshold=None):
    assert threshold

    s = 0.0
    e2 = 0.0
    for iBinX in range(*rargs):
        s += h.GetBinContent(iBinX)
        e = h.GetBinError(iBinX)
        e2 += e * e
        if 0 < s and math.sqrt(e2)/s < threshold:
            # print iBinX, h.GetBinLowEdge(iBinX), s, math.sqrt(e2), math.sqrt(e2)/s
            return iBinX
    return None


def binning(h, width, xn_l, x1_r):
    if xn_l <= x1_r:
        return (1, h.GetXaxis().GetXmin(), h.GetXaxis().GetXmax())

    nbins = 1 + int((xn_l - x1_r) / width)
    return (1 + nbins, xn_l - nbins * width, xn_l + width)


def fine_histo():
    vs = cfg.variables()
    assert len(vs) == 1
    d = vs[0]
    fileName = cfg.outFileName(var=d["var"], cuts=d["cuts"])
    return histo(fileName, subdir="tauTau_2jet2tag", name="sum_b")


def fixed_width(width=0.1, threshold_r=0.2, threshold_l=0.1):
    h = fine_histo()
    iBin = bin_search(h, rargs=(1 + h.GetNbinsX(), 0, -1), threshold=threshold_r)
    xn_l = h.GetBinLowEdge(iBin)

    iBin = bin_search(h, rargs=(0, 2 + h.GetNbinsX()), threshold=threshold_l)
    x1_r = h.GetBinLowEdge(1 + iBin)

    return binning(h, width, xn_l, x1_r)


def variable_width(minWidth=0.1, threshold=0.2, debug=True):
    h = fine_histo()
    low_edges = []

    iBin = 1 + h.GetNbinsX()
    if debug:
        header = "   ".join(["iBin", "%6s" % "x", "delta", "   note", "%6s" % "x2", "iBin2", "low_edges"])
        print header
        print "-" * len(header)

    while True:
        iBin = bin_search(h, rargs=(iBin, -1, -1), threshold=threshold)
        if iBin is None:
            break

        x = h.GetBinLowEdge(iBin)
        fields = ["%4d" % iBin, "%6.3f" % x]

        if low_edges:
            fields.append("%5.3f" % (low_edges[-1] - x))
            if minWidth <= (low_edges[-1] - x):
                fields.append("%7s" % "ok")
                low_edges.append(x)
            else:
                fields.append("%7s" % "revised")
                x = low_edges[-1] - minWidth
                low_edges.append(x)
                iBin = h.FindBin(x)
        else:
            fields += ["fake", " " * 8]
            low_edges.append(x + minWidth)
            low_edges.append(x)

        fields.append("%6.3f" % x)
        fields.append(" %4d" % iBin)
        if debug:
            fields.append(str([float("%6.3f" % y) for y in low_edges]))
            print "   ".join(fields)
        iBin -= 1

    low_edges.reverse()
    return low_edges
