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
              # "0M": "tauTau_2jet0tag",
              }

bdtDir = "root/bdt/7"
# bdtDir = "/nfs_scratch/zmao/samples_new/forDataCard/BDT"

# WARNING: these two variables get modified by multi-bdt.py
_bdtBins = (7, -0.6, 0.1)
_stem = "root/cb/4/combined_iso1.0_one1To4_pt_%s__withDYEmbed_massWindow.root"
# _stem = "/nfs_scratch/zmao/samples_new/forDataCard/combined_iso1.0_one1To4_pt_%s__withDYEmbed.root"


def files(variable=""):
    assert variable
    s = "normal"
    return {"":                             _stem % s,
            "_CMS_scale_t_tautau_8TeVUp":   _stem % "tauUp",
            "_CMS_scale_t_tautau_8TeVDown": _stem % "tauDown",
            "_CMS_scale_j_8TeVUp":   _stem % "jetUp",
            "_CMS_scale_j_8TeVDown": _stem % "jetDown",
            "_CMS_scale_btagEff_8TeVUp": _stem % "bSysUp",
            "_CMS_scale_btagEff_8TeVDown": _stem % "bSysDown",
            "_CMS_scale_btagFake_8TeVUp": _stem % "bMisUp",
            "_CMS_scale_btagFake_8TeVDown": _stem % "bMisDown",
            }


__fakeSignals = {"ggAToZhToLLTauTau": masses_spin0,
                 "ggAToZhToLLBB": [250] + masses_spin0,
                 "ggGravitonTohhTo2Tau2B": [270, 300, 500, 700, 1000],
                 "ggRadionTohhTo2Tau2B":   [     300, 500, 700, 1000],
                 "bbH": range(90, 150, 10) + [160, 180, 200, 250, 300, 350, 400],
                 }

def procs(variable="", category=""):
    assert variable
    assert category

    # first character '-' means subtract rather than add
    out = {"TT": ["tt", "tt_semi", "tthad"],
           "*VV": ["ZZ", "WZJetsTo2L2Q", "WW", "WZ3L", "zzTo2L2Nu", "zzTo4L"],
           #"ZTT": ["DYJetsToLL"],
           #"ZTT": ["DY1JetsToLL", "DY2JetsToLL", "DY3JetsToLL", "DY4JetsToLL"],
           "ZTT": ["DY_embed", "-tt_embed"],
           "*singleT": ["t", "tbar"],
           "*ZLL": ["ZLL"],
           "QCD": ["dataOSRelax", "-MCOSRelax"],
           "data_obs": ["dataOSTight"],
           ## fakes below
           "ggH125": ["ggH125"],
           "qqH125": ["qqH125"],
           "VH125": ["VH125"],
           "ZJ": ["ZJ"],
           }

    for m in masses_spin0:
        out["ggHTohhTo2Tau2B%3d" % m] = ["H2hh%3d" % m]

    for p in fakeSignalList():
        out[p] = [p]

    if variable == "BDT":
        del out["*singleT"]
        del out["*ZLL"]
        out["ZLL"] = ["ZLL"]  # fake

    if category == "0M":
        out["W"] = ["W1JetsToLNu", "W2JetsToLNu", "W3JetsToLNu", "W4JetsToLNu"]
    return out


def procs2(variable="", category=""):
    assert variable
    assert category

    # first character '*' means unit normalize and then use factor
    if variable == "BDT":
        return {"VV": ["*VV"]}
    else:
        return {"VV": ["*VV", "*singleT"],
                "ZLL": ["*ZLL"],
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

    out = [
        # {"var": "svMass",      "bins": it_sv_bins_cat2_new, "cuts": {}},
        # {"var": "fMassKinFit", "bins": fm_bins_tt, "cuts": preselection}, #mass_windows},
        # {"var": "CSVJ1Pt", "bins": it_sv_bins_cat1_new, "cuts": preselection}, #mass_windows},
        # {"var": "CSVJ1Pt", "bins": it_sv_bins_cat1_new, "cuts": preselection}, #mass_windows},
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
    for dct in variables():
        if len(set(files(dct["var"]).values())) <= 2:
            print "FIXME: include variations"

    if __fakeSignals:
        print "FIXME: include", sorted(__fakeSignals.keys())

    fakeBkgs = []
    for cat in categories.keys():
        for dct in variables():
            var = dct["var"]
            lst = []
            for k, v in procs(var, cat).iteritems():
                if type(v) != list:
                    sys.exit("ERROR: type of '%s' is not list." % str(v))
                else:
                    lst += v

                if len(v) == 1 and v[0] == k and k not in fakeSignalList():  # FIXME: condition is imperfect
                    fakeBkgs.append(k)

            if len(set(lst)) != len(lst):
                sys.exit("ERROR: procs values has duplicates: %s." % str(sorted(lst)))

    fakeBkgs = list(set(fakeBkgs))
    if fakeBkgs:
        print "FIXME: include", sorted(fakeBkgs)


complain()
