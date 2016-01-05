#!/usr/bin/env python

import os
import ROOT as r

for ch in ["et", "em"]:
    for m in range(500, 2500, 500):
        print ch, m
        cmd = "combine -M Asymptotic -m %d -n .Zprime.%s LIMITS/%s/%d/htt_%s_0_13TeV.txt > /dev/null" % (m, ch, ch, m, ch)
        # print cmd
        os.system(cmd)
        f = r.TFile("higgsCombine.Zprime.%s.Asymptotic.mH%d.root" % (ch, m))
        tree = f.Get("limit")
        tree.Scan("mh:limit:quantileExpected", "quantileExpected > 0.0")
        f.Close()
