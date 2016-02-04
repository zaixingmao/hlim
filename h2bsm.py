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


def burst_one(inFileName="", hNameOut="", blackList=["Up", "Down", "WAS_FLIPPED"]):
    fIn = r.TFile(inFileName)

    for key in fIn.GetListOfKeys():
        subdir = key.GetName()
        fIn.cd(subdir)
        mkdir(subdir)
        for key2 in r.gDirectory.GetListOfKeys():
            hName = key2.GetName()

            if any([hName.endswith(x) for x in blackList]):
                continue

            if hName in ["data_obs", "sum_b"]:
                continue
            h = fIn.Get("%s/%s" % (subdir, hName)).Clone(hNameOut)
            h.SetDirectory(0)

            proc = hName
            for old, new in [("ZTT", "Z"),
                             ("ggH", "ZPrime_"),
                             ]:
                proc = proc.replace(old, new)
                if proc != hName:
                    print "FIXME %s --> %s" % (hName, proc)

            if proc.startswith("ZPrime_"):
                mass = int(proc.split("_")[1])
                factor = xs_fb(mass)
                if factor:
                    h.Scale(factor / 1000.)  # 1 pb --> some xs_fb
                else:
                    print proc, mass, "xs not found"

            h.SetTitle(proc)
            ch = subdir.replace("_inclusive", "")

            fOut = r.TFile("%s/%s_%s.root" % (subdir, ch, proc), "RECREATE")
            fOut.cd()
            h.Write()
            fOut.Close()

    fIn.Close()


def xs_fb(m):
    return {500: 9330.0,
            1000:  468.0,
            1500:   72.3,
            2000:   17.3,
            2500:   5.54,
            3000:   1.29,
            3500:   0.49,
            4000:   0.255,
            4500:   0.17,
            }.get(m)


if __name__ == "__main__":

    for filename in ["htt_et.inputs-Zp-13TeV.root", "htt_em.inputs-Zp-13TeV.root"][:1]:
        full = "%s/src/auxiliaries/shapes/Brown/%s" % (os.environ["CMSSW_BASE"], filename)
        print full
        burst_one(inFileName=full, hNameOut="m_effective")
