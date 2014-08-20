#!/usr/bin/env python

import math
import ROOT as r


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


def histos(fileName="", bins=None, procs=[], var="", rescaleX=False, mJJMin=None, mJJMax=None):
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
        cut = 'sampleName=="%s"' % proc
        if mJJMin is not None:
            cut += " && (%g < mJJ)" % mJJMin
        if mJJMax is not None:
            cut += " && (mJJ < %g)" % mJJMax

        tree.Draw("%s>>%s" % (var, proc), '(%s)*(%s)' % (w, cut))
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
                    xs *= 1.0e3
                    if proc.endswith("260"):
                        xs *= 30. / 442.8
                    if proc.endswith("300"):
                        xs *= 30. / 477.
                    if proc.endswith("350"):
                        xs *= 30. / 257.1
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
       mJJMin=None, mJJMax=None, lumi=19.0):

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

    hs = histos(fileName=inFile, procs=procs.keys(), bins=bins, var=var, rescaleX=rescaleX,
                mJJMin=mJJMin, mJJMax=mJJMax)
    hs["tt_full"].Add(hs["tt_semi"])
    del hs["tt_semi"]

    if var == "BDT":
        tag = "bdt%s" % inFile.replace("combined_", "").replace(".root", "")
    else:
        tag = var

    f = r.TFile("htt_tt.inputs-Hhh-8TeV_%dx%s_%s_1pb.root" % (sFactor,
                                                              sKey.replace("H2hh", ""),
                                                              tag,
                                                              ), "RECREATE")
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


def loop(inFile="", bdt=None, other=None, wcut=None):
    if bdt:
        #for inFile, bins in [("combined_260.root", (4, -0.55, 0.25)),
        #                     ("combined_300.root", (4, -0.5, 0.3)),
        #                     ("combined_350.root", (4, -0.45, 0.35)),
        #                     #("combined_350.root", (5, -0.6, 0.4)),
        #                     ]:
        for var, bins in [("BDT_260", (4, -0.55, 0.25)),
                          ("BDT_300", (4, -0.5, 0.3)),
                          ("BDT_350", (4, -0.45, 0.35)),
                          ]:
            for sFactor in [0, 1, 2, 4][:1]:
                go(inFile=inFile,
                   sFactor=sFactor,
                   sKey="H2hh260",
                   bins=bins,
                   rescaleX=True,
                   var=var,
                   )
    if other:
        go(#inFile="various_vars.root",
           inFile=inFile,
           sFactor=0,
           sKey="H2hh260",
           bins=(15, 50.0, 200.0),
           rescaleX=True,
           var="svMass",
           #var="mJJReg",
           #var="mJJ",
           )

    if wcut:
        print "ERROR: modify file name"
        go(inFile=inFile,
           sFactor=0,
           sKey="H2hh260",
           bins=(15, 50.0, 200.0),
           rescaleX=True,
           var="svMass",
           #var="mJJReg",
           #var="mJJ",
           mJJMin=100.0,
           mJJMax=130.0,
           )
        

if __name__ == "__main__":
    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = 2000

    loop(inFile="combined.root",
         bdt=True,
         other=False,
         wcut=False,
         )
