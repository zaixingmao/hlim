import os
import sys

if "CMSSW_BASE" not in os.environ:
    sys.exit("Set up the CMSSW environment.")

root_dest = "%s/src/auxiliaries/shapes/Brown" % os.environ["CMSSW_BASE"]

#masses_spin0 = [260, 300, 350][:1]
masses_spin0 = range(260, 360, 10) #+ [500, 700]
masses_spin2 = [500, 700]

categories = {#"MM_LM": "tauTau_2jet2tag",
              "2M": "tauTau_2jet2tag",
              "1M": "tauTau_2jet1tag",
              }


def cutDesc(cuts):
    descs = []
    for cutVar, (cutMin, cutMax) in sorted(cuts.iteritems()):
        cutDesc = cutVar
        if cutMin is not None:
            cutDesc = "%.1f.%s" % (cutMin, cutDesc)
        if cutMax is not None:
            cutDesc = "%s.%.1f" % (cutDesc, cutMax)
        descs.append(cutDesc)
    return "_".join(descs)


def variables():
    preselection = {}
    mass_windows = {"mJJ": (70.0, 150.0), "svMass": (90.0, 150.0), "fMassKinFit": (0.0, None)}
    chi2 = {"chi2KinFit2": (0.0, 10.0)}

    out = [{"var": "fMassKinFit", "bins": ( 4, 250.0, 410.0), "cuts": mass_windows},
           {"var": "fMassKinFit", "bins": ( 4, 250.0, 410.0), "cuts": chi2},
           ]

    if False:
        for var, bins in [("BDT_260", (8, -0.6, 0.2)),
                          ("BDT_270", (8, -0.6, 0.2)),
                          ("BDT_280", (8, -0.6, 0.2)),
                          ("BDT_290", (8, -0.6, 0.2)),
                          ("BDT_300", (8, -0.6, 0.2)),
                          ("BDT_310", (8, -0.6, 0.2)),
                          ("BDT_320", (8, -0.6, 0.2)),
                          ("BDT_330", (8, -0.6, 0.2)),
                          ("BDT_340", (8, -0.6, 0.2)),
                          ("BDT_350", (8, -0.6, 0.2)),
                          ]:
            out.append({"var": var, "bins": bins, "cuts": preselection})
    return out


multi_vars = ["",
              #"fMassKinFit_0.0.chi2KinFit2.10.0",
              #"fMassKinFit_70.0.mJJ.150.0_90.0.svMass.150.0",
              "fMassKinFit_0.0.fMassKinFit_70.0.mJJ.150.0_90.0.svMass.150.0",
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
