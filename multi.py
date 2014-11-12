#!/usr/bin/env python

import cfg
import os

cats = " ".join([s[-4] for s in cfg.categories.values()])

workDir = "/".join(__file__.split("/")[:-1])
for var in cfg.multi_vars:
    if not var:
        continue

    masses = cfg.masses_spin0
    if "BDT" in var:
        m = int(var[4:7])
        masses = filter(lambda x: abs(x-m) < 11, masses)
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
    for cat in cats.split():
        files.append("../test/tauTau_2jet%stag_prefit_8TeV_LIN.pdf" % cat)

    for f in files:
        os.system("cp -p %s/%s %s/" % (workDir, f, var))
