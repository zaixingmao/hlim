#!/usr/bin/env python
from operator import itemgetter

import ROOT as r
r.gROOT.SetBatch(True)

def setMyLegend(lPosition, lHistList):
    l = r.TLegend(lPosition[0], lPosition[1], lPosition[2], lPosition[3])
    l.SetFillStyle(0)
    l.SetBorderSize(0)
    for i in range(len(lHistList)):
        l.AddEntry(lHistList[i][0], lHistList[i][1])
    return l


def getGraph(file, graph):

    ifile = r.TFile(file)
    tree = ifile.Get("limit")

    nEntries = tree.GetEntries()

    values = []

    xRange = [-2.0, 2.0]

    for i in range(nEntries):
        tree.GetEntry(i)
#         xValue = tree.CMS_scale_t_tautau_8TeV
#         xValue = tree.CMS_scale_j_8TeV
        xValue = tree.CMS_htt_ttbarNorm_8TeV

        if xValue < xRange[0] or xValue > xRange[1]:
            continue
        values.append((xValue, tree.deltaNLL))
    
    values = sorted(values, key=itemgetter(0), reverse=False)

    for i in range(len(values)):
        graph.SetPoint(i, values[i][0], values[i][1])


    return graph

def draw():
    g1 = r.TGraph()
    g2 = r.TGraph()
    g3 = r.TGraph()

    fakeHist1 = r.TH1F()
    fakeHist1.SetLineColor(r.kRed)
    fakeHist1.SetLineStyle(2)
    fakeHist2 = r.TH1F()
    fakeHist3 = r.TH1F()
    fakeHist3.SetLineColor(r.kBlue)
    fakeHist3.SetLineStyle(2)

    g1 = getGraph("higgsCombineTest.MultiDimFit.mH260.root", g1)
    g2 = getGraph("higgsCombineTest.MultiDimFit.mH270.root", g2)
    g3 = getGraph("higgsCombineTest.MultiDimFit.mH280.root", g3)

    varName = 'ttbarNorm'#''#'scale_jet_pt'#'scale_tau_pt'


    psfile = '%s.pdf' %varName
    c = r.TCanvas("c","Test", 800, 600)

    g1.SetMaximum(5.0)
    g1.GetXaxis().SetTitle("%s" %varName)
    g1.GetYaxis().SetTitle("-ln(Likelihood)")

    g1.SetMaximum(5.0)
    g1.SetMinimum(-0.2)
    g1.SetLineColor(r.kRed)
    g1.SetLineStyle(2)
    g3.SetLineColor(r.kBlue)
    g3.SetLineStyle(2)
    g1.Draw('AC')
    g2.Draw('same')
    g3.Draw('same')


    position = (0.2, 0.85 - 0.06*3, 0.55, 0.85)
#     legend = setMyLegend(position, [(fakeHist1, 'mH270, after fit = (-0.29sig, 0.57)'),
#                                     (fakeHist2, 'mH280, after fit = (-0.17sig, 1.25)'),
#                                     (fakeHist3, 'mH290, after fit = (-0.29sig, 0.72)')])

#     legend = setMyLegend(position, [(fakeHist1, 'mH270, after fit = (+0.06sig, 0.94)'),
#                                     (fakeHist2, 'mH280, after fit = (-0.21sig, 0.83)'),
#                                     (fakeHist3, 'mH290, after fit = (-0.12sig, 0.60)')])

    legend = setMyLegend(position, [(fakeHist1, 'mH260, after fit = (+0.20sig, 0.93)'),
                                    (fakeHist2, 'mH270, after fit = (-0.57sig, 1.71)'),
                                    (fakeHist3, 'mH280, after fit = (+0.21sig, 1.02)')])

    legend.Draw('same')



    c.Print('%s' %psfile)

draw()


