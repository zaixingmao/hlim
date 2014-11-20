#!/usr/bin/env python

import cfg
import os

cats = cfg.cats()
workDir = cfg.workDir()

for d in cfg.variables():
    masses = cfg.masses_spin0
    if "BDT" in d["var"] and 7 <= len(d["var"]):
        m = int(d["var"][4:7])
        masses = filter(lambda x: abs(x-m) < 11, masses)
    masses = " ".join(["%s" % x for x in masses])

    dirName = "%s_%s" % (d["var"], cfg.cutDesc(d["cuts"]))
    os.system("rm -rf %s" % dirName)
    os.system("mkdir %s" % dirName)
    os.system(" ".join(["cd %s &&" % workDir,
                        "./go.py",
                        "--file=%s" % cfg.outFileName(var=d["var"], cuts=d["cuts"]),
                        "--full",
                        "--postfitonlyone",
                        "--masses='%s'" % masses,
                        "--categories='%s'" % cats,
                        ]))

    files = ["tt_ggHTohh-limit.pdf", "tt_ggHTohh-limit.txt"]
    for cat in cats.split():
        files.append("../test/tauTau_2jet%stag_prefit_8TeV_LIN.pdf" % cat)

    for f in files:
        os.system("cp -p %s/%s %s/" % (workDir, f, dirName))
