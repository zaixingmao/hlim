#!/usr/bin/env python

import os
import sys
import ROOT as r
from h2bsm import xs_fb


def merge(stems=None, inDir=None, outDir=None, hName=None, suffix=None):
    outFile = r.TFile("%s/src/auxiliaries/shapes/Brown/merged_%s.root" % (os.environ["CMSSW_BASE"], hName), "RECREATE")
    outFile.mkdir(outDir)

    name_map = [("QCD_all", "QCD"),
                ("ZPrime_", "ggH"),
                ("ZprimeToTauTau_M_", "ggH"),
                ("Data", "data_obs"),
                ("Diboson", "VV"),
                ("TTBar", "TT"),
                ("WJets", "W"),
                ("ZJets", "ZTT"),

                ("Z.root", "ZTT.root"),
                ("eleTau_", ""),
                ]

    for stem in stems:
        inFileName = inDir + stem + suffix
        inFile = r.TFile(inFileName)
        h1 = inFile.Get(hName)
        if not h1:
            sys.exit("%s:%s not found" % (inFileName, hName))

        proc = stem
        for old, new in name_map:
            proc = proc.replace(old, new)

        h = h1.Clone(proc)
        h.SetDirectory(0)
        inFile.Close()

        if proc.startswith("ggH"):
            mass = int(proc.replace("ggH", ""))
            if xs_fb(mass):
                h.Scale(1000. / xs_fb(mass))  # some xs_fb --> 1 pb
            else:
                print proc, mass, "xs not found"

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


def ele():
    stems = ["eleTau_ZPrime_%d" % i for i in [500, 1000, 1500, 2000, 2500, 3000]]
    stems += ["eleTau_VV", "eleTau_QCD", "eleTau_TT", "eleTau_W", "eleTau_Z", "eleTau_data_obs"]
    d = "Fitter/eleTau_8TeVbins_900/"
    hName = "m_effective"
    merge(stems=stems, hName=hName, inDir=d, outDir="eleTau_inclusive", suffix=".root")


def mu():
    stems = ["ZprimeToTauTau_M_%d" % i for i in [500, 1000, 1500, 2000, 2500, 3000]]
    stems += ["Data", "Diboson", "QCD", "TTBar", "WJets", "ZJets"]
    d = "Fitter/"
    hName = "DiJetMass"
    merge(stems=stems, hName=hName, inDir=d, outDir="eleTau_inclusive", suffix="_muTauSR_ForFitter.root")


def had():
    stems = ["ZprimeToTauTau_M_%d" % i for i in [500, 1000, 1500, 2000, 2500, 3000]]
    stems += ["Data", "Diboson", "QCD", "TTBar", "WJets", "ZJets"]
    d = "Fitter/"
    hName = "DiJetMass"
    merge(stems=stems, hName=hName, inDir=d, outDir="eleTau_inclusive", suffix="_diTauSR_ForFitter.root")


if __name__ == "__main__":
    # m1("eleTau")
    # m1("emu")
    # m2()
    # mu()
    # ele()
    had()
