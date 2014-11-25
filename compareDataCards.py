#!/usr/bin/env python

import ROOT as r
import collections
import os
import sys


def fetchOneDir(f, subdir):
    out = {}
    for key in r.gDirectory.GetListOfKeys():
        name = key.GetName()
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


def band(u, d):
    ux = u.GetXaxis()
    dx = d.GetXaxis()
    for func in ["GetNbins", "GetXmin", "GetXmax"]:
        if getattr(ux, func)() != getattr(dx, func)():
            sys.exit("Binning (%s) check failed for %s, %s" % (func, u.GetName(), d.GetName()))

    out = u.Clone()
    out.Reset()
    for i in range(1, 1 + out.GetNbinsX()):
        c1 = u.GetBinContent(i)
        c2 = d.GetBinContent(i)
        out.SetBinContent(i, (c1 + c2) / 2.0)
        error = abs(c1 - c2) / 2.0
        out.SetBinError(i, max(0.00001, error))
    return out


def maximum(l=[]):
    out = None
    for h in l:
        for i in range(1, 1 + h.GetNbinsX()):
            value = h.GetBinContent(i) + h.GetBinError(i)
            if (out is None) or (out < value):
                out = value
    return out


def ls(h, s=""):
    return "#color[%d]{%s  %.2f}" % (h.GetLineColor(), s, integral(h))


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
        h1u = d1[subdir]["%s_CMS_scale_t_tautau_8TeVUp" % hName]
        h1d = d1[subdir]["%s_CMS_scale_t_tautau_8TeVDown" % hName]
        h1b = band(h1u, h1d)
        keep.append(h1b)

        h2 = d2[subdir][hName]
        h2u = d2[subdir]["%s_CMS_scale_t_tautau_8TeVUp" % hName]
        h2d = d2[subdir]["%s_CMS_scale_t_tautau_8TeVDown" % hName]
        h2b = band(h2u, h2d)
        keep.append(h2b)

        canvas.cd(1 + j)
        r.gPad.SetTickx()
        r.gPad.SetTicky()
            
        h1b.SetTitle("%s / %s;%s;events / GeV" % (subdir, hName, xTitle))
        h1b.SetMinimum(0.0)

        h1b.SetMaximum(1.1 * maximum([h1, h1u, h1d, h2, h2u, h2d]))
        h1b.SetStats(False)
        h1b.GetYaxis().SetTitleOffset(1.25)

        h1b.SetMarkerColor(r.kWhite)
        h1b.SetLineColor(r.kGray)
        h1b.SetFillColor(r.kGray)
        h1b.SetFillStyle(3354)
        h1b.Draw("e2")

        h1d.SetLineColor(r.kWhite)
        h1d.Draw("histsame")

        h1u.SetLineColor(r.kGray)
        h1u.Draw("histsame")

        h1.SetLineColor(r.kBlack)
        h1.SetMarkerColor(r.kBlack)
        h1.Draw("ehistsame")
        #keep.append(moveStatsBox(h1))

        h2b.SetMarkerColor(r.kWhite)
        h2b.SetLineColor(r.kCyan)
        h2b.SetFillColor(r.kCyan)
        h2b.SetFillStyle(3345)
        h2b.Draw("e2same")

        h2d.SetLineColor(r.kWhite)
        h2d.Draw("histsame")

        h2u.SetLineColor(r.kCyan)
        h2u.Draw("histsame")

        h2.SetLineColor(r.kBlue)
        h2.SetMarkerColor(r.kBlue)
        h2.Draw("ehistsame")
        #keep.append(moveStatsBox(h2))

        leg = r.TLegend(0.7, 0.6, 0.87, 0.87)
        leg.SetBorderSize(0)
        leg.SetFillStyle(0)

        #leg.AddEntry(h1b, "band", "f")
        leg.AddEntry(h1u, ls(h1u, "up"), "l")
        leg.AddEntry(h1d, ls(h1d, "down"), "l")
        leg.AddEntry(h1, ls(h1, "nominal"), "le")

        #leg.AddEntry(h2b, "band", "f")
        leg.AddEntry(h2u, ls(h2u, "up"), "l")
        leg.AddEntry(h2d, ls(h2d, "down"), "l")
        leg.AddEntry(h2, ls(h2, "nominal"), "le")

        #leg.SetHeader("(#color[1]{%.2f},  #color[4]{%.2f})" % (integral(h1), integral(h2)))
        leg.Draw()
        keep.append(leg)
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


def report(l=[], suffixes=["8TeVUp", "8TeVDown"], recursive=False):
    for (hs, message) in l:
        if not hs:
            continue

        for suffix in suffixes:
            hs2 = filter(lambda x: x.endswith(suffix), hs)
            for h in hs2:
                hs.remove(h)
            hs3 = [x[:x.find("_%s" % suffix)] for x in hs2]
            if recursive:
                report([(hs3, "%s (%s)" % (message, suffix))])

        m = collections.defaultdict(list)
        print message
        for h in sorted(hs):
            if tryNums(m, h) is None:
                m[''].append(h)

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
    report([(m1, "directories missing from '%s':" % file1),
            (m2, "directories missing from '%s':" % file2),
            ])

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
