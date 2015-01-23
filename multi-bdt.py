#!/usr/bin/env python

import cfg
import os
import sys
import make_root_files
import determine_binning


def make_root_file(dirName):
    fineBins = (1000, -1.0, 1.0)

    # print dirName
    os.system("rm -rf %s" % dirName)
    os.system("mkdir %s" % dirName)
    print "  (making .root file)"

    cfg._bdtBins = fineBins

    # make histograms with very fine binning
    make_root_files.options.integrals = False
    make_root_files.options.contents = False
    make_root_files.options.unblind = unblind
    make_root_files.loop()

    # then choose a coarser binning
    cfg._bdtBins = determine_binning.bins()

    # make histograms with this binning
    make_root_files.options.contents = True
    make_root_files.loop()

    # replace fine bins for next mass point
    cfg._bdtBins = fineBins


def plot(dirName):
    print "  (plotting histograms)"
    cmd = " ".join(["cd %s && " % dirName,
                    "../compareDataCards.py",
                    "--xtitle=BDT",
                    "--file1=Brown/BDT.root",
                    "--file2=Brown/BDT.root",
                    ])
    os.system(cmd)


def compute_limit(mass, dirName):
    cats = cfg.cats()
    workDir = cfg.workDir()
    print "  (running limit)"
    args = ["cd %s &&" % workDir,
            "./go.py",
            "--file=%s" % cfg.outFileName(var=bdt, cuts={}),
            "--full",
            "--postfitonlyone",
            "--masses='%s'" % mass,
            "--categories='%s'" % cats,
            ]
    os.system(" ".join(args))

    files = ["tt_ggHTohh-limit.pdf", "tt_ggHTohh-limit.txt"]
    # for cat in cats.split():
    #     files.append("../test/tauTau_2jet%stag_prefit_8TeV_LIN.pdf" % cat)

    for f in files:
        os.system("cp -p %s/%s %s/" % (workDir, f, dirName))


def go(suffix="normal.root"):
    for mass in cfg.masses_spin0:
        for fileName in os.listdir(cfg.bdtDir):
            if ("_H%3d_%s" % (mass, suffix)) not in fileName:
                continue

            cfg._stem = "%s/%s" % (cfg.bdtDir, fileName.replace(suffix, "%s.root"))
            dirName = fileName.replace("combined", bdt).replace("_%s" % suffix, "")
            make_root_file(dirName)
            plot(dirName)
            compute_limit(mass, dirName)


if __name__ == "__main__":
    bdt = "BDT"
    unblind = False
    lst = cfg.variables()
    if len(lst) != 1 or lst[0]["var"] != bdt:
        sys.exit("FATAL: please edit cfg.variables() to use 'BDT'.")

    if not unblind:
        print "BLIND!"

    go()
