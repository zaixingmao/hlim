#!/usr/bin/env python

import os
import sys
import ROOT as r


def merge(stems=None, inDir=None, outDir=None, hName=None, suffix=None):
    outFile = r.TFile("%s/src/auxiliaries/shapes/Brown/merged_%s.root" % (os.environ["CMSSW_BASE"], hName), "RECREATE")
    outFile.mkdir(outDir)

    for stem in stems:
        inFileName = inDir + stem + suffix
        inFile = r.TFile(inFileName)
        h1 = inFile.Get(hName)
        if not h1:
            sys.exit("%s:%s not found" % (inFileName, hName))

        proc = stem.replace("_all", "").replace("ZPrime_", "ggH")
        h = h1.Clone(proc)
        h.SetDirectory(0)
        inFile.Close()

        outFile.cd(outDir)
        h.Write()

    outFile.Close()


def m1(ch):
    stems = ["ZPrime_%d" % i for i in [500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500]]
    stems += ["QCD", "ZTT", "W", "VV", "TT"]
    d = "/home/elaird/CMSSW_7_1_5/src/hlim/%s_inclusive/%s_" % (ch, ch)
    merge(stems=stems, hName="m_effective", inDir=d, outDir="%s_inclusive" % ch, suffix=".root")


def m2():
    stems = ["ZPrime_%d_all" % i for i in [500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500]]
    stems += ["QCD_all", "ZTT", "W", "VV"]
    d = "/user_data/zmao/ZPrimeHistos/et/"
    hName = "m_withMET"
    merge(stems=stems, hName=hName, inDir=d, outDir="eleTau_inclusive", suffix="_%s.root" % hName)


if __name__ == "__main__":
    # m1("eleTau")
    # m1("emu")
    m2()
