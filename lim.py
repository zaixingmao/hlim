#!/usr/bin/env python

import os
import ROOT as r


def filenames(ch="", masses=[]):
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


if __name__ == "__main__":
    for ch in ["et", "em"]:
        chain = chained(filenames(ch=ch, masses=range(500, 2500, 500)))
        dump(ch, limits(chain))
