#!/usr/bin/env python

import ROOT as r
import collections
import os
import sys


def fetchOneDir(f, subdir, scale):
    out = {}
    for key in r.gDirectory.GetListOfKeys():
        name = key.GetName()
        h = f.Get("%s/%s" % (subdir, name)).Clone()
        h.SetDirectory(0)
        h.Scale(scale)
        if not options.raw_yields:
            normalize(h)
        out[name] = h
    return out


def date_and_histograms(fileName, scale):
    b = "%s/src/auxiliaries/shapes" % os.environ["CMSSW_BASE"]

    if not fileName:
        return '', {}

    if b not in fileName:
        fileName = "%s/%s" % (b, fileName)

    f = r.TFile(fileName)
    if f.IsZombie():
        sys.exit("'%s' is a zombie." % fileName)

    date = f.GetCreationDate()
    out = {}
    for key in f.GetListOfKeys():
        name = key.GetName()
        f.cd(name)
        out[name] = fetchOneDir(f, name, scale)
    f.Close()
    return date, out


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
    out = h.Integral(1, h.GetNbinsX(), "" if options.raw_yields else "width")
    for bin in [0, 1 + h.GetNbinsX()]:
        out += h.Integral(bin, bin)
    return out


def bandHisto(u, d):
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


def shortened(band):
    s = band
    for old, new in [("_tautau_8TeV", ""),
                     ("_8TeV", ""),
                     ("_13TeV", ""),
                     ("CMS_", ""),
                     ]:
        s = s.replace(old, new)
    return s


def draw(h, gopts, d, colorFlip):
    h.Draw(gopts)

    flipped = d.get(h.GetName() + options.flippedSuffix)
    if flipped:
        flipped.Multiply(h)
        flipped.SetLineStyle(h.GetLineStyle())
        flipped.SetLineColor(colorFlip)
        flipped.SetMarkerColor(colorFlip)
        flipped.Draw(gopts.replace("hist", "") + "same")


def oneDir(canvas, pdf, hNames, d1, d2, subdir, xTitle, band, skip2=False):
    keep = []

    iEnd = len(whiteList) - 1
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
            print "ERROR: '%s' not in list of available names: %s" % (hName, str(hNames))

        h1 = d1[subdir].get(hName)
        if not h1:
            print "ERROR: %s/%s not found" % (subdir, hName)
            if j == 3 or i == iEnd:
                canvas.cd(0)
                canvas.Print(pdf)
            continue

        h1b = None
        if band:
            h1u = d1[subdir].get("%s_%sUp" % (hName, band))
            h1d = d1[subdir].get("%s_%sDown" % (hName, band))
            if h1u and h1d:
                h1b = bandHisto(h1u, h1d)
                keep.append(h1b)

        h2 = d2[subdir].get(hName)
        if not h2:
            print "ERROR: %s/%s not found" % (subdir, hName)
            if j == 3 or i == iEnd:
                canvas.cd(0)
                canvas.Print(pdf)
            continue

        h2b = None
        if band:
            h2u = d2[subdir].get("%s_%sUp" % (hName, band))
            h2d = d2[subdir].get("%s_%sDown" % (hName, band))
            if h2u and h2d:
                h2b = bandHisto(h2u, h2d)
                keep.append(h2b)

        canvas.cd(1 + j)
        r.gPad.SetTickx()
        r.gPad.SetTicky()

        hFirst = h1b if (band and h1b) else h1
        title = "%s / %s" % (subdir, hName)
        if band:
            title += " / %s" % shortened(band)

        hFirst.SetTitle("%s;%s;events / %s" % (title, xTitle, "bin" if options.raw_yields else "GeV"))

        hList = [h1, h2]
        if h1b:
            hList += [h1u, h1d]
        if h2b:
            hList += [h2u, h2d]

        if options.logy:
            r.gPad.SetLogy()
            hFirst.SetMaximum(2.0 * maximum(hList))
        else:
            hFirst.SetMinimum(0.0)
            hFirst.SetMaximum(1.1 * maximum(hList))

        hFirst.SetStats(False)
        hFirst.GetYaxis().SetTitleOffset(1.25)

        if band and h1b:
            h1b.SetMarkerColor(bandColor1)
            h1b.SetLineColor(bandColor1)
            h1b.SetFillColor(bandColor1)
            h1b.SetFillStyle(3354)
            h1b.Draw("e2")

            h1d.SetLineColor(bandColor1)
            h1d.SetLineStyle(4)
            draw(h1d, "histsame", d1[subdir], bandColor1Flip)

            h1u.SetLineColor(bandColor1)
            draw(h1u, "histsame", d1[subdir], bandColor1Flip)

        h1.SetLineColor(lineColor1)
        h1.SetMarkerColor(lineColor1)
        draw(h1, "ehistsame" if band else "ehist", d1[subdir], lineColor1Flip)
        #keep.append(moveStatsBox(h1))

        if band and h2b and not skip2:
            h2b.SetMarkerColor(bandColor2)
            h2b.SetLineColor(bandColor2)
            h2b.SetFillColor(bandColor2)
            h2b.SetFillStyle(3345)
            h2b.Draw("e2same")

            h2d.SetLineColor(bandColor2)
            h2d.SetLineStyle(4)
            draw(h2d, "histsame", d2[subdir], bandColor2Flip)

            h2u.SetLineColor(bandColor2)
            draw(h2u, "histsame", d2[subdir], bandColor2Flip)

        if not skip2:
            h2.SetLineColor(lineColor2)
            h2.SetMarkerColor(lineColor2)
            draw(h2, "ehistsame", d2[subdir], lineColor2Flip)
            #keep.append(moveStatsBox(h2))

        leg = r.TLegend(0.65, 0.6, 0.87, 0.87)
        leg.SetBorderSize(0)
        leg.SetFillStyle(0)

        if band and h1b:
            #leg.AddEntry(h1b, "band", "f")
            leg.AddEntry(h1u, ls(h1u, "up"), "l")
            leg.AddEntry(h1d, ls(h1d, "down"), "l")
        leg.AddEntry(h1, ls(h1, "nominal"), "le")

        if band and h2b and not skip2:
            #leg.AddEntry(h2b, "band", "f")
            leg.AddEntry(h2u, ls(h2u, "up"), "l")
            leg.AddEntry(h2d, ls(h2d, "down"), "l")
        if not skip2:
            leg.AddEntry(h2, ls(h2, "nominal"), "le")

        #leg.SetHeader("(#color[1]{%.2f},  #color[4]{%.2f})" % (integral(h1), integral(h2)))
        leg.Draw()
        keep.append(leg)
        if j == 3 or i == iEnd:
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


def report(l=[], suffixes=["Up", "Down", "_WAS_FLIPPED"], recursive=False):
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


def drawTitlePage(canvas, pdf, xTitle, file1, date1, scale1, file2, date2, scale2, band):
    text = r.TText()
    text.SetNDC()
    text.SetTextAlign(22)

    text.DrawText(0.5, 0.8, xTitle)
    text.DrawText(0.5, 0.7, "band: %s" % band)

    text.SetTextSize(0.7 * text.GetTextSize())

    if file1:
        text.SetTextColor(lineColor1)
        text.DrawText(0.5, 0.45, file1)
        text.DrawText(0.5, 0.41, "scale = %g" % scale1)
        text.DrawText(0.5, 0.37, "(%s)" % date1.AsString())

    if file2:
        text.SetTextColor(lineColor2)
        text.DrawText(0.5, 0.31, file2)
        text.DrawText(0.5, 0.27, "scale = %g" % scale2)
        text.DrawText(0.5, 0.23, "(%s)" % date2.AsString())

    text.SetTextColor(r.kMagenta)
    text.DrawText(0.5, 0.1, ".pdf file created at " + r.TDatime().AsString())
    canvas.Print(pdf)


def go(xTitle, file1, scale1, file2, scale2, band=""):
    date1, d1 = date_and_histograms(file1, scale1)
    date2, d2 = date_and_histograms(file2, scale2)

    if not file2:
        date2 = date1
        d2 = d1

    subdirs, m1, m2 = common_keys(d1, d2)
    report([(m1, "directories missing from '%s':" % file1),
            (m2, "directories missing from '%s':" % file2),
            ])

    pdf = "comparison_%s" % xTitle.split()[0]
    if band:
        pdf += "_%s" % shortened(band)
    pdf += ".pdf"

    canvas = r.TCanvas()
    canvas.Print(pdf + "[")

    drawTitlePage(canvas, pdf, xTitle, file1, date1, scale1, file2, date2, scale2, band)

    for subdir in reversed(subdirs):
        hNames, h1, h2 = common_keys(d1[subdir], d2[subdir])
        report([(h1, 'histograms missing from %s/%s:' % (file1, subdir)),
                (h2, 'histograms missing from %s/%s:' % (file2, subdir)),
                ])

        hNames = filter(lambda hName: not any([hName.startswith(x) for x in ignorePrefixes]), hNames)
        oneDir(canvas, pdf, hNames, d1, d2, subdir, xTitle, band, skip2=not file2)

    canvas.Print(pdf + "]")


def opts():
    import optparse
    parser = optparse.OptionParser()

    parser.add_option("--file1",
                      dest="file1",
                      # default="Brown/htt_data50ns_mc25ns_noPUWeight-13TeV-mvis.root",
                      default="Brown/m_vis.root",
                      )

    parser.add_option("--file2",
                      dest="file2",
                      default="Imperial/ic4.root",
                      )

    parser.add_option("--scale1",
                      dest="scale1",
                      default=1.0,
                      type="float",
                      )

    parser.add_option("--scale2",
                      dest="scale2",
                      default=1.0,
                      type="float",
                      )

    parser.add_option("--xtitle",
                      dest="xtitle",
                      default="m_vis (GeV)",
                      )

    parser.add_option("--raw-yields",
                      dest="raw_yields",
                      default=False,
                      action="store_true",
                      )

    parser.add_option("--logy",
                      dest="logy",
                      default=False,
                      action="store_true",
                      )

    parser.add_option("--masses",
                      dest="masses",
                      default="160",
                      )

    parser.add_option("--bands",
                      dest="bands",
                      # default=",".join(["CMS_scale_%s_8TeV" % s for s in ["t_tautau", "j", "btag", "btagEff", "btagFake"]]),
                      default=",".join(["", "CMS_scale_W_13TeV", "CMS_scale_j_13TeV", "CMS_scale_btag_13TeV"])
                      )

    parser.add_option("--flipped-suffix",
                      dest="flippedSuffix",
                      default="_WAS_FLIPPED",
                      )

    options, args = parser.parse_args()
    return options


if __name__ == "__main__":
    r.gROOT.SetBatch(True)
    r.PyConfig.IgnoreCommandLineOptions = True


    ignorePrefixes = ["ggAToZh", "bbH", "ggRadion", "ggGraviton"]

    r.gErrorIgnoreLevel = 2000
    r.gStyle.SetOptStat("rme")
    r.gROOT.SetBatch(True)

    lineColor1 = r.kBlack
    lineColor1Flip = r.kOrange - 7
    bandColor1 = r.kGray
    bandColor1Flip = r.kOrange - 5

    lineColor2 = r.kBlue
    lineColor2Flip = r.kViolet + 4
    bandColor2 = r.kCyan
    bandColor2Flip = r.kViolet + 6

    options = opts()

    whiteList = ["TT", "QCD", "VV", "ZTT", "W", "W+QCD", "sum_b"]
    # whiteList += ["ZL", "ZJ", "data_obs"]
    whiteList += ["ggH%s" % m for m in options.masses.split()]

    for band in options.bands.split(","):
        go(options.xtitle, options.file1, options.scale1, options.file2, options.scale2, band)
