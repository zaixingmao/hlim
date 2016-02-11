#!/usr/bin/env python

import os
import ROOT as r
from h2bsm import xs_fb


def filenames(ch="", masses=[], method="", extra=""):
    assert method

    out = []
    for m in masses:
        # print ch, m
        args = "-M %s -m %d -n .Zprime.%s %s" % (method, m, ch, extra)
        cmd = "combine %s LIMITS/%s/%d/htt_%s_0_13TeV.txt >& /dev/null" % (args, ch, m, ch)
        # print cmd
        os.system(cmd)
        out.append("higgsCombine.Zprime.%s.%s.mH%d.root" % (ch, method, m))
    return out


def filenames_ml(ch="", masses=[], quiet=True):
    out = []

    outFile = "ml_results_%s.txt" % ch
    if os.path.exists(outFile):
        os.remove(outFile)

    for m in masses:
        #"--saveNLL --saveShapes --saveNormalizations"
        cmd = "combine -M MaxLikelihoodFit -m %d -n .Zprime.%s LIMITS/%s/%d/htt_%s_0_13TeV.txt" % (m, ch, ch, m, ch)
        if quiet:
            os.system("%s >& /dev/null" % cmd)
        else:
            os.system('echo "\n%d" >> %s' % (m, outFile))
            os.system("%s | grep -A 1 'Best fit r' >> %s" % (cmd, outFile))
        dest = "higgsCombine.Zprime.%s.ML.mH%d.root" % (ch, m)
        os.system("mv mlfit.Zprime.%s.root %s" % (ch, dest))
        out.append(dest)
    return out


def chained(l=[], treeName="limit"):
    out = r.TChain(treeName)
    for filename in l:
        out.AddFile(filename)
    return out


def limits(chain):
    d = {}
    for iEntry in range(chain.GetEntries()):
        chain.GetEntry(iEntry)
        key = round(chain.quantileExpected, 3)
        if key not in d:
            d[key] = {}
        d[key][chain.mh] = chain.limit
    return d


def dump_lim(ch, d, tag="", n=10):
    masses = set(sum([x.keys() for x in d.values()], []))
    masses = sorted(list(masses))

    header0 = "%s %s" % (ch, tag)
    header = "   ".join([header0.ljust(n)] + ["%7d" % m for m in masses])
    print header
    print "-" * len(header)
    for quantile, mass_dict in sorted(d.iteritems()):
        row = ["%7.3f" % quantile if quantile > 0.0 else "(obs)"]
        row[0] = row[0].ljust(n)
        for m in masses:
            row.append("%7.3f" % mass_dict[m])
        print "   ".join(row)
    print


def plot_lim(ch, d, tag=""):
    masses = set(sum([x.keys() for x in d.values()], []))
    masses = sorted(list(masses))

    null = r.TH2D("", ch + ";M(Z')   [GeV];95% CL upper limit on #sigma(pp#rightarrow Z') x BR(Z'#rightarrow#tau#tau)   [pb]", 1, 400.0, 3100.0, 1, 0.01, 10.0)
    null.SetStats(False)
    null.Draw()

    leg = r.TLegend(0.5, 0.6, 0.8, 0.8)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)

    ssm = r.TGraph()
    graphs = {}

    for quantile, mass_dict in sorted(d.iteritems()):

        graphs[quantile] = r.TGraph()
        for i, m in enumerate(masses):
            graphs[quantile].SetPoint(i, m, mass_dict[m])
            if abs(quantile - 0.5) < 0.001:
                ssm.SetPoint(i, m, xs_fb(m) / 1000.)

        if 0.0 < quantile:
            graphs[quantile].SetLineColor(r.kBlue)
        else:
            leg.AddEntry(graphs[quantile], "Observed", "l")

        if abs(quantile - 0.5) < 0.001:
            graphs[quantile].SetLineStyle(1)
            leg.AddEntry(graphs[quantile], "expected (post-fit)", "l")
            leg.AddEntry(ssm, "SSM xs", "l")

        if abs(quantile - 0.84) < 0.001:
            graphs[quantile].SetLineStyle(2)
            leg.AddEntry(graphs[quantile], "#pm1#sigma expected (post-fit)", "l")

        if abs(quantile - 0.16) < 0.001:
            graphs[quantile].SetLineStyle(2)

        if abs(quantile - 0.975) < 0.001:
            graphs[quantile].SetLineStyle(3)
            leg.AddEntry(graphs[quantile], "#pm2#sigma expected (post-fit)", "l")

        if abs(quantile - 0.025) < 0.001:
            graphs[quantile].SetLineStyle(3)

        graphs[quantile].Draw("csame")

    ssm.SetLineColor(r.kRed)
    ssm.Draw("same")

    leg.Draw()
    r.gPad.SetLogy()
    r.gPad.SetTickx()
    r.gPad.SetTicky()

    pdf = "%s_%s.pdf" % (ch, tag)
    r.gPad.Print(pdf)
    os.system("cp -p %s ~/public_html/" % pdf)


def diff_nuisances(ch="", filenames=[]):
    prog = "%s/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py" % os.environ["CMSSW_BASE"]

    outFile = "nuisances_diffs_%s.txt" % ch
    if os.path.exists(outFile):
        os.remove(outFile)

    for filename in filenames:
        os.system('echo "\n%s" >> %s' % (filename, outFile))
        os.system("python %s %s >> %s" % (prog, filename, outFile))


if __name__ == "__main__":
    masses = range(500, 3500, 500)
    chs = ["et", "em", "mt", "tt"][:2]
    for ch in chs:
        # for tests
        # postfit = limits(chained(['higgsCombine.Zprime.et.Asymptotic.mH500.root', 'higgsCombine.Zprime.et.Asymptotic.mH1000.root', 'higgsCombine.Zprime.et.Asymptotic.mH1500.root', 'higgsCombine.Zprime.et.Asymptotic.mH2000.root', 'higgsCombine.Zprime.et.Asymptotic.mH2500.root', 'higgsCombine.Zprime.et.Asymptotic.mH3000.root']))

        postfit = limits(chained(filenames(ch=ch, masses=masses, method="Asymptotic")))
        plot_lim(ch, postfit, tag="limit")
        dump_lim(ch, postfit, tag="limit")
        dump_lim(ch, limits(chained(filenames(ch=ch, masses=masses, method="Asymptotic", extra="-t -1"))), tag="prelimit")
        dump_lim(ch, limits(chained(filenames(ch=ch, masses=masses, method="MaxLikelihoodFit"))), tag="r")
        dump_lim(ch, limits(chained(filenames(ch=ch, masses=masses, method="ProfileLikelihood", extra="--significance"))), tag="signif")
        dump_lim(ch, limits(chained(filenames(ch=ch, masses=masses, method="GoodnessOfFit", extra="--algo=saturated --fixedSignalStrength=0"))), tag="gof")
        diff_nuisances(ch, filenames_ml(ch, masses))
