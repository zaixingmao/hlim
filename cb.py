#!/usr/bin/env python

import cfg
import os

if __name__ == "__main__":
    cats = cfg.cats()
    workDir = cfg.workDir()

    cmd = " ".join(["cd %s &&" % workDir,
                    "./go.py",
                    "--full",
                    "--postfitonlyone",
                    #"--alsoObs",
                    "--masses='%s'" % " ".join(["%s" % x for x in cfg.masses_spin0]),
                    "--categories='%s'" % cats,
                    ])

    # print cmd
    os.system(cmd)

    # for cat in cats.split():
    #     files.append("../test/tauTau_2jet%stag_prefit_8TeV_LIN.pdf" % cat)

    d = cfg.variable()
    dirName = "%s_%s" % (d["var"], cfg.cutDesc(d["cuts"]))
    os.system("rm -rf %s" % dirName)
    os.system("mkdir %s" % dirName)

    for ext in [".pdf", ".txt", ".root"]:
        os.system("cp -p %s/tt_ggHTohh-limit%s %s/" % (workDir, ext, dirName))
