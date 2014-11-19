import os
import sys

if "CMSSW_BASE" not in os.environ:
    sys.exit("Set up the CMSSW environment.")


def isSignal(proc):
    return any([proc.startswith(p) for p in ["H2hh", "ggA", "bbH"]])


def isAntiIsoData(proc):
    return proc == "dataOSRelax"


root_dest = "%s/src/auxiliaries/shapes/Brown" % os.environ["CMSSW_BASE"]

substring_signal_example = "350"
lumi     = 19.7   # /fb

signalXsPrefix = "H2hh"
signalXs = 1.0e3  # fb (= 1.0 pb)

masses_spin0 = [260, 300, 350][-1:]
#masses_spin0 = range(260, 360, 10) #+ [500, 700]
masses_spin2 = [500, 700]

categories = {#"MM_LM": "tauTau_2jet2tag",
              "2M": "tauTau_2jet2tag",
              "1M": "tauTau_2jet1tag",
              }


def variables():
    preselection = {}
    mass_windows = {"mJJ": (70.0, 150.0), "svMass": (90.0, 150.0), "fMassKinFit": (0.0, None)}
    chi2 = {"chi2KinFit2": (0.0, 10.0)}

    out = [#{"var": "fMassKinFit", "bins": ( 4, 250.0, 410.0), "cuts": mass_windows},
           #"var": "fMassKinFit", "bins": ( 4, 250.0, 410.0), "cuts": chi2},
           ]

    if True:
        for var, bins in [("BDT", (8, -0.6, 0.2)),
                          #("BDT_270", (8, -0.6, 0.2)),
                          #("BDT_280", (8, -0.6, 0.2)),
                          #("BDT_290", (8, -0.6, 0.2)),
                          #("BDT_300", (8, -0.6, 0.2)),
                          #("BDT_310", (8, -0.6, 0.2)),
                          #("BDT_320", (8, -0.6, 0.2)),
                          #("BDT_330", (8, -0.6, 0.2)),
                          #("BDT_340", (8, -0.6, 0.2)),
                          #("BDT_350", (8, -0.6, 0.2)),
                          ]:
            out.append({"var": var, "bins": bins, "cuts": preselection})
    return out


def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != 17:
            raise e


def outFileName(sFactor=0, sKey="", var="", cuts={}):
    stem = root_dest + "/"
    mkdir(stem)

    if sFactor:
        print "FIXME: sFactor"
        stem += "%dx%s" % (sFactor, sKey.replace("H2hh", ""))
    stem += var
    if cutDesc(cuts):
        stem += "_%s" % cutDesc(cuts)
    return "%s.root" % stem


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
