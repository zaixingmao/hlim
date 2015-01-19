#!/usr/bin/env python

import cfg
import os
import make_root_files
import determine_binning

cats = cfg.cats()
workDir = cfg.workDir()
redirect = False

fineBins = cfg._bdtBins

for mass in cfg.masses_spin0:
    for fileName in os.listdir(cfg.bdtDir):
        if ("_H%3d" % mass) not in fileName:
            continue

        dirName = fileName.replace("combined", "BDT").replace(".root", "")
        # print dirName
        os.system("rm -rf %s" % dirName)
        os.system("mkdir %s" % dirName)
        print "  (making .root file)"

        cfg._stem = "%s/%s" % (cfg.bdtDir, fileName.replace(".root", "%s.root"))

        # make histograms with very fine binning
        make_root_files.options.integrals = False
        make_root_files.options.contents = True
        make_root_files.options.unblind = False
        make_root_files.loop()

        # # then choose a coarser binning
        # cfg._bdtBins = determine_binning.bins()

        # # make histograms with this binning
        # make_root_files.options.contents = True
        # make_root_files.loop()

        # # replace fine bins for next mass point
        # cfg._bdtBins = fineBins

        # continue
        print "  (running limit)"
        args = ["cd %s &&" % workDir,
                "./go.py",
                "--file=%s" % cfg.outFileName(var="BDT", cuts={}),
                "--full",
                "--postfitonlyone",
                "--masses='%s'" % mass,
                "--categories='%s'" % cats,
                ]
        if redirect:
            args.append("> %s/limit.out" % dirName)
        os.system(" ".join(args))

        files = ["tt_ggHTohh-limit.pdf", "tt_ggHTohh-limit.txt"]
        # for cat in cats.split():
        #     files.append("../test/tauTau_2jet%stag_prefit_8TeV_LIN.pdf" % cat)

        for f in files:
            os.system("cp -p %s/%s %s/" % (workDir, f, dirName))
