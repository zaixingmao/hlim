#!/usr/bin/env python

import cfg
import os

cats = cfg.cats()
workDir = cfg.workDir()

if __name__ == "__main__":
    d = cfg.variable()
    masses = cfg.masses_spin0

    dirName = "%s_%s" % (d["var"], cfg.cutDesc(d["cuts"]))
    os.system("rm -rf %s" % dirName)
    os.system("mkdir %s" % dirName)
    aux = "%s/src/auxiliaries/shapes" % os.environ["CMSSW_BASE"]

    it = "%s/Italians/htt_tt.inputs-Hhh-8TeV_m_ttbb_kinfit_KinFitConvergedWithMassWindow.root" % aux
    #br = "%s/Brown/fMassKinFit_0.0.fMassKinFit_70.0.mJJ.150.0_90.0.svMass.150.0_new.root" % aux
    br = cfg.outFileName(var=d["var"], cuts=d["cuts"])

    cmd = " ".join(["cd %s &&" % workDir,
                    "./go.py",
                    "--file=%s" % br,
                    "--full",
                    "--postfitonlyone",
                    #"--alsoObs",
                    "--masses='%s'" % " ".join(["%s" % x for x in masses]),
                    "--categories='%s'" % cats,
                    ])

    # print cmd
    os.system(cmd)

    files = ["tt_ggHTohh-limit.pdf", "tt_ggHTohh-limit.txt"]
    # for cat in cats.split():
    #     files.append("../test/tauTau_2jet%stag_prefit_8TeV_LIN.pdf" % cat)

    for f in files:
        os.system("cp -p %s/%s %s/" % (workDir, f, dirName))
