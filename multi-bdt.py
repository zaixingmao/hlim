#!/usr/bin/env python

import cfg
import os


cats = cfg.cats()
workDir = cfg.workDir()
inDir = "root"
redirect = False

for mass in cfg.masses_spin0:
    for fileName in os.listdir(inDir):
        if ("_H%3d_" % mass) not in fileName:
            continue

        dirName = fileName.replace("combined", "BDT").replace(".root", "")
        print dirName
        os.system("rm -rf %s" % dirName)
        os.system("mkdir %s" % dirName)
        print "  (root)"
        cmd = "./make_root_files.py %s/%s" % (inDir, fileName)

        if redirect:
            cmd += " > %s/yields.txt" % dirName
        os.system(cmd)

        print "  (limit)"
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
