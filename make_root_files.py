#!/usr/bin/env python

import array
import collections
import math
import optparse
import os
import sys

import cfg
from compareDataCards import report


def error(msg="", die=True):
    s = "\033[%s%s\033[0m" % ("91m" if die else "35m", "ERROR: ")
    s += msg
    if die:
        sys.exit(s)
    else:
        print s


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


def merge_second_layer(d, f, variable, category, variation):
    for destProc, srcProcs in cfg.procs2(variable, category).iteritems():
        destProc += variation

        for srcProc in srcProcs:
            key = srcProc + variation
            h = d[key]

            if destProc not in d:
                d[destProc] = h.Clone(destProc)
                d[destProc].SetDirectory(0)
                d[destProc].Reset()

            if srcProc[0] == "*" and category != '0M':
                applyFactor(h, f, hName="%s_%s" % (srcProc[1:], category), unit=True)
                if variation:
                    print "FIXME: check varied factors"

            d[destProc].Add(h)
            del d[key]


def rescaled_bins(bins, variable):
    if type(bins) is not tuple:
        error("cannot rescale X for non-uniform binning (%s)." % variable)

    assert bins[0]
    binWidth = (bins[2] - bins[1]) / bins[0]
    assert binWidth
    factor = 1.0 / binWidth
    bins = (bins[0], bins[1] * factor, bins[2] * factor)
    variable = "(%g*%s)" % (factor, variable)
    return bins, variable


def histos(bins=None, variable="", cuts={}, category=""):
    assert bins

    # rescale so that bin width is 1.0
    if cfg.rescaleX:
        bins, variable = rescaled_bins(bins, variable)

    procs = cfg.procs(variable, category)

    out = {}
    for variation, fileName in cfg.files(variable).iteritems():
        f = r.TFile(fileName)
        tree = f.Get("eventTree")
        checkSamples(tree, fileName, variable, category)

        # first layer of merging
        for destProc, srcProcs in procs.iteritems():
            if destProc == "data_obs" and not options.unblind:
                continue

            destProc += variation

            for srcProc, h in histosOneFile(f, tree, bins, srcProcs, variable, cuts, category).iteritems():
                if destProc not in out:
                    out[destProc] = h.Clone(destProc)
                    out[destProc].SetDirectory(0)
                    out[destProc].Reset()
                factor = -1.0 if srcProc[0] == "-" else 1.0
                out[destProc].Add(h, factor)

        applyFactor(out["QCD" + variation], f, hName="L_to_T_SF_%s" % category, unit=False)

        if any(["embed" in src for src in procs.get("ZTT", [])]):
           applyFactor(out["ZTT" + variation], f, hName="MC2Embed2Cat_%s" % category, unit=(category != '0M'))

        merge_second_layer(out, f, variable, category, variation)
        f.Close()
    return out


def histosOneFile(f, tree, bins, procs, variable, cuts, category):
    if type(bins) is list:
        a = array.array('d', bins)
        bins = (len(a) - 1, a)

    out = {}
    for proc_orig in procs:
        if proc_orig and proc_orig[0] == "-":
            proc = proc_orig[1:]
        else:
            proc = proc_orig

        h = r.TH1D(proc, proc+";%s;events / bin" % variable, *bins)
        h.Sumw2()

        if cfg.isData(proc):
            w = "(1.0)"
        elif cfg.isDataEmbedded(proc):
            w = "(triggerEff*embeddedWeight*decayModeWeight)"
        elif cfg.isMcEmbedded(proc):
            w = "(%g*triggerEff*PUWeight*embeddedWeight*xs/initEvents)" % cfg.lumi
        elif cfg.isSignal(proc):
            w = "(%g*triggerEff*xs*PUWeight*decayModeWeight/initEvents)" % cfg.lumi
        else:
            w = "(%g*triggerEff*xs*PUWeight/initEvents)" % cfg.lumi

        cutString = '(sampleName=="%s")' % proc
        if category:
            cutString += ' && (Category=="%s")' % category

        for cutVar, (cutMin, cutMax) in sorted(cuts.iteritems()):
            if cutMin is not None:
                cutString += " && (%g < %s)" % (cutMin, cutVar)
            if cutMax is not None:
                cutString += " && (%s < %g)" % (cutVar, cutMax)

        tree.Draw("%s>>%s" % (variable, proc), '(%s)*(%s)' % (w, cutString))
        h.SetDirectory(0)
        if options.shift:
            shift(h)

        out[proc_orig] = h
    return out


def printSampleInfo(xs, ini):
    n = max([len(x) for x in xs.keys()])
    header = "      ".join(["sample".ljust(n),
                            "xs (fb)",
                            "#eventsAOD",
                            "lumi_MC (/fb)",
                            ])
    print header + "  (before weight)"
    print "-" * len(header)
    for key, xsValues in sorted(xs.iteritems()):
        for x in xsValues:
            continue
        for nEvents in ini[key]:
            continue
        fields = [key.ljust(n)]
        if not cfg.isData(key):
            fields += ["%8.0f" % x,
                       " %12.0f" % nEvents,
                       "       %7.1f" % (nEvents / x),
                       ]
        print "    ".join(fields)
    print "-" * len(header)


def checkSamples(tree, fileName=".root file", variable="", category=""):
    xs = collections.defaultdict(set)
    ini = collections.defaultdict(set)

    for iEntry in range(tree.GetEntries()):
        tree.GetEntry(iEntry)
        sn = tree.sampleName
        sn = sn[:sn.find("\x00")]
        xs[sn].add(tree.xs)
        ini[sn].add(tree.initEvents)

        if options.allowMultiXs:
            continue

        if len(xs[sn]) != 1:
            error("sample %s (file %s) has multiple values of xs: %s" % (sn, fileName, xs[sn]))
        if len(ini[sn]) != 1:
            error("sample %s (file %s) has multiple values of ini: %s" % (sn, fileName, ini[sn]))

    if options.xs:
        printSampleInfo(xs, ini)

    extra = []
    for proc in sum(cfg.procs(variable, category).values(), []):
        if proc and proc[0] == "-":
            proc = proc[1:]
        if proc in cfg.fakeSignalList():
            continue  # warning is done in cfg.complain()
        if proc in xs:
            del xs[proc]
        else:
            extra.append(proc)

    report([(xs.keys(), "Samples in %s but not procs():" % fileName),
            (extra, "Samples in procs() but not %s:" % fileName),
            ])


def applyFactor(h=None, tfile=None, hName="", unit=False):
    if unit:
        i = h.Integral(0, 1 + h.GetNbinsX())  # fixme: under/overflows?
        if not i:
            error("Empty histogram '%s'." % h.GetName(), die=False)
        else:
            h.Scale(1.0 / i)

    hFactor = tfile.Get(hName)
    if not hFactor:
        error("Could not find histogram '%s' in file '%s'." % (hName, tfile.GetName()))
    factor = hFactor.GetBinContent(1)
    if options.factors:
        print "%s: %8.6f" % (hName, factor)
    h.Scale(factor)


def describe(h, l, keys):
    print l, h.GetXaxis().GetTitle(), "(sum of %s)" % str(keys)
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


def go(sFactor=None, sKey="", bins=None, var="", cuts=None):
    assert var
    printHeader(var, cuts)

    l = " " * 4

    oArgs = {"sFactor": sFactor,
             "sKey": sKey,
             "var": var,
             "cuts": cuts,
             }
    f = r.TFile(cfg.outFileName(**oArgs), "RECREATE")
    for category, tag in cfg.categories.iteritems():
        hs = histos(category=category, bins=bins, variable=var, cuts=cuts)
        if options.integrals or options.xs or options.contents:
            printTag(tag, l)
        f.mkdir(tag).cd()
        oneTag(tag, hs, sKey, sFactor, l)
    f.Close()


def printIntegrals(lst=[], l=""):
    hyphens = "-" * 55
    print l, hyphens
    s = 0.0
    for tag, proc, integral in sorted(lst):
        s += integral
        print l, proc.ljust(30), "%9.3f" % integral, " (for %4.1f/fb)" % cfg.lumi
    print l, " ".ljust(25), "sum = %9.3f" % s
    print l, hyphens


def oneTag(tag, hs, sKey, sFactor, l):
    integrals = []
    # scale and write
    for (proc, h) in hs.iteritems():
        if not h:
            print "ERROR: %s" % proc, h
            continue

        #h.Print("all")
        if cfg.isSignal(proc) and cfg.substring_signal_example not in proc:
            pass
        elif proc.endswith("Down") or proc.endswith("Up"):
            pass
        else:
            integrals.append((tag, proc, h.Integral(0, 2 + h.GetNbinsX())))
        h.Write()

    if options.integrals:
        printIntegrals(integrals, l)

    if not options.unblind:
        fakeDataset(hs, sKey, sFactor, l).Write()

    if options.sumb:
        h, keys = sumb(hs)
        h.Write()
        if options.contents and options.unblind:
            describe(h, l, keys)


def sumb(hs, name="sum_b"):
    d = None
    keys = []
    for key, histo in hs.iteritems():
        if cfg.isSignal(key):
            continue
        if key.endswith("8TeVUp") or key.endswith("8TeVDown"):
            continue

        if d is None:
            d = histo.Clone(name)
            d.SetTitle(name)
            d.Reset()
        d.Add(histo)
        keys.append(key)
    return d, keys


def fakeDataset(hs, sKey, sFactor, l):
    assert type(sFactor) is int, type(sFactor)

    d, keys = sumb(hs, name="data_obs")
    if options.contents:
        describe(d, l, keys)

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


def opts():
    parser = optparse.OptionParser()

    parser.add_option("--contents",
                      dest="contents",
                      default=False,
                      action="store_true",
                      help="print bin contents")

    parser.add_option("--xs",
                      dest="xs",
                      default=False,
                      action="store_true",
                      help="print xs table")

    parser.add_option("--integrals",
                      dest="integrals",
                      default=False,
                      action="store_true",
                      help="print integrals")

    parser.add_option("--factors",
                      dest="factors",
                      default=False,
                      action="store_true",
                      help="print loose-to-tight and embedded-sample rate factors")

    parser.add_option("--shift",
                      dest="shift",
                      default=False,
                      action="store_true",
                      help="shift under- and over-flows into visible bins")

    parser.add_option("--allow-multi-xs",
                      dest="allowMultiXs",
                      default=False,
                      action="store_true",
                      help="skip check of uniqueness of xs for each process name")

    parser.add_option("--unblind",
                      dest="unblind",
                      default=False,
                      action="store_true",
                      help="use real data for data_obs rather than floor(sum(b))")

    parser.add_option("--sum-b",
                      dest="sumb",
                      default=False,
                      action="store_true",
                      help="store sum of all backgrounds (useful for choosing binning)")

    options, args = parser.parse_args()
    return options


options = opts()
import ROOT as r  # placed after opts so as not to steal --help
r.gROOT.SetBatch(True)
r.gErrorIgnoreLevel = 2000

if __name__ == "__main__":
    go(**cfg.variable())
else:
    for item in ["allowMultiXs", "integrals", "unblind", "sumb", "shift"]:
        setattr(options, item, True)
