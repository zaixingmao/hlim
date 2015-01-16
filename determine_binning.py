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

        if s and math.sqrt(e2)/s < threshold:
            # print iBinX, s, math.sqrt(e2), math.sqrt(e2)/s
            break
    return iBinX


def binning(h, width, xn_l, x1_r):
    if xn_l <= x1_r:
        return (1, h.GetXaxis().GetXmin(), h.GetXaxis().GetXmax())
    
    nbins = 1 + int((xn_l - x1_r) / width)
    return (1 + nbins, xn_l - nbins * width, xn_l + width)
            

def bins(width=0.1, threshold_r=0.4, threshold_l=0.2):
    vars = cfg.variables()
    assert len(vars) == 1
    d = vars[0]
    fileName = cfg.outFileName(var=d["var"], cuts=d["cuts"])

    h = histo(fileName, subdir="tauTau_2jet2tag", name="sum_b")

    iBin = bin_search(h, rargs=(1 + h.GetNbinsX(), 0, -1), threshold=threshold_r)
    xn_l = h.GetBinLowEdge(iBin)

    iBin = bin_search(h, rargs=(0, 2 + h.GetNbinsX()), threshold=threshold_l)
    x1_r = h.GetBinLowEdge(1 + iBin)

    return binning(h, width, xn_l, x1_r)


if __name__ == "__main__":
    print '"bins": (%s, %g, %g)' % bins()
