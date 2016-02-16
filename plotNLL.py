#!/usr/bin/env python

import os
import ROOT as r

def one_graph(channel, mass, color):
    f = r.TFile("higgsCombine.Zprime.%s.MultiDimFit.mH%d.root" % (channel, mass))
    tree = f.Get("limit")
    tree.Draw("2*deltaNLL:r")
    graph = r.gROOT.FindObject("Graph").Clone("%s_%d" % (channel, mass))
    graph.Sort()
    
    graph.SetLineWidth(2)
    graph.SetLineColor(color)
    graph.SetMarkerStyle(7)
    graph.SetMarkerColor(color)
    graph.SetTitle(";#sigma(M_{%d})   [pb];-2 #Delta ln L" % mass)
    graph.GetXaxis().SetTitleOffset(1.2)
    graph.GetXaxis().SetRangeUser(0, 2)
    graph.GetYaxis().SetRangeUser(0, 8)
    f.Close()

    return graph


if __name__ == "__main__":
    c = r.TCanvas("canvas", "canvas", 2)

    combined = False
    if combined:
        os.system("combineCards.py LIMITS/cmb/500/htt_et_0_13TeV.txt LIMITS/cmb/500/htt_mt_0_13TeV.txt > etmt.txt")
        os.system("combineCards.py LIMITS/cmb/500/htt_*_0_13TeV.txt > cmb.txt")
        os.system("combine -M MultiDimFit -m 500 -n .Zprime.cmb --algo=grid --points=100 --setPhysicsModelParameterRanges r=0,2 cmb.txt --minimizerAlgo=Minuit")
        os.system("combine -M MultiDimFit -m 500 -n .Zprime.etmt --algo=grid --points=100 --setPhysicsModelParameterRanges r=0,2 etmt.txt --minimizerAlgo=Minuit")

    mass = 500
    et = one_graph("et", mass, 214)
    mt = one_graph("mt", mass, r.kRed)
    em = one_graph("em", mass, r.kGreen)
    tt = one_graph("tt", mass, r.kCyan)

    if combined:
        cmb = one_graph("cmb", mass, r.kBlack)
        etmt = one_graph("etmt", mass, r.kMagenta)

    et.Draw("apc")
    mt.Draw("pcsame")
    em.Draw("pcsame")
    tt.Draw("pcsame")
    if combined:
        cmb.Draw("pcsame")
        etmt.Draw("pcsame")

    leg = r.TLegend(0.6, 0.6, 0.9, 0.9)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)

    leg.AddEntry(et, "et", "l")
    leg.AddEntry(mt, "mt", "l")
    leg.AddEntry(em, "em", "l")
    leg.AddEntry(tt, "tt", "l")
    if combined:
        leg.AddEntry(cmb, "cmb (et,mt,em,tt)", "l")
        leg.AddEntry(etmt, "cmb (et,mt)", "l")

    leg.Draw()

    c.SetGridy()
    c.SetTickx()
    c.SetTicky()
    
    c.Print("nll.pdf")

