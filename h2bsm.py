#!/usr/bin/env python

import os
import sys
import ROOT as r


def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != 17:
            raise e

if __name__ == "__main__":
    variable = "m_effective"
    fIn = r.TFile("%s/src/auxiliaries/shapes/Brown/%s.root" % (os.environ["CMSSW_BASE"], variable))

    for key in fIn.GetListOfKeys():
        subdir = key.GetName()
        fIn.cd(subdir)
        mkdir(subdir)
        for key2 in r.gDirectory.GetListOfKeys():
            hName = key2.GetName()
            if hName in ["data_obs", "sum_b"]:
                continue
            h = fIn.Get("%s/%s" % (subdir, hName)).Clone(variable)
            h.SetDirectory(0)
            
            proc = hName.replace("ggH", "ZPrime_")
            h.SetTitle(proc)
            ch = subdir.replace("_inclusive", "")
            fOut = r.TFile("%s/%s_%s.root" % (subdir, ch, proc), "RECREATE")
            fOut.cd()
            h.Write()
            fOut.Close()
