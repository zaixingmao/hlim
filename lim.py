#!/usr/bin/env python

import os
import ROOT as r


def filenames_lim(ch="", masses=[]):
    out = []
    for m in masses:
        # print ch, m
        cmd = "combine -M Asymptotic -m %d -n .Zprime.%s LIMITS/%s/%d/htt_%s_0_13TeV.txt > /dev/null" % (m, ch, ch, m, ch)
        # print cmd
        os.system(cmd)
        out.append("higgsCombine.Zprime.%s.Asymptotic.mH%d.root" % (ch, m))

        # f = r.TFile(out[-1])
        # tree = f.Get("limit")
        # tree.Scan("mh:limit:quantileExpected", "quantileExpected > 0.0")
        # f.Close()
    return out


def filenames_ml(ch="", masses=[]):
    out = []

    outFile = "ml_results_%s.txt" % ch
    if os.path.exists(outFile):
        os.remove(outFile)

    for m in masses:
        #"--saveNLL --saveShapes --saveNormalizations"
        os.system('echo "\n%d" >> %s' % (m, outFile))
        cmd = "combine -M MaxLikelihoodFit -m %d -n .Zprime.%s LIMITS/%s/%d/htt_%s_0_13TeV.txt | grep -A 1 'Best fit r'" % (m, ch, ch, m, ch)
        os.system("%s >> %s" % (cmd, outFile))
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
        if chain.quantileExpected <= 0.0:
            continue
        key = round(chain.quantileExpected, 3)
        if key not in d:
            d[key] = {}
        d[key][chain.mh] = chain.limit
    return d


def dump(ch, d):
    masses = set(sum([x.keys() for x in d.values()], []))
    masses = sorted(list(masses))
    print "   ".join([ch.ljust(5)] + ["%5d" % m for m in masses])
    for quantile, mass_dict in sorted(d.iteritems()):
        row = ["%5.3f" % quantile]
        for m in masses:
            row.append("%5.3f" % mass_dict[m])
        print "   ".join(row)


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
        chain = chained(filenames_lim(ch=ch, masses=masses))
        dump(ch, limits(chain))

    for ch in chs:
        diff_nuisances(ch, filenames_ml(ch, masses))
