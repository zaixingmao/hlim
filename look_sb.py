#!/usr/bin/env python

import os
import sys
import math
import cfg
import ROOT as r


if __name__ == "__main__":
    fIn = r.TFile(sys.argv[1])

    for key in fIn.GetListOfKeys():
        subdir = key.GetName()
        fIn.cd(subdir)
        hb = fIn.Get("%s/sum_b" % subdir)
        signals = []
        for key2 in r.gDirectory.GetListOfKeys():
            hName = key2.GetName()
            if cfg.isSignal(hName) and not cfg.isVariation(hName):
                signals.append(hName)

        print subdir
        header = "%10s  %3s  %7s   %7s" % ("signal", "bin", "s/sqrt(b)", "xs @ s/sqrt(b)=2")
        print header
        print "-" * len(header)
        for signal in sorted(signals):
            hs = fIn.Get("%s/%s" % (subdir, signal))
            xMax = -999.9
            i = None
            for iBin in range(1, 1 + hs.GetNbinsX()):
                s = hs.GetBinContent(iBin)
                b = hb.GetBinContent(iBin)
                if 0.0 < b:
                    x = s / math.sqrt(b)
                    if xMax < x:
                        xMax = x
                        i = iBin
                        # print "%3d  %g  %g  %g  %g" % (i, s, b, math.sqrt(b), s / math.sqrt(b))
            print "%10s  %3d  %g     %g" % (signal, i, xMax, 2.0 / xMax)
    fIn.Close()
