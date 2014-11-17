#!/usr/bin/env python

import math
import optparse
import os
import sys
import ROOT as r
import cfg


def inputFile():
    parser = optparse.OptionParser("usage: %prog xyz.root")
    options, args = parser.parse_args()
    if len(args) != 1 or not args[0].endswith(".root"):
        parser.print_help()
        exit()
    return args[0]


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


def isData(proc):
    return proc.startswith("data")


def isSignal(proc):
    for prefix in ["H2hh", "ggA", "bbH"]:
        if proc.startswith(prefix):
            return True
    return False


def isAntiIsoData(proc):
    return proc == "dataOSRelax"


def histos(fileName="", bins=None, procs=[], var="", rescaleX=False, cuts={}, category=""):
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
        w = "1.0" if isData(proc) else "triggerEff"
        cutString = '(sampleName=="%s")' % proc
        if category:
            cutString += ' && (Category=="%s")' % category

        for cutVar, (cutMin, cutMax) in sorted(cuts.iteritems()):
            if cutMin is not None:
                cutString += " && (%g < %s)" % (cutMin, cutVar)
            if cutMax is not None:
                cutString += " && (%s < %g)" % (cutVar, cutMax)

        tree.Draw("%s>>%s" % (var, proc), '(%s)*(%s)' % (w, cutString))
        h.SetDirectory(0)
        shift(h)
        out[proc] = h
        if isAntiIsoData(proc):
            applyLooseToTight(h, f, category)

    applySampleWeights(out, f)
    f.Close()
    return out


def applySampleWeights(hs={}, tfile=None):
    numer = tfile.Get("xs")
    denom = tfile.Get("initEvents")
    xNumer = numer.GetXaxis()
    xDenom = denom.GetXaxis()

    for proc, h in hs.iteritems():
        if isData(proc):
            continue

        for iBin in range(1, 1 + numer.GetNbinsX()):
            if xNumer.GetBinLabel(iBin) == proc:
                xs = numer.GetBinContent(iBin)
                if proc.startswith("H2hh"):
                    xs = 1.0e3 # 1 pb
                h.Scale(xs)
                h.GetZaxis().SetTitle("@ %g fb" % xs)
                #print proc, xs

        for iBin in range(1, 1 + denom.GetNbinsX()):
            if xDenom.GetBinLabel(iBin) == proc:
                content = denom.GetBinContent(iBin)
                assert content, "%s_%d" % (proc, iBin)
                h.Scale(1.0 / content)


def applyLooseToTight(h=None, tfile=None, category=""):
    hName = "L_to_T_%s" % category
    hFactor = tfile.Get(hName)
    if not hFactor:
        sys.exit("Could not find histogram '%s' in file '%s'." % (hName, tfile.GetName()))
    factor = hFactor.GetBinContent(1)
    h.Scale(factor)


def describe(h, l):
    print l, h.GetXaxis().GetTitle()
    headers = "bin       x         cont  +-   err    (   rel)"
    print l, headers
    print l, "-" * len(headers)
    for iBinX in range(1, 1 + h.GetNbinsX()):
        x = h.GetBinCenter(iBinX)
        c = h.GetBinContent(iBinX)
        e = h.GetBinError(iBinX)
        s = " %2d   %9.2e   %7.1e +- %7.1e" % (iBinX, x, c, e)
        if c:
            s += "  (%5.1f%s)" % (100.*e/c, "%")
        print l, s
    print l, "sum".ljust(12) + " = %9.3f" % h.Integral(0, 2 + h.GetNbinsX())
    print


def outFileName(sFactor, sKey, var, cuts):
    stem = cfg.root_dest + "/"
    mkdir(stem)

    if sFactor:
        stem += "%dx%s" % (sFactor, sKey.replace("H2hh", ""))
    stem += var
    if cfg.cutDesc(cuts):
        stem += "_%s" % cfg.cutDesc(cuts)
    return "%s.root" % stem


def printHeader(var, cuts):
    desc = "| %s;   %s |" % (var, str(cuts))
    h = "-" * len(desc)
    print h
    print desc
    print h


def printTag(tag, l):
    print
    s_tag = "* %s *" % tag
    a = "*" * len(s_tag)
    print l, a
    print l, s_tag
    print l, a


def go(inFile="", sFactor=None, sKey="", bins=None, var="", rescaleX=True,
       cuts=None, lumi=19.7, masses=[]):

    assert type(sFactor) is int, type(sFactor)
    assert bins
    assert var

    procs = {"tt_full": "TT",
             "tt_semi": "tt_semi",
             "ZZ": "VV",
             "W1JetsToLNu": "W",
             "W2JetsToLNu": "W2",
             "W3JetsToLNu": "W3",
             "DY1JetsToLL": "ZTT",
             "DY2JetsToLL": "DY2",
             "DY3JetsToLL": "DY3",
             "dataOSRelax": "QCD",
             }

    merge =  {"tt_full": ["tt_semi"],
              "DY1JetsToLL": ["DY2JetsToLL", "DY3JetsToLL"],
              "W1JetsToLNu": ["W2JetsToLNu", "W3JetsToLNu"],
              }

    fakeSigs = ["ggAToZhToLLTauTau", "ggAToZhToLLBB", "bbH"]
    print "FIXME: include", fakeSigs
    for m in masses:
        procs["H2hh%3d" % m] = "ggHTohhTo2Tau2B%3d" % m
        for stem in fakeSigs:
            sig = "%s%3d" % (stem, m)
            procs[sig] = sig

    print "FIXME: deal with 250"
    procs["bbH250"] = "bbH250"

    kargs = {"procs": procs.keys(),
             "bins": bins,
             "var": var,
             "cuts": cuts,
             "rescaleX": rescaleX,
             "fileName": inFile,
             }

    print "FIXME: include variations"
    printHeader(var, cuts)
    l = " " * 4

    f = r.TFile(outFileName(sFactor, sKey, var, cuts), "RECREATE")
    for category, tag in cfg.categories.iteritems():
        hs = histos(category=category, **kargs)
        printTag(tag, l)
        for target, sources in merge.iteritems():
            for source in sources:
                hs[target].Add(hs[source])
                del hs[source]
        f.mkdir(tag).cd()
        oneTag(tag, hs, procs, lumi, sKey, sFactor, l)
    f.Close()


def printIntegrals(lst=[], lumi=None, l=""):
    hyphens = "-" * 55
    print l, hyphens
    s = 0.0
    for tag, proc, integral in sorted(lst):
        s += integral
        print l, proc.ljust(30), "%9.3f" % integral, " (for %4.1f/fb)" % lumi
    print l, " ".ljust(25), "sum = %9.3f" % s
    print l, hyphens


def oneTag(tag, hs, procs, lumi, sKey, sFactor, l):
    integrals = []
    # scale and write
    for (proc, h) in hs.iteritems():
        if not isData(proc):
            h.Scale(lumi)
        #h.Print("all")
        if isSignal(proc) and "350" not in proc:
            pass
        else:
            integrals.append((tag, proc, h.Integral(0, 2 + h.GetNbinsX())))

        nom = procs[proc]
        h.Write(nom)
        # fake
        for var in ["Up", "Down"]:
            h.Write("%s_CMS_scale_t_tautau_8TeV%s" % (nom, var))

    printIntegrals(integrals, lumi, l)

    d = fakeDataset(hs, sKey, sFactor, l)
    d.Write()


def fakeDataset(hs, sKey, sFactor, l):
    d = None
    for key, histo in hs.iteritems():
        if isSignal(key):
            continue
        if d is None:
            d = histo.Clone("data_obs")
            d.Reset()
        d.Add(histo)

    describe(d, l)

    zTitle = "Observed = floor(sum(bkg)"  # missing ) added below
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

    return d


def loop(inFile=""):
    masses = cfg.masses_spin0
    for spec in cfg.variables():
        for mInj in masses[:1]:
            for sFactor in [0, 1, 2, 4][:1]:
                go(inFile=inFile,
                   sFactor=sFactor,
                   sKey="H2hh%3d" % mInj,
                   rescaleX=True,
                   masses=masses,
                   **spec)


if __name__ == "__main__":
    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = 2000

    loop(inFile=inputFile())
