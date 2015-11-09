#!/usr/bin/env python

import cfg
import root_dest
import os

if __name__ == "__main__":
    cats = cfg.cats()
    workDir = cfg.workDir()
    d = cfg.variable()

    root_dest.copy(src=cfg.outFileName(var=d["var"], cuts=d["cuts"]), link=True)

    cmd = " ".join(["cd %s &&" % workDir,
                    "./go.py",
                    "--full",
                    "--alsoObs",
                    "--masses='%s'" % " ".join(["%s" % x for x in cfg.masses]),
                    "--categories='%s'" % cats,
                    ])

    # print cmd
    os.system(cmd)

    # for cat in cats.split():
    #     files.append("../test/tauTau_2jet%stag_prefit_8TeV_LIN.pdf" % cat)

    dirName = "%s_%s" % (d["var"], cfg.cutDesc(d["cuts"]))
    os.system("rm -rf %s" % dirName)
    os.system("mkdir %s" % dirName)

    for ext in [".pdf", ".txt", ".root"]:
        os.system("cp -p %s/tt_ggHTohh-limit%s %s/" % (workDir, ext, dirName))
