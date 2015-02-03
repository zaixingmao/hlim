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
