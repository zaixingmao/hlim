#!/usr/bin/env python

from cfg import masses_spin0, categories, multi_vars
import os

masses = " ".join(["%s" % x for x in masses_spin0])
cats = " ".join(["%s" % i for i in categories])

workDir = "/".join(__file__.split("/")[:-1])
for var in multi_vars:
    if not var:
        continue

    if "BDT" in var:
        m = int(var[4:7])
        masses = filter(lambda x: abs(x-m) < 11, masses_spin0)
        masses = " ".join(["%s" % x for x in masses])

    os.system("rm -rf %s" % var)
    os.system("mkdir %s" % var)
    os.system(" ".join(["cd %s &&" % workDir,
                        "./go.py",
                        "--file=root/%s.root" % var,
                        "--full",
                        "--postfitonlyone",
                        "--masses='%s'" % masses,
                        "--categories='%s'" % cats,
                        ]))

    files = ["tt_ggHTohh-limit.pdf", "tt_ggHTohh-limit.txt"]
    for iCat in categories:
        files.append("../test/tauTau_2jet%dtag_prefit_8TeV_LIN.pdf" % iCat)

    for f in files:
        os.system("cp -p %s/%s %s/" % (workDir, f, var))
