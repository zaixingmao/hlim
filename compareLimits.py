#!/usr/bin/env python
import ROOT as r
import optparse

r.gStyle.SetOptStat(0)
r.gROOT.SetBatch(True)  # to suppress canvas pop-outs

def opts():
    parser = optparse.OptionParser()
    parser.add_option("--input", dest="inputFile", default="/Users/zmao/Downloads/tt_ggHTohh-limit_compare.txt" , help="input file where it specifies the limits")
    parser.add_option("--useForBand", dest="useForBand", default=0, help="which block is used for plotting sigma bands")
    parser.add_option("--nameForMain", dest="nameForMain", default='cut base', help="name for the analysis which has the sigma bands")
    parser.add_option("--nameForExtra", dest="nameForExtra", default='BDT', help="name for the analysis which has only the median values")

    options, args = parser.parse_args()
    return options

options = opts()

def compareLimits(ifile, useForBand, nameForMain, nameForExtra):

    lines = open(ifile, "r").readlines()

    bands = []
    median = []
    save = False
    for i in range(0, len(lines)):   #loop through Map file
        current_line = lines[i]
        contents = current_line.split()
        if len(contents) > 1 and contents[0] == '260': #start of block
            bands.append({"2Sig": [], "1Sig": []})
            median.append([])
            save = True
        
        if save:    
            #Fill
            bands[len(bands)-1]["2Sig"].append(int(contents[0]))
            bands[len(bands)-1]["2Sig"].append(float(contents[1]))
            bands[len(bands)-1]["2Sig"].append(float(contents[5]))
            bands[len(bands)-1]["1Sig"].append(int(contents[0]))
            bands[len(bands)-1]["1Sig"].append(float(contents[2]))
            bands[len(bands)-1]["1Sig"].append(float(contents[4]))
            median[len(bands)-1].append(int(contents[0]))
            median[len(bands)-1].append(float(contents[3]))

        if len(contents) > 1 and contents[0] == '350': #end of block
            save = False

    if len(bands) < 2:
        print "Only found one block of limits. Please add another block for comparison!!"
        return 0

    #Fill TGraph
    nPoints = len(median[useForBand])/2
    sig2Band = r.TGraph()
    sig1Band = r.TGraph()
#     sig2Band.SetFillStyle(3001)
    sig2Band.SetFillColor(r.TColor.GetColor(252,241,15))
#     sig1Band.SetFillStyle(3001)
    sig1Band.SetFillColor(r.kGreen)
    median1 = r.TGraph()
    median1.SetLineColor(r.kRed)
    median1.SetLineWidth(2)
    median2 = r.TGraph()
    median2.SetLineColor(r.kBlue)
    median2.SetLineStyle(2)
    median2.SetLineWidth(2)

    diff = r.TGraph()
    diff.SetLineColor(r.kBlue)
    diff.SetLineStyle(2)
    diff.SetLineWidth(2)

    if useForBand:
        notUseForBand = 0
    else:
        notUseForBand = 1

    for i in range(nPoints):
        sig2Band.SetPoint(i, bands[useForBand]["2Sig"][i*3], bands[useForBand]["2Sig"][i*3+2])
        sig2Band.SetPoint(2*nPoints - 1 - i, bands[useForBand]["2Sig"][i*3], bands[useForBand]["2Sig"][i*3+1])
        sig1Band.SetPoint(i, bands[useForBand]["1Sig"][i*3], bands[useForBand]["1Sig"][i*3+2])
        sig1Band.SetPoint(2*nPoints - 1 - i, bands[useForBand]["1Sig"][i*3], bands[useForBand]["1Sig"][i*3+1])
        median1.SetPoint(i, median[useForBand][i*2], median[useForBand][i*2+1])
        median2.SetPoint(i, median[notUseForBand][i*2], median[notUseForBand][i*2+1])
        diff.SetPoint(i, median[0][i*2], 2*abs(median[0][i*2+1]-median[1][i*2+1])/(median[0][i*2+1]+median[1][i*2+1]))

    canv = r.TH1F('canv', '', 10, 260, 350)
    canv.SetXTitle("m_{H} [GeV]")
    canv.GetXaxis().SetLabelFont(62)
    canv.GetXaxis().SetLabelSize(0.045)
    canv.GetXaxis().SetLabelOffset(0.015)
    canv.GetXaxis().SetTitleSize(0.045)
    canv.GetXaxis().SetTitleFont(62)
    canv.GetXaxis().SetTitleColor(1)
    canv.GetXaxis().SetTitleOffset(1.05)
    canv.SetYTitle("95% CL limit on #sigma(gg#rightarrowH#rightarrowhh) #times BR [pb]")
    canv.GetYaxis().SetLabelFont(62)
    canv.GetYaxis().SetTitleFont(62)
    canv.GetYaxis().SetTitleOffset(1.1)
    canv.GetYaxis().SetTitleSize(0.045)
    canv.GetYaxis().SetLabelSize(0.045)
    canv.SetNdivisions(505, "X")

    #Set Legend
    l = r.TLegend(0.12, 0.65, 0.62, 0.85)
    l.SetBorderSize( 0 )
    l.SetFillStyle( 1001 )
    l.SetFillColor(r.kWhite)
    l.AddEntry(median1, "Expected (%s)" %nameForMain, "L")
    l.AddEntry(sig1Band, "#pm 1#sigma Expected",  "F")
    l.AddEntry(sig2Band, "#pm 2#sigma Expected",  "F")
    l.AddEntry(median2, "Expected (%s)" %nameForExtra,  "L")

    psfile = '%sVS%s_limit.pdf' %(nameForMain, nameForExtra)
    c = r.TCanvas("c","Test", 800, 700)
    p = r.TPad("p","p",0.05,1,1.,0.05)
    p.Draw()
    p.cd()
    r.gPad.SetTicky()
    r.gPad.SetTickx()
    canv.SetMaximum(5)
    canv.Draw()
    canv.SetTitle("CMS, H #rightarrow #tau#tau, 19.7 fb^{-1} at 8 TeV")
    r.gStyle.SetTitleX(0.33)
    r.gStyle.SetTitleY(0.96)
    r.gStyle.SetTitleFontSize(0.04)
    sig2Band.Draw("fsame")
    sig1Band.Draw("fsame")
    median1.Draw("Lsame")
    median2.Draw("Lsame")
    l.Draw("same")
    canv.GetYaxis().Draw("A")
    canv.Draw("sameaxis")
    c.Print('%s(' %psfile)
    c.Clear()

    canv2 = r.TH1F('canv2', '', 10, 260, 350)
    canv2.SetXTitle("m_{H} [GeV]")
    canv2.GetXaxis().SetLabelFont(62)
    canv2.GetXaxis().SetLabelSize(0.045)
    canv2.GetXaxis().SetLabelOffset(0.015)
    canv2.GetXaxis().SetTitleSize(0.045)
    canv2.GetXaxis().SetTitleFont(62)
    canv2.GetXaxis().SetTitleColor(1)
    canv2.GetXaxis().SetTitleOffset(1.05)
    canv2.SetYTitle("Limit Differences")
    canv2.GetYaxis().SetLabelFont(62)
    canv2.GetYaxis().SetTitleFont(62)
    canv2.GetYaxis().SetTitleOffset(1.25)
    canv2.GetYaxis().SetTitleSize(0.045)
    canv2.GetYaxis().SetLabelSize(0.045)
    canv2.SetNdivisions(505, "X")

    #Set Legend
    l2 = r.TLegend(0.4, 0.65, 0.8, 0.85)
    l2.SetBorderSize( 0 )
    l2.SetFillStyle( 1001 )
    l2.SetFillColor(r.kWhite)
    l2.AddEntry(diff, "#frac{2 #times | %s - %s |}{%s + %s}" %(nameForMain, nameForExtra, nameForMain, nameForExtra), "L")

    p2 = r.TPad("p2","p2",0.05,1,1.,0.05)
    p2.Draw()
    p2.cd()
    r.gPad.SetTicky()
    r.gPad.SetTickx()
    p2.SetGrid()
    canv2.SetMaximum(0.5)
    canv2.Draw()
    canv2.SetTitle("CMS, H #rightarrow #tau#tau, 19.7 fb^{-1} at 8 TeV")
    r.gStyle.SetTitleX(0.33)
    r.gStyle.SetTitleY(0.96)
    r.gStyle.SetTitleFontSize(0.04)
    diff.Draw("Lsame")
    l2.Draw("same")
    canv2.GetYaxis().Draw("A")
    canv2.Draw("sameaxis")
    c.Print('%s)' %psfile)

compareLimits(ifile = options.inputFile, useForBand = options.useForBand, nameForMain = options.nameForMain, nameForExtra = options.nameForExtra)
