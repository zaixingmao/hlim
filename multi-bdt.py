#!/usr/bin/env python

import cfg
import root_dest
import os
import sys
import make_root_files
import determine_binning
import compareDataCards
import ROOT as r


def histo(fileName, subdir="", name=""):
    f = r.TFile(fileName)
    path = "%s/%s" % (subdir, name)
    h1 = f.Get(path)
    if not h1:
        sys.exit("path %s:%s not found" % (fileName, path))
    h = h1.Clone()
    h.SetDirectory(0)
    f.Close()
    return h


def make_root_file(dirName, fileName, variable, ini_bins=None, subdir="", minWidth=None, threshold=None, catlist=None):
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

    variable["bins"] = ini_bins

    staticBinning = (minWidth is None) or (threshold is None)
    if staticBinning:
        make_root_files.options.contents = True

    make_root_files.go(variable, categoryWhitelist=catlist, skipVariations=not staticBinning)

    if staticBinning:
        return

    # then choose a coarser binning
    fine_histo = histo(fileName=fileName,
                       subdir=subdir,
                       name="sum_b")

    # variable["bins"] = determine_binning.fixed_width(fine_histo)
    variable["bins"] = determine_binning.variable_width(h=fine_histo, minWidth=minWidth, threshold=threshold)
    print "binning_____"
    print variable["bins"]
    # make histograms with this binning
    make_root_files.options.contents = True
    make_root_files.go(variable, categoryWhitelist=catlist)


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


def compute_limit(dirName, fileName, mass, BDT=True):
    cats = cfg.cats()
    workDir = cfg.workDir()
    print "  (running limit)"

    if BDT:
        args = ["cd %s &&" % workDir,
                "./go.py",
                "--full",
                "--alsoObs",
#                 "--postfitonlyone",
                "--masses='%s'" % mass,
                "--categories='%s'" % cats,
                "--BDT",
                ]
    else:

        args = ["cd %s &&" % workDir,
                "./go.py",
                "--full",
                "--alsoObs",
                "--masses='%s'" % mass,
                "--categories='%s'" % cats,
                ]

    os.system(" ".join(args))

    files = ["tt_ggHTohh-limit.pdf", "tt_ggHTohh-limit.txt"]
    # for cat in cats.split():
    #     files.append("../test/tauTau_2jet%stag_prefit_8TeV_LIN.pdf" % cat)

    for f in files:
        os.system("cp -p %s/%s %s/" % (workDir, f, dirName))


def go_bdt(suffix="normal.root"):
    variable = {"var": "BDT",
                #"bins": (7, -0.6, 0.1),
                "cuts": {},
                }

    # clean up previous results
    os.system("rm -rf %s" % root_dest.bdt_tmp)

    for mass in cfg.masses:
        for fileIn in os.listdir(cfg.bdtDir):
            if ("_H%3d_%s" % (mass, suffix)) not in fileIn:
                continue

            cfg._stem = "%s/%s" % (cfg.bdtDir, fileIn.replace(suffix, "%s.root"))

            variable["tag"] = "%3d" % mass
            fileOut = cfg.outFileName(**variable)

            dirOut = fileIn.replace("combined", variable["var"]).replace("_%s" % suffix, "")
            if not options.reuse:
                make_root_file(dirOut, fileOut, variable, ini_bins=(1000, -1.0, 1.0), subdir="tauTau_2jet2tag", minWidth=0.1, threshold=0.25)
            root_dest.copy(src=fileOut, link=True)
            plot(dirOut, fileOut, xtitle=variable["var"]+variable["tag"], mass=mass)
            compute_limit(dirOut, fileOut, mass)


def go_cb(suffix="normal.root"):
    variable = {"var": "fMassKinFit",
                "cuts": {"fMassKinFit": (0.0, None), "mJJ": (70.0, 150.0), "svMass": (90.0, 150.0)},
                }
    mass = "%s" % " ".join(["%s" % x for x in cfg.masses])

    fileOut = cfg.outFileName(**variable)
    dirOut = "%s_%s" % (variable["var"], cfg.cutDesc(variable["cuts"]))
    if not options.reuse:
        make_root_file(dirOut, fileOut, variable, ini_bins=(1000, 250.0, 1000.0), subdir="tauTau_2jet2tag", minWidth=0.1, threshold=0.25)
    d = cfg.variable()
    root_dest.copy(src=cfg.outFileName(var=d["var"], cuts=d["cuts"]), link=True)
#    plot(dirOut, fileOut, xtitle=variable["var"], mass=cfg.masses[0])
    compute_limit(dirOut, fileOut, mass, False)


def go_zp(suffix="normal.root"):
    variable = {"var": "m_effective",
                "cuts": {# "tauTightIso": (0.5, None),
                         # "eleRelIso": (None, 0.15),
                         # "pfMEt": (30, None),
                         # "pZetaCut": (-50, None),
                         # "nCSVL": (None, 0.5),
                         # "cosDPhi": (None, -0.95),

                         "~tauDecayMode": (4.5, 9.5),
                         },
                }

    fileOut = cfg.outFileName(**variable)
    dirOut = "%s_%s" % (variable["var"], cfg.cutDesc(variable["cuts"]))

    for ch, subdir in cfg.categories.iteritems():
        variations = set([key.replace("Up", "").replace("Down", "") for key in cfg.files(ch).keys()])

        # ini_bins = [73.0, 98.0, 123.0, 148.0, 173.0, 198.0, 223.0, 248.0, 273.0, 298.0, 335.0, 360.0, 390.0, 425.0, 495.0, 520.0]
        # make_root_file(dirOut, fileOut, variable, ini_bins=ini_bins, subdir=subdir, catlist=[ch])
        make_root_file(dirOut, fileOut, variable, ini_bins=(1000, 0.0, 1000.0), subdir=subdir, minWidth=25.0, threshold=0.20, catlist=[ch])
        root_dest.copy(src=cfg.outFileName(var=variable["var"], cuts=variable["cuts"]), channel=ch, era="13TeV", tag="Zp")

        args = "--file1=Brown/htt_%s.inputs-Zp-13TeV.root --file2='' --masses='500 1000 1500 2000' --logy --xtitle='%s (GeV)'" % (ch, variable["var"])
        args += " --bands=%s" % ",".join([v.replace("_CMS", "CMS") for v in variations])

        # os.system("./compareDataCards.py %s" % args)
        # os.system("cp -p comparison_%s.pdf ~/public_html/comparison_%s_%s.pdf" % (variable["var"], variable["var"], ch))

        os.system("./compareDataCards.py %s --raw-yields" % args)

        for prefix in variations:
            prefix2 = compareDataCards.shortened(prefix)
            os.system("cp -p comparison_%s%s.pdf ~/public_html/%s%s_%s_raw.pdf" % (variable["var"], prefix2, variable["var"], prefix2, ch))


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
    # go_bdt()
    # go_cb()
    go_zp()
