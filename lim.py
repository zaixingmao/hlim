#!/usr/bin/env python

import os
import ROOT as r
import optparse
import xs


def system(cmd):
    if options.verbose:
        print cmd
    os.system(cmd)


def filenames(ch="", masses=[], method="", extra="", seed=None):
    assert method

    out = []
    for m in masses:
        # print ch, m
        args = "-M %s -m %d -n .Zprime.%s %s" % (method, m, ch, extra)
        fName = "higgsCombine.Zprime.%s.%s.mH%d.root" % (ch, method, m)
        if seed is not None:
            fName = fName.replace(".root", ".%d.root" % seed)
            args += " -s %d" % seed

        cmd = "combine %s LIMITS/%s/%d/zp_%s_0_13TeV.txt >& /dev/null" % (args, ch, m, ch)
        # cmd = "combine %s LIMITS/%s/%d/cmb.txt >& /dev/null" % (args, ch, m)
        system(cmd)
        out.append(fName)
    return out


def filenames_ml(ch="", masses=[], quiet=True):
    out = []

    outFile = "ml_results_%s.txt" % ch
    if os.path.exists(outFile):
        os.remove(outFile)

    for m in masses:
        #"--saveNLL --saveShapes --saveNormalizations"
        cmd = "combine -M MaxLikelihoodFit -m %d -n .Zprime.%s LIMITS/%s/%d/zp_%s_0_13TeV.txt" % (m, ch, ch, m, ch)
        if quiet:
            system("%s >& /dev/null" % cmd)
        else:
            system('echo "\n%d" >> %s' % (m, outFile))
            system("%s | grep -A 1 'Best fit r' >> %s" % (cmd, outFile))

        dest = "higgsCombine.Zprime.%s.ML.mH%d.root" % (ch, m)
        system("mv mlfit.Zprime.%s.root %s" % (ch, dest))
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


def dump_lim(ch, d, tag="", n=11):
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

    if options.xsRel:
        null = r.TH2D("", ch + ";M(Z')   [GeV];95% CL upper limit on r", 1, 400.0, 3100.0, 1, 0.001, 100.0)
    else:
        null = r.TH2D("", ch + ";M(Z')   [GeV];95% CL upper limit on #sigma(pp#rightarrow Z') x BR(Z'#rightarrow#tau#tau)   [pb]", 1, 400.0, 3100.0, 1, 0.001, 10.0)

    null.SetStats(False)
    null.Draw()

    leg = r.TLegend(0.5, 0.6, 0.8, 0.8)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)

    ssm15 = r.TGraph()
    ssm16 = r.TGraph()
    graphs = {}

    for quantile, mass_dict in sorted(d.iteritems()):

        graphs[quantile] = r.TGraph()
        iSSM15 = 0
        iSSM16 = 0
        for i, m in enumerate(masses):
            graphs[quantile].SetPoint(i, m, mass_dict[m])
            if abs(quantile - 0.5) < 0.001:
                if options.xsRel:
                    ssm15.SetPoint(i, m, 1.0)
                else:
                    xs15 = xs.pb_nlo(m, 2015)
                    xs16 = xs.pb_nlo(m, 2016)
                    if xs15 is not None:
                        ssm15.SetPoint(iSSM15, m, xs15)
                        iSSM15 += 1
                    else:
                        print "WARNING: no xs15 for mass %d" % m

                    if xs16 is not None:
                        ssm16.SetPoint(iSSM16, m, xs16)
                        iSSM16 += 1
                    else:
                        print "WARNING: no xs16 for mass %d" % m

                    if not any([xs15, xs16]):
                        continue

        if 0.0 < quantile:
            graphs[quantile].SetLineColor(r.kBlue)
            graphs[quantile].SetMarkerColor(r.kBlue)
            graphs[quantile].SetMarkerStyle(20)
        else:
            leg.AddEntry(graphs[quantile], "Observed", "l")

        if abs(quantile - 0.5) < 0.001:
            graphs[quantile].SetLineStyle(1)
            leg.AddEntry(graphs[quantile], "expected (post-fit)", "l")
            leg.AddEntry(ssm15, "xs (SSM, NLO 2015)", "l")
            leg.AddEntry(ssm16, "xs (SSM, NLO 2016)", "l")

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

        graphs[quantile].Draw("pcsame")

    ssm15.SetLineColor(r.kRed)
    ssm15.SetMarkerColor(r.kRed)
    ssm15.SetMarkerStyle(20)
    ssm15.Draw("same")

    ssm16.SetLineColor(r.kMagenta)
    ssm16.SetMarkerColor(r.kMagenta)
    ssm16.SetMarkerStyle(20)
    ssm16.Draw("same")

    leg.Draw()
    r.gPad.SetLogy()
    r.gPad.SetTickx()
    r.gPad.SetTicky()

    pdf = "%s_%s.pdf" % (ch, tag)
    r.gPad.Print(pdf)
    system("cp -p %s ~/public_html/" % pdf)


def diff_nuisances(ch="", filenames=[]):
    "--vtol2=99 --stol2=99 --vtol=99 --stol=99"
    prog = "%s/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py -a" % os.environ["CMSSW_BASE"]

    outFile = "nuisances_diffs_%s.txt" % ch
    if os.path.exists(outFile):
        os.remove(outFile)

    for filename in filenames:
        for cmd in ['echo "\n%s" >> %s' % (filename, outFile),
                    "python %s %s >> %s" % (prog, filename, outFile),
                    ]:
            system(cmd)

def opts():
    parser = optparse.OptionParser()
    parser.add_option("--verbose",
                      dest="verbose",
                      default=False,
                      action="store_true")
    parser.add_option("--xs-rel",
                      dest="xsRel",
                      default=False,
                      action="store_true")
    parser.add_option("--limits",
                      dest="limits",
                      default=False,
                      action="store_true")
    parser.add_option("--gof",
                      dest="gof",
                      default=False,
                      action="store_true")
    parser.add_option("--scan",
                      dest="scan",
                      default=False,
                      action="store_true")
    parser.add_option("--nuis",
                      dest="nuis",
                      default=False,
                      action="store_true")
    parser.add_option("--all",
                      dest="all",
                      default=False,
                      action="store_true")

    options, args = parser.parse_args()

    if options.all:
        for opt in ["limits", "gof", "scan", "nuis"]:
            setattr(options, opt, True)

    return options


if __name__ == "__main__":
    options = opts()

    # masses = range(500, 3500, 500)
    masses = [500, 750, 1250, 1750, 2000, 2500, 3000, 3500, 4000]
    # chs = ["cmb", "em", "et", "mt", "tt"][2:-1]
    chs = ["tt"]
    for ch in chs:
        # for tests
        # postfit = limits(chained(['higgsCombine.Zprime.et.Asymptotic.mH500.root', 'higgsCombine.Zprime.et.Asymptotic.mH1000.root', 'higgsCombine.Zprime.et.Asymptotic.mH1500.root', 'higgsCombine.Zprime.et.Asymptotic.mH2000.root', 'higgsCombine.Zprime.et.Asymptotic.mH2500.root', 'higgsCombine.Zprime.et.Asymptotic.mH3000.root']))

        if options.limits:
            postfit = limits(chained(filenames(ch=ch, masses=masses, method="Asymptotic")))
            plot_lim(ch, postfit, tag="limit")
            dump_lim(ch, postfit, tag="limit")
            # dump_lim(ch, limits(chained(filenames(ch=ch, masses=masses, method="Asymptotic", extra="-t -1"))), tag="prelimit")
            # dump_lim(ch, limits(chained(filenames(ch=ch, masses=masses, method="MaxLikelihoodFit"))), tag="r")
            # dump_lim(ch, limits(chained(filenames(ch=ch, masses=masses, method="ProfileLikelihood", extra="--significance"))), tag="signif")

        if options.gof:
            dump_lim(ch, limits(chained(filenames(ch=ch, masses=masses[:1], method="GoodnessOfFit", extra="--algo=saturated --fixedSignalStrength=0"))), tag="gof")
            filenames(ch=ch, masses=masses[:1], method="GoodnessOfFit", extra="--algo=saturated --fixedSignalStrength=0 -t 100", seed=1)

        if options.scan:
            print filenames(ch=ch, masses=masses, method="MultiDimFit", extra="--algo=grid --points=100 --setPhysicsModelParameterRanges r=0,2 --minimizerAlgo=Minuit")

        if options.nuis:
            diff_nuisances(ch, filenames_ml(ch, masses))
