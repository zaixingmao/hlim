#!/usr/bin/env python

import os
import sys
import ROOT as r
from h2bsm import xs_fb


def scale_one(inFileName=""):
    fIn = r.TFile(inFileName, "UPDATE")

    for key in fIn.GetListOfKeys():
        subdir = key.GetName()
        fIn.cd(subdir)
        for key2 in r.gDirectory.GetListOfKeys():
            hName = key2.GetName()
            if not hName.startswith("ggH"):
                continue

            h = fIn.Get("%s/%s" % (subdir, hName))

            if "_" in hName:
                mass = int(hName[3:hName.find("_")])
            else:
                mass = int(hName[3:])

            factor = xs_fb(mass)
            if factor:
                h.Scale(factor / 1000.)  # 1 pb --> some xs_fb
            else:
                print "xs not found for %s/%d: NOT SCALING!" % (hName, mass)

            h.Write()
    fIn.Close()


if __name__ == "__main__":

    for filename in ["htt_et.inputs-Zp-13TeV.root", "htt_em.inputs-Zp-13TeV.root"]:
        full = "%s/src/auxiliaries/shapes/Brown/%s" % (os.environ["CMSSW_BASE"], filename)
        full2 = full + "2"
        os.system("cp -p %s %s" % (full, full2))
        print full
        print full2
        scale_one(inFileName=full2)
