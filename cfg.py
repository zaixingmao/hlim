import os
import sys

if "CMSSW_BASE" not in os.environ:
    sys.exit("Set up the CMSSW environment.")

root_dest = "%s/src/auxiliaries/shapes/Brown" % os.environ["CMSSW_BASE"]

lumi     = 19.7   # /fb
rescaleX = False

substring_signal_example = "2B350"
signalXsPrefix = "H2hh"
signalXs = 1.0e3  # fb (= 1.0 pb)

#masses_spin0 = [260, 300, 350]
masses_spin0 = range(260, 360, 10) #+ [500, 700]
masses_spin2 = [500, 700]

categories = {#"MM_LM": "tauTau_2jet2tag",
              "2M": "tauTau_2jet2tag",
              "1M": "tauTau_2jet1tag",
              }

files = {"":                             "root/combined_inclusiveDY.root",
         "_CMS_scale_t_tautau_8TeVUp":   "root/combined_up.root",
         "_CMS_scale_t_tautau_8TeVDown": "root/combined_down.root",
         }

__fakeSignals = ["ggAToZhToLLTauTau", "ggAToZhToLLBB", "bbH"]

def procs():
    out = {"TT": ["tt_full", "tt_semi"],
           "VV": ["ZZ"],
           "W": ["W1JetsToLNu", "W2JetsToLNu", "W3JetsToLNu"],
           "ZTT": ["DYJetsToLL"],
           #"ZTT": ["DY1JetsToLL", "DY2JetsToLL", "DY3JetsToLL", "DY4JetsToLL"],
           "QCD": ["dataOSRelax"],
           }

    out["bbH250"] = ["bbH250"]
    for m in masses_spin0:
        out["ggHTohhTo2Tau2B%3d" % m] = ["H2hh%3d" % m]
        for stem in __fakeSignals:
            sig = "%s%3d" % (stem, m)
            out[sig] = [sig]

    return out


def isSignal(proc):
    return any([proc.startswith(p) for p in ["ggHTo", "ggATo", "bbH"]])


def isAntiIsoData(proc):
    return proc == "dataOSRelax"


def cats():
    return " ".join([s[-4] for s in categories.values()])


def workDir():
    return "/".join(__file__.split("/")[:-1])



def variables():
    preselection = {}
    fMass = {"fMassKinFit": (0.0, None)}
    #chi2 = {"chi2KinFit2": (0.0, 10.0)}
    mass_windows = {"mJJ": (70.0, 150.0), "svMass": (90.0, 150.0)}
    mass_windows.update(fMass)

    out = [{"var": "svMass",      "bins": ( 14,   0.0, 350.0), "cuts": {}},
           #{"var": "fMassKinFit", "bins": ( 4, 250.0, 410.0), "cuts": fMass},
           {"var": "fMassKinFit", "bins": ( 4, 250.0, 410.0), "cuts": mass_windows},
           ##"var": "fMassKinFit", "bins": ( 4, 250.0, 410.0), "cuts": chi2},
           ]

    if False:
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


def complain():
    if len(set(files.values())) != 3:
        print "FIXME: include variations"

    print "FIXME: deal with 250"
    if __fakeSignals:
        print "FIXME: include", __fakeSignals

    lst = []
    for v in procs().values():
        if type(v) != list:
            sys.exit("ERROR: type of '%s' is not list." % str(v))
        else:
            lst += v
    if len(set(lst)) != len(lst):
        sys.exit("ERROR: procs values has duplicates: %s." % str(sorted(lst)))


complain()
