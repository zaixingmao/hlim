#!/usr/bin/env python

import cfg
import root_dest
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


def make_root_file(dirName, fileName, variable):
    # print dirName
    os.system("rm -rf %s" % dirName)
    os.system("mkdir %s" % dirName)
    print "  (making .root file)"

    # make histograms with very fine binning
    make_root_files.ugly_setup()
    make_root_files.options.integrals = False
    make_root_files.options.contents = False
    make_root_files.options.unblind = options.unblind
    if not options.unblind:
        print "BLIND!"

    variable["bins"] = (1000, -1.0, 1.0)
    make_root_files.go(variable)

    # then choose a coarser binning
    fine_histo = histo(fileName=fileName,
                       subdir="tauTau_2jet2tag",
                       name="sum_b")

    # variable["bins"] = determine_binning.fixed_width(fine_histo)
    variable["bins"] = determine_binning.variable_width(fine_histo)

    # make histograms with this binning
    make_root_files.options.contents = True
    make_root_files.go(variable)


def plot(dirName, fileName, xtitle, mass):
    print "  (plotting histograms)"
    cmd = " ".join(["cd %s && " % dirName,
                    "../compareDataCards.py",
                    "--xtitle=%s" % xtitle,
                    "--file1=%s" % fileName,
                    "--file2=%s" % fileName,
                    "--masses=%3d" % mass,
                    ])
    os.system(cmd)


def compute_limit(dirName, fileName, mass):
    cats = cfg.cats()
    workDir = cfg.workDir()
    print "  (running limit)"
    args = ["cd %s &&" % workDir,
            "./go.py",
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
    variable = {"var": "BDT",
                #"bins": (7, -0.6, 0.1),
                "cuts": {},
                }

    # clean up previous results
    os.system("rm -rf %s" % root_dest.bdt_tmp)

    for mass in cfg.masses_spin0:
        for fileIn in os.listdir(cfg.bdtDir):
            if ("_H%3d_%s" % (mass, suffix)) not in fileIn:
                continue

            cfg._stem = "%s/%s" % (cfg.bdtDir, fileIn.replace(suffix, "%s.root"))

            variable["tag"] = "%3d" % mass
            fileOut = cfg.outFileName(**variable)

            dirOut = fileIn.replace("combined", variable["var"]).replace("_%s" % suffix, "")
            if not options.reuse:
                make_root_file(dirOut, fileOut, variable)
            root_dest.copy(src=fileOut, link=True)
            plot(dirOut, fileOut, xtitle=variable["var"]+variable["tag"], mass=mass)
            compute_limit(dirOut, fileOut, mass)


def opts():
    import optparse
    parser = optparse.OptionParser()

    parser.add_option("--unblind",
                      dest="unblind",
                      default=False,
                      action="store_true",
                      help="use obs when computing expected limits")

    parser.add_option("--reuse-existing-files",
                      dest="reuse",
                      default=False,
                      action="store_true",
                      help="do not call make_root_files")

    options, args = parser.parse_args()
    return options


if __name__ == "__main__":
    options = opts()
    go()
