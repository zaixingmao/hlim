#!/usr/bin/env python

import os
import sys
import ROOT as r
from xs import xs_pb


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

            factor = xs_pb(mass)
            if factor:
                h.Scale(factor)  # 1 pb --> some xs_pb
            else:
                print "xs not found for %s/%d: NOT SCALING!" % (hName, mass)

            h.Write()
    fIn.Close()


def go():
    subdir = ["Brown", "Zp_1pb"][1]
    for ch in ["et", "em", "mt", "tt"][:2]:
        full = "%s/src/auxiliaries/shapes/%s/htt_%s.inputs-Zp-13TeV.root" % (os.environ["CMSSW_BASE"], subdir, ch)
        full2 = full.replace("/%s/" % subdir, "/Zp_nominal/")
        os.system("cp -p %s %s" % (full, full2))
        print full
        print full2
        scale_one(inFileName=full2)


if __name__ == "__main__":
    go()
