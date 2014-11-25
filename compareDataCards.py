#!/usr/bin/env python

import ROOT as r
import collections
import os
import sys


def fetchOneDir(f, subdir):
    out = {}
    for key in r.gDirectory.GetListOfKeys():
        name = key.GetName()
        if name.endswith("8TeVUp") or name.endswith("8TeVDown"):
            continue
        h = f.Get("%s/%s" % (subdir, name)).Clone()
        h.SetDirectory(0)
        normalize(h)
        out[name] = h
    return out


def histograms(fileName=""):
    f = r.TFile("%s/src/auxiliaries/shapes/%s" % (os.environ["CMSSW_BASE"], fileName))
    if f.IsZombie():
        sys.exit("'%s' is a zombie." % fileName)

    out = {}
    for key in f.GetListOfKeys():
        name = key.GetName()
        f.cd(name)
        out[name] = fetchOneDir(f, name)
    f.Close()
    return out


def normalize(h):
    for iBin in range(1, 1 + h.GetNbinsX()):
        h.SetBinContent(iBin, h.GetBinContent(iBin) / h.GetBinWidth(iBin))
        h.SetBinError(iBin, h.GetBinError(iBin) / h.GetBinWidth(iBin))


def common_keys(d1, d2):
    keys1 = d1.keys()
    keys2 = d2.keys()

    m1 = []
    m2 = []
    common = []
    for key in set(keys1 + keys2):
        if key not in keys1:
            m1.append(key)
        elif key not in keys2:
            m2.append(key)
        else:
            common.append(key)
    return common, m1, m2


def moveStatsBox(h):
    h.SetStats(True)
    r.gPad.Update()
    tps = h.FindObject("stats")
    if tps:
        tps.SetTextColor(h.GetLineColor())
        tps.SetX1NDC(0.86)
        tps.SetX2NDC(1.00)
        tps.SetY1NDC(0.70)
        tps.SetY2NDC(1.00)
    return tps


def integral(h):
    out = h.Integral(1, h.GetNbinsX(), "width")
    for bin in [0, 1 + h.GetNbinsX()]:
        out += h.Integral(bin, bin)
    return out


def oneDir(canvas, pdf, hNames, d1, d2, subdir, xTitle):
    keep = []
    for i, hName in enumerate(whiteList):
        if not hName:
            continue

        j = i % 4
        if j == 0:
            canvas.cd(0)
            canvas.Clear()
            canvas.Divide(2, 2)

        if hName in hNames:
            hNames.remove(hName)
        else:
            print "ERROR: %s not found" % hName

        h1 = d1[subdir][hName]
        h2 = d2[subdir][hName]

        canvas.cd(1 + j)
        r.gPad.SetTickx()
        r.gPad.SetTicky()
            
        h1.SetLineColor(r.kBlack)
        i1 = integral(h1)
        i2 = integral(h2)

        title = hName
        title += "  (#color[1]{%.2f},  #color[4]{%.2f})" % (i1, i2)
        h1.SetTitle("%s / %s;%s;events / GeV" % (subdir, title, xTitle))

        h1.SetMinimum(0.0)
        # h1.SetMaximum(1.2 * max([h1.GetMaximum(), h2.GetMaximum()]))

        # h1.SetMarkerStyle(8)
        # h1.SetMarkerSize(0.6)
        # h1.SetLineWidth(2)
        # h1.SetMarkerColor(1)
        # h1.SetLineColor(1)
        # h1.SetLineStyle(1)
        # h1.SetFillColor(0)
        # h1.Draw("hist")
        h1.Draw()
        #keep.append(moveStatsBox(h1))

        # h4 = h1.Clone()
        # h4.SetLineWidth(0)
        # h4.SetFillColor(r.kGray)
        # h4.SetFillStyle(3344)
        # h4.Draw("e2same")

        # h2.SetMarkerStyle(8)
        # h2.SetMarkerSize(0.6)
        # h2.SetMarkerColor(4)
        # h2.SetLineWidth(2)
        # h2.SetLineStyle(1)
        # h2.SetLineColor(4)
        # h2.SetFillColor(0)
        # h2.Draw("hist e same")

        h2.SetLineColor(r.kBlue)
        h2.Draw("same")
        #keep.append(moveStatsBox(h2))

        if j == 3 or i == (len(whiteList) - 1):
            canvas.cd(0)
            canvas.Print(pdf)

    report([(hNames, "Skipping")])


def tryNums(m, h):
    num = None
    for i in range(-4, -1):
        try:
            num = int(h[i:])
            key = h[:i]
            m[key].append(num)
            break
        except ValueError, e:
            continue
    return num


def report(l=[]):
    for (hs, message) in l:
        if not hs:
            continue

        m = collections.defaultdict(list)
        for h in sorted(hs):
            if tryNums(m, h) is None:
                pass

        print message
        singles = []
        for key, lst in sorted(m.iteritems()):
            if not key:
                singles += lst
            elif len(lst) == 1:
                singles.append(key+str(lst[0]))
            else:
                print key, sorted(lst)

        if singles:
            print sorted(singles)
        print


if __name__ == "__main__":
    "Italians/htt_tt.inputs-Hhh-8TeV_m_ttbb_kinfit_only_massCut"
    "Italians/htt_tt.inputs-Hhh-8TeV_m_bb_slice.root"
    
    "Italians/htt_tt.inputs-Hhh-8TeV_m_ttbb_kinfit_massCut.root"
    "Italians/htt_tt.inputs-Hhh-8TeV_m_ttbb_kinfit_only.root"
    "Brown/fMassKinFit_0.0.fMassKinFit.root"
    "Brown/fMassKinFit_0.0.fMassKinFit_70.0.mJJ.150.0_90.0.svMass.150.0.root"

    xTitle, file1, file2  = ("svMass (preselection)",
                             "Italians/htt_tt.inputs-Hhh-8TeV_m_sv.root",
                             "Brown/svMass.root")

    #xTitle, file1, file2  = ("fMassKinFit (after cuts)",
    #                         "Italians/htt_tt.inputs-Hhh-8TeV_m_ttbb_kinfit_massCut.root",
    #                         "Brown/fMassKinFit_0.0.fMassKinFit_70.0.mJJ.150.0_90.0.svMass.150.0.root",
    #                         )

    ignorePrefixes = ["ggAToZh", "bbH", "W", "data_obs", "ggRadion", "ggGraviton"]

    whiteList = ["TT", "QCD", "VV", "ZTT",
                 "ggHTohhTo2Tau2B260", "ggHTohhTo2Tau2B300", "ggHTohhTo2Tau2B350",
                 ]

    r.gErrorIgnoreLevel = 2000
    r.gStyle.SetOptStat("rme")
    r.gROOT.SetBatch(True)
    d1 = histograms(file1)
    d2 = histograms(file2)

    subdirs, m1, m2 = common_keys(d1, d2)
    if m1:
        print "directories missing from '%s':" % file1, m1
    if m2:
        print "directories missing from '%s':" % file2, m2

    pdf = "comparison.pdf"
    canvas = r.TCanvas()
    canvas.Print(pdf + "[")

    for subdir in reversed(subdirs):
        hNames, h1, h2 = common_keys(d1[subdir], d2[subdir])
        report([(h1, 'histograms missing from %s/%s:' % (file1, subdir)),
                (h2, 'histograms missing from %s/%s:' % (file2, subdir)),
                ])

        hNames = filter(lambda hName: not any([hName.startswith(x) for x in ignorePrefixes]), hNames)
        oneDir(canvas, pdf, hNames, d1, d2, subdir, xTitle)

    canvas.Print(pdf + "]")
