import os
import sys
from root_dest import root_dest

lumi     = 19.7   # /fb
rescaleX = False

substring_signal_example = "2B350"

masses_spin0 = range(260, 360, 10) #+ [500, 700]
masses_spin2 = [500, 700]

categories = {#"MM_LM": "tauTau_2jet2tag",
              "2M": "tauTau_2jet2tag",
              "1M": "tauTau_2jet1tag",
              #"0M": "tauTau_2jet0tag",
              }

bdtDir = "root/bdt/4"

# used to determine coarser binning;
# WARNING: gets modified by multi-bdt.py
#_bdtBins = (1000, -1.0, 1.0)
_bdtBins = (7, -0.6, 0.1)

# WARNING: gets modified by multi-bdt.py
_stem = "root/combined_iso1.0_one1To4_pt_%s__withDYEmbed_massWindow_with0tag.root"

def files():
    s = ""
    return {"":                             _stem % s,
            "_CMS_scale_t_tautau_8TeVUp":   _stem % "",
            "_CMS_scale_t_tautau_8TeVDown": _stem % "",
            "_CMS_scale_j_8TeVUp":   _stem % s,
            "_CMS_scale_j_8TeVDown": _stem % s,
            "_CMS_scale_btag_8TeVUp": _stem % s,
            "_CMS_scale_btag_8TeVDown": _stem % s,
            }

__fakeSignals = {"ggAToZhToLLTauTau": masses_spin0,
                 "ggAToZhToLLBB": [250] + masses_spin0,
                 "ggGravitonTohhTo2Tau2B": [270, 300, 500, 700, 1000],
                 "ggRadionTohhTo2Tau2B":   [     300, 500, 700, 1000],
                 "bbH": range(90, 150, 10) + [160, 180, 200, 250, 300, 350, 400],
                 }

fakeBkgs = ["ggH125", "qqH125", "VH125", "W", "ZJ", "ZL"][:-1]


def procs():
    # first character '-' means subtract rather than add
    out = {"TT": ["tt", "tt_semi", "tthad"],
           "*VV": ["ZZ", "WZJetsTo2L2Q", "WW", "WZ3L", "zzTo2L2Nu", "zzTo4L"],
           #"W": ["W2JetsToLNu", "W3JetsToLNu", "W4JetsToLNu"],  # W1 provides no events
           #"ZTT": ["DYJetsToLL"],
           #"ZTT": ["DY1JetsToLL", "DY2JetsToLL", "DY3JetsToLL", "DY4JetsToLL"],
           #"*singleT": ["t", "tbar"],
           "ZTT": ["DY_embed", "-tt_embed"],
           #"*ZLL": ["ZLL"],
           "QCD": ["dataOSRelax", "-MCOSRelax"],
           "data_obs": ["dataOSTight"],
           }

    for m in masses_spin0:
        out["ggHTohhTo2Tau2B%3d" % m] = ["H2hh%3d" % m]

    for p in fakeBkgs + fakeSignalList():
        out[p] = [p]

    return out


def procs2():
    # first character '*' means unit normalize and then use factor
    return {"VV": ["*VV", "*singleT"][:1],
            # "ZLL": ["*ZLL"],
            }


def fakeSignalList():
    out = []
    for stem, masses in __fakeSignals.iteritems():
        for m in masses:
            out.append("%s%d" % (stem, m))
    return out


def isData(proc):
    return proc.startswith("data")


def isDataEmbedded(proc):
    return proc.startswith("DY_embed")  # fixme: dimuon


def isMcEmbedded(proc):
    return proc.endswith("tt_embed")  # first character may be minus sign


def isSignal(proc):
    return any([proc.startswith(p) for p in ["ggHTo", "ggATo", "ggGraviton", "ggRadion", "bbH"]])


def cats():
    return " ".join([s[-4] for s in sorted(categories.values())])


def workDir():
    return "/".join(__file__.split("/")[:-1])



def variables():
    fm_bins_old= (4, 250.0, 410.0)
    fm_bins_lt = [200, 250, 270, 290, 310, 330, 350, 370, 390, 410, 430, 450, 500, 550, 600, 650, 700]
    fm_bins_tt = [200, 250, 280, 310, 340, 370, 400, 500, 600, 700]#[:-2]

    it_sv_bins_cat1_old = range(0, 200, 10) + range(200, 375, 25)
    it_sv_bins_cat2_old = range(0, 210, 20) + [250, 300, 350]
    it_sv_bins_cat1_new = range(0, 200, 10) + range(200, 375, 25)
    it_sv_bins_cat2_new = range(0, 200, 20) + range(200, 400, 50)
    it_fm_bins_cats = range(0, 510, 20) + range(550, 1050, 50)


    preselection = {}
    fMass = {"fMassKinFit": (0.0, None)}
    #chi2 = {"chi2KinFit2": (0.0, 10.0)}
    mass_windows = {"mJJ": (70.0, 150.0), "svMass": (90.0, 150.0)}
    mass_windows.update(fMass)

    ## bins are either a tuple: (n, xMin, xMax)
    ##  or
    ## a list of bin lower edges

    out = [#{"var": "svMass",      "bins": it_sv_bins_cat2_new, "cuts": {}},
           #{"var": "fMassKinFit", "bins": fm_bins_tt, "cuts": mass_windows},
           {"var": "BDT", "bins": _bdtBins, "cuts": preselection},
           ]

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
    if len(set(files().values())) <= 2:
        print "FIXME: include variations"

    if __fakeSignals:
        print "FIXME: include", sorted(__fakeSignals.keys())

    if fakeBkgs:
        print "FIXME: include", sorted(fakeBkgs)

    lst = []
    for v in procs().values():
        if type(v) != list:
            sys.exit("ERROR: type of '%s' is not list." % str(v))
        else:
            lst += v
    if len(set(lst)) != len(lst):
        sys.exit("ERROR: procs values has duplicates: %s." % str(sorted(lst)))


complain()
