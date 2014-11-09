#!/usr/bin/env python

from cfg import masses_spin0, categories
import os

vars = ["",
        #"fMassKinFit_0.2.BDT_300_3",
        #"fMassKinFit_0.0.BDT_300_3",
        #"fMassKinFit_90.0.mJJ.140.0_90.0.svMass.140.0",
        "fMassKinFit_0.0.chi2KinFit2.10.0",
        #"fMassKinFit_0.2.CSVJ2.0.7_90.0.mJJ.140.0_90.0.svMass.140.0",
        #"fMassKinFit_0.7.CSVJ2_90.0.mJJ.140.0_90.0.svMass.140.0",
        #"BDT_260",
        #"BDT_270",
        #"BDT_280",
        #"BDT_290",
        #"BDT_300",
        #"BDT_310",
        #"BDT_320",
        #"BDT_330",
        #"BDT_340",
        #"BDT_350",
        ]

masses = " ".join(["%s" % x for x in masses_spin0])
cats = " ".join(["%s" % i for i in categories])

workDir = "/".join(__file__.split("/")[:-1])
for var in vars:
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
                        "--masses='%s'" % masses,
                        "--categories='%s'" % cats,
                        ]))

    files = ["tt_ggHTohh-limit.pdf", "tt_ggHTohh-limit.txt"]
    for iCat in categories:
        files.append("../test/tauTau_2jet%dtag_prefit_8TeV_LIN.pdf" % iCat)

    for f in files:
        os.system("cp -p %s/%s %s/" % (workDir, f, var))
