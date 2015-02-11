#!/usr/bin/env python

import cfg
import os
import sys
import make_root_files
import determine_binning
import ROOT as r


def histo(fileName, subdir="", name=""):
    f = r.TFile(fileName)
    h = f.Get("%s/%s" % (subdir, name)).Clone()
    h.SetDirectory(0)
    f.Close()
    return h


def make_root_file(dirName, tag=""):
    # print dirName
    os.system("rm -rf %s" % dirName)
    os.system("mkdir %s" % dirName)
    print "  (making .root file)"

    variable = cfg.variable()
    variable["tag"] = tag  # used in filename

    # make histograms with very fine binning
    make_root_files.options.integrals = False
    make_root_files.options.contents = False
    make_root_files.options.unblind = unblind
    variable["bins"] = (1000, -1.0, 1.0)
    make_root_files.go(variable)

    # then choose a coarser binning
    fine_histo = histo(fileName=cfg.outFileName(**variable),
                       subdir="tauTau_2jet2tag",
                       name="sum_b")

    # variable["bins"] = determine_binning.fixed_width(fine_histo)
    variable["bins"] = determine_binning.variable_width(fine_histo)

    # make histograms with this binning
    make_root_files.options.contents = True
    make_root_files.go(variable)


def plot(dirName, mass):
    print "  (plotting histograms)"
    cmd = " ".join(["cd %s && " % dirName,
                    "../compareDataCards.py",
                    "--xtitle=BDT%3d" % mass,
                    "--file1=Brown/BDT.root",
                    "--file2=Brown/BDT.root",
                    "--masses=%3d" % mass,
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
            "--BDT",
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
            make_root_file(dirName, tag="%3d" % mass)
            plot(dirName, mass)
            compute_limit(mass, dirName)


if __name__ == "__main__":
    bdt = "BDT"
    unblind = False
    if cfg.variable()["var"] != bdt:
        sys.exit("FATAL: please edit cfg.variable() to use 'BDT'.")

    if not unblind:
        print "BLIND!"

    go()
