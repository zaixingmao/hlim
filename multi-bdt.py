#!/usr/bin/env python

import cfg
import os
import make_root_files

cats = cfg.cats()
workDir = cfg.workDir()
inDir = "root/bdt/3"
redirect = False


for mass in cfg.masses_spin0:
    for fileName in os.listdir(inDir):
        if ("_H%3d" % mass) not in fileName:
            continue

        dirName = fileName.replace("combined", "BDT").replace(".root", "")
        # print dirName
        os.system("rm -rf %s" % dirName)
        os.system("mkdir %s" % dirName)
        print "  (making .root file)"

        # WARNING: HACK!
        cfg.__stem = "%s/%s" % (inDir, fileName.replace(".root", "%s.root"))

        make_root_files.loop()

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
        for cat in cats.split():
            files.append("../test/tauTau_2jet%stag_prefit_8TeV_LIN.pdf" % cat)

        for f in files:
            os.system("cp -p %s/%s %s/" % (workDir, f, dirName))
