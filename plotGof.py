#!/usr/bin/env python

import ROOT as r
import bisect


def gofs(channel, mass, seed=None):
    fName = "higgsCombine.Zprime.%s.GoodnessOfFit.mH%d.root" % (channel, mass)
    if seed is not None:
        fName = fName.replace(".root", ".%d.root" % seed)

    f = r.TFile(fName)
    tree = f.Get("limit")
    vals = []
    for iEntry in range(tree.GetEntries()):
        tree.GetEntry(iEntry)
        vals.append(tree.limit)
    vals.sort()
    f.Close()
    return vals


def rank(obs, vals):
    return bisect.bisect(sorted(vals), obs)


def go(channel, mass, seed):
    vals = gofs(channel, mass, seed=seed)
    h = r.TH1D("gof_dist_null", channel + ";goodness-of-fit statistic:  -2 log #frac{L(obs | SM)}{L(obs | obs)};Toys / bin", 100, 0.0, 1.1*vals[-1])
    h.SetStats(False)
    h.GetXaxis().SetTitleOffset(1.2)

    for val in vals:
        h.Fill(val)
    h.Draw("ehist")

    obs = gofs(channel, mass, seed=None)[0]
    arr = r.TArrow()
    arr.SetLineWidth(2)
    arr.SetArrowSize(0.5 * arr.GetArrowSize())
    arr_obs = arr.DrawArrow(obs, 0.5 * h.GetMaximum(), obs, 0.0)

    leg = r.TLegend(0.1, 0.7, 0.5, 0.9)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)

    leg.AddEntry(h, "distribution under null (%d toys)" % len(vals), "le")
    leg.AddEntry(arr_obs, "obs (p-value = %d / %d)" % (len(vals) - rank(obs, vals), len(vals)), "l")

    leg.Draw()

    r.gPad.SetTickx()
    r.gPad.SetTicky()
    r.gPad.Print("gof_%s.pdf" % channel)


if __name__ == "__main__":
    r.gROOT.SetBatch(True)

    # mass is part of filename but was not used in computation
    for ch in ["et", "em", "mt", "tt"]:
        go(channel=ch, mass=500, seed=1)


