#!/usr/bin/env python

from masses import spin0
import os

vars = [#"fMassKinFit_0.2.BDT_300_3",
        #"fMassKinFit_0.0.BDT_300_3",
        #"fMassKinFit_90.0.mJJ.140.0_90.0.svMass.140.0",
        #"fMassKinFit_0.2.CSVJ2.0.7_90.0.mJJ.140.0_90.0.svMass.140.0",
        #"fMassKinFit_0.7.CSVJ2_90.0.mJJ.140.0_90.0.svMass.140.0",
        "BDT_260_8Vars",
        "BDT_270_8Vars",
        "BDT_280_8Vars",
        "BDT_290_8Vars",
        "BDT_300_8Vars",
        "BDT_310_8Vars",
        "BDT_320_8Vars",
        "BDT_330_8Vars",
        "BDT_340_8Vars",
        "BDT_350_8Vars",
        "BDT_500_8Vars",
        "BDT_700_8Vars",
        ]

masses = " ".join(["%s" % x for x in spin0])

workDir = "/".join(__file__.split("/")[:-1])
for var in vars:
    os.system("rm -rf %s" % var)
    os.system("mkdir %s" % var)
    os.system("cd %s && ./go.py --file=root/0x260_%s.root --full --masses='%s'" % (workDir, var, masses))

    files = ["", "tt_ggHTohh-limit.pdf", "tt_ggHTohh-limit.txt", "test/tauTau_2jet2tag_prefit_8TeV_LIN.pdf"]
    files = (" %s/" % workDir).join(files)
    os.system("cp -p %s %s/" % (files, var))
