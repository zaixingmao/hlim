#!/usr/bin/env python

import math
import os
import ROOT as r


def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != 17:
            raise e


def combineBinContentAndError(h, binToContainCombo, binToBeKilled):
    c = h.GetBinContent(binToContainCombo) + h.GetBinContent(binToBeKilled)
    e = h.GetBinError(binToContainCombo)**2 + h.GetBinError(binToBeKilled)**2
    e = e**0.5

    h.SetBinContent(binToBeKilled, 0.0)
    h.SetBinContent(binToContainCombo, c)

    h.SetBinError(binToBeKilled, 0.0)
    h.SetBinError(binToContainCombo, e)


def shift(h):
    n = h.GetNbinsX()
    combineBinContentAndError(h, n, n+1)  # overflows
    combineBinContentAndError(h, 1, 0)  # underflows


def histos(fileName="", bins=None, procs=[], var="", rescaleX=False, cut=None):
    assert fileName
    assert bins

    # rescale so that bin width is 1.0
    if rescaleX:
        assert bins[0]
        binWidth = (bins[2] - bins[1]) / bins[0]
        assert binWidth
        factor = 1.0 / binWidth
        bins = (bins[0], bins[1] * factor, bins[2] * factor)
        var = "(%g*%s)" % (factor, var)

    f = r.TFile(fileName)
    tree = f.Get("eventTree")
    out = {}

    for proc in procs:
        h = r.TH1D(proc, proc+";%s;events / bin" % var, *bins)
        h.Sumw2()
        w = "1.0" if proc.startswith("data") else "triggerEff"
        cutString = 'sampleName=="%s"' % proc
        if cut:
            assert len(cut) == 3, cut
            cutVar, cutMin, cutMax = cut
            if cutMin is not None:
                cutString += " && (%g < %s)" % (cutMin, cutVar)
            if cutMax is not None:
                cutString += " && (%s < %g)" % (cutVar, cutMax)

        tree.Draw("%s>>%s" % (var, proc), '(%s)*(%s)' % (w, cutString))
        h.SetDirectory(0)
        shift(h)
        out[proc] = h

    applySampleWeights(out, f)
    f.Close()
    return out


def applySampleWeights(hs={}, tfile=None):
    numer = tfile.Get("xs")
    denom = tfile.Get("initEvents")
    xNumer = numer.GetXaxis()
    xDenom = denom.GetXaxis()

    for proc, h in hs.iteritems():
        for iBin in range(1, 1 + numer.GetNbinsX()):
            if xNumer.GetBinLabel(iBin) == proc:
                xs = numer.GetBinContent(iBin)

                #fake signal xs
                if proc.startswith("H2hh"):
                    #xs *= 1.0e3
                    #if proc.endswith("260"):
                    #    xs *= 30. / 442.8
                    #if proc.endswith("300"):
                    #    xs *= 30. / 477.
                    #if proc.endswith("350"):
                    #    xs *= 30. / 257.1
                    xs = 1.0e3 # 1 pb
                h.Scale(xs)
                h.GetZaxis().SetTitle("@ %g fb" % xs)
                #print proc, xs

        for iBin in range(1, 1 + denom.GetNbinsX()):
            if xDenom.GetBinLabel(iBin) == proc:
                content = denom.GetBinContent(iBin)
                assert content, "%s_%d" % (proc, iBin)
                h.Scale(1.0 / content)


def describe(h):
    print h.GetXaxis().GetTitle()
    headers = "bin       x         cont  +-   err    (   rel)"
    print headers
    print "-" * len(headers)
    for iBinX in range(1, 1 + h.GetNbinsX()):
        x = h.GetBinCenter(iBinX)
        c = h.GetBinContent(iBinX)
        e = h.GetBinError(iBinX)
        s = " %2d   %9.2e   %7.1e +- %7.1e" % (iBinX, x, c, e)
        if c:
            s += "  (%5.1f%s)" % (100.*e/c, "%")
        print s
    print

def go(inFile="", sFactor=None, sKey="", bins=None, var="", rescaleX=True,
       cut=None, lumi=19.0):

    assert type(sFactor) is int, type(sFactor)
    assert bins
    assert var

    procs = {"H2hh260": "ggHTohh260",
             "H2hh300": "ggHTohh300",
             "H2hh350": "ggHTohh350",
             "tt_full": "TT",
             "tt_semi": "tt_semi",
             "ZZ": "VV",
             "dataOSRelax": "QCD",
             }

    hs = histos(fileName=inFile, procs=procs.keys(), bins=bins, var=var,
                rescaleX=rescaleX, cut=cut)

    hs["tt_full"].Add(hs["tt_semi"])
    del hs["tt_semi"]

    dir = "root"
    mkdir(dir)
    fileName = "%s/%dx%s_%s" % (dir, sFactor, sKey.replace("H2hh", ""), var)
    if cut:
        cutDesc = cut[0]
        if cut[1] is not None:
            cutDesc = "%d.%s" % (cut[1], cutDesc)
        if cut[2] is not None:
            cutDesc = "%s.%d" % (cutDesc, cut[2])
        fileName += "_%s" % cutDesc

    f = r.TFile("%s.root" % fileName, "RECREATE")
    f.mkdir("tauTau_2jet2tag").cd()

    # scale and write
    for (proc, h) in hs.iteritems():
        if not proc.startswith("data"):
            h.Scale(lumi)
        #h.Print("all")
        h.Write(procs[proc])

    #print "OSRelax:"
    #hs["dataOSRelax"].Print("all")

    # make a fake dataset
    d = hs["tt_full"].Clone("data_obs")
    d.Add(hs["ZZ"])
    d.Add(hs["dataOSRelax"])

    describe(d)
    zTitle = "Observed (=  <bkg>"
    if sFactor:
        d.Add(hs[sKey], sFactor)
        if sFactor != 1:
            zTitle += " + %d#times" % sFactor
        else:
            zTitle += " + "
        zTitle += "%s %s)" % (sKey.replace("2hh", ""), hs[sKey].GetZaxis().GetTitle())
    else:
        zTitle += ")"

    d.GetZaxis().SetTitle(zTitle)


    # integerize
    for iBin in range(1, 1 + d.GetNbinsX()):
        c = math.floor(d.GetBinContent(iBin))
        d.SetBinContent(iBin, c)
        d.SetBinError(iBin, math.sqrt(max(0.0, c)))

    #d.Print("all")
    d.Write()

    f.Close()


def loop(inFile="", specs={}):
    for spec in specs:
        for mInj in [260, 300, 350][:1]:
            for sFactor in [0, 1, 2, 4][:1]:
                go(inFile=inFile,
                   sFactor=sFactor,
                   sKey="H2hh%3d" % mInj,
                   rescaleX=True,
                   **spec)


if __name__ == "__main__":
    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = 2000

    loop(inFile="combined.root",
         specs=[{"var": "BDT_260", "bins": ( 4, -0.55, 0.25), "cut": []},
                {"var": "BDT_300", "bins": ( 4, -0.50, 0.30), "cut": []},
                {"var": "BDT_350", "bins": ( 4, -0.45, 0.35), "cut": []},
                {"var": "svMass",  "bins": (15, 50.0, 200.0), "cut": []},
                {"var": "svMass",  "bins": (15, 50.0, 200.0), "cut": ("mJJ", 90.0, 140.0)},
                #{"var": "mJJReg",  "bins": (15, 50.0, 200.0), "cut": []},
                {"var": "mJJ",     "bins": (15, 50.0, 200.0), "cut": []},
                ],
         )
