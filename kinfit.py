#!/usr/bin/env python

import os
import ROOT as r


def setup(path="", lib=""):
    # https://twiki.cern.ch/twiki/bin/viewauth/CMS/HHKinFit
    full = "%s/%s" % (path, lib)
    if not os.path.exists(full):
        os.system("cd %s && ./compile.sh" % path)
    r.gSystem.Load(full)
    r.gROOT.LoadMacro("%s/include/HHKinFitMaster.h+" % path)


def fit(tree):
    b1 = r.TLorentzVector()
    b2 = r.TLorentzVector()
    tauvis1 = r.TLorentzVector()
    tauvis2 = r.TLorentzVector()

    b1.SetPtEtaPhiM(tree.CSVJ1Pt, tree.CSVJ1Eta, tree.CSVJ1Phi, tree.CSVJ1Mass)
    b2.SetPtEtaPhiM(tree.CSVJ2Pt, tree.CSVJ2Eta, tree.CSVJ2Phi, tree.CSVJ2Mass)

    tauvis1.SetPtEtaPhiM(tree.pt1.at(0), tree.eta1.at(0), tree.phi1.at(0), tree.m1.at(0))
    tauvis2.SetPtEtaPhiM(tree.pt2.at(0), tree.eta2.at(0), tree.phi2.at(0), tree.m2.at(0))

    kinFits = r.HHKinFitMaster(b1, b2, tauvis1, tauvis2)

    ptmiss = r.TLorentzVector()
    ptmiss.SetPtEtaPhiM(tree.met.at(0), 0.0, tree.metphi.at(0), 0.0)

    metcov = r.TMatrixD(2, 2)
    metcov[0][0] = tree.mvacov00
    metcov[1][0] = tree.mvacov10
    metcov[0][1] = tree.mvacov01
    metcov[1][1] = tree.mvacov11
    #metcov.Print()

    kinFits.setAdvancedBalance(ptmiss, metcov)

    kinFits.addMh1Hypothesis(hypo_mh1)
    kinFits.addMh2Hypothesis(hypo_mh2)
    
    kinFits.doFullFit()
    chi2 = kinFits.getBestChi2FullFit()
    mh = kinFits.getBestMHFullFit()
    #prob = kinFits.getFitProbFullFit()
    #print prob
    #print iEvent, chi2, prob, mh
    return chi2, mh


def loop(fileName="", nEventsMax=None):
    h_chi2 = r.TH1D("h_chi2", ";chi2;events / bin", 120, -10.0, 390.0)
    bins = [120, -10.0, 590.0]
    h_m = r.TH1D("h_m", ";m_{fit} (GeV);events / bin", *bins)
    h_fMass = r.TH1D("h_fMass", ";m_{no fit} (GeV);events / bin", *bins)

    bins2 = bins + bins
    h_m_vs_m = r.TH2D("h_m_vs_m", ";m_{fit} (GeV);m_{no fit};events / bin", *bins2)

    f = r.TFile(fileName)
    tree = f.Get("eventTree")
    
    nEvents = tree.GetEntries()
    if nEventsMax is not None:
        nEvents = min([nEvents, nEventsMax])

    for iEvent in range(nEvents):
        tree.GetEntry(iEvent)
        
        if tree.charge1.at(0) == tree.charge2.at(0):
            continue

        if 1.5 < tree.iso1.at(0):
            continue
            
        if 1.5 < tree.iso2.at(0):
            continue
            
        if tree.CSVJ1 < 0.679:
            continue
            
        if tree.CSVJ2 < 0.244:
            continue

        chi2, mh = fit(tree)
        h_chi2.Fill(chi2)
        h_m.Fill(mh)
        h_fMass.Fill(tree.fMass)
        h_m_vs_m.Fill(mh, tree.fMass)

    f.Close()
    return [h_chi2, h_m, h_fMass, h_m_vs_m]


def pdf(fileName="", histos=[]):
    out = "check.pdf"
    can = r.TCanvas()
    
    can.Print(out+"[")
    for h in histos:
        #h.SetStats(False)
        h.Draw()
        r.gPad.SetTickx()
        r.gPad.SetTicky()
        can.Print(out)
    can.Print(out+"]")


if __name__ == "__main__":
    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = 2000
    r.gStyle.SetOptStat("e")

    hypo_mh1 = r.std.vector('Int_t')()
    hypo_mh2 = r.std.vector('Int_t')()
    hypo_mh1.push_back(125)
    hypo_mh2.push_back(125)

    user = os.environ["USER"]
    setup(path="/afs/cern.ch/user/%s/%s/HHKinFit" % (user[0], user),
          lib="libHHKinFit.so",
          )
    histos = loop(fileName="v2/H2hh260_all.root",
                  #nEventsMax=200,
                  )
    pdf(fileName="check.pdf", histos=histos)
