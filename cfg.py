import os
import sys
from root_dest import root_dest

lumi     = 40.0e-3   # /fb
rescaleX = False

substring_signal_example = "2B350"

masses_spin0 = [260,270,280]#range(260, 360, 10) #+ [500, 700]
masses_spin2 = [500, 700]

categories = {"tt": "tauTau_inclusive",
              "et": "eleTau_inclusive",
              "mt": "muTau_inclusive",
              "em": "emu_inclusive",
              }

#bdtDir = "/nfs_scratch/zmao/samples_Iso/datacard_new/bdt_new/"
bdtDir = "root/bdt/11/"
# WARNING: this variable gets modified by multi-bdt.py
_stem = "13TeV_datacards/combined%s.root"


def files(variable=""):
    assert variable
    s = ""
    return {"":                             _stem % s,
            # "_CMS_scale_t_tautau_8TeVUp":   _stem % "tauUp",
            # "_CMS_scale_t_tautau_8TeVDown": _stem % "tauDown",
            # "_CMS_scale_j_8TeVUp":   _stem % "jetUp",
            # "_CMS_scale_j_8TeVDown": _stem % "jetDown",
            # "_CMS_scale_btag_8TeVUp": _stem % "bSysUp",
            # "_CMS_scale_btag_8TeVDown": _stem % "bSysDown",
            # "_CMS_scale_btagEff_8TeVUp": _stem % "bSysUp",     # duplicate of btag
            # "_CMS_scale_btagEff_8TeVDown": _stem % "bSysDown", # duplicate of btag
            # "_CMS_scale_btagFake_8TeVUp": _stem % "bMisUp",
            # "_CMS_scale_btagFake_8TeVDown": _stem % "bMisDown",
            }


def qcd_sf_name(category):
    # return "L_to_T_SF_%s" % category
    return "SS_to_OS_%s" % category


def procs(variable="", category=""):
    assert variable
    assert category

    # first character '-' means subtract rather than add
    # first character '*' (see procs2)
    out = {"TT": ["TTJets"],
           "VV": ["WZ", "WW", "ZZ"],
           "W": ["WJets"],
           "ZTT": ["DY-50"],
           "singleT": ['ST_antiTop_tW', 'ST_top_tW'],
           "QCD": ["dataSS", "-MCSS"],
           "data_obs": ["dataOS"],
           }

    checkProcs(out)
    return out


def procs2(variable="", category=""):
    """first character '*' means unit normalize and then use factor"""
    assert variable
    assert category
    # out = {"VV": ["*VV", "*singleT"],
    #        "ZLL": ["*ZLL"],
    #        }
    return {}


def isData(proc):
    return proc.startswith("data")

def isDataEmbedded(proc):
    return proc.startswith("DY_embed")  # fixme: dimuon


def isMcEmbedded(proc):
    return proc.endswith("tt_embed")  # first character may be minus sign


def isSignal(proc):
    return any([proc.startswith(p) for p in ["ggHTo", "ggATo", "ggGraviton", "ggRadion", "bbH"]])


def reportExtra(proc):
    # don't report about MC DY and W, which are typically not used
    if proc.startswith("DY") and proc.endswith("JetsToLL"):
        return False
    if proc.startswith("W") and proc.endswith("JetsToLNu"):
        return False
    return True


def cats():
    return " ".join([s[-4] for s in sorted(categories.values())])


def workDir():
    return "/".join(__file__.split("/")[:-1])



def variable():
    fm_bins_old= (4, 250.0, 410.0)
    fm_bins_lt = [200, 250, 270, 290, 310, 330, 350, 370, 390, 410, 430, 450, 500, 550, 600, 650, 700]
    fm_bins_tt = [200, 250, 280, 310, 340, 370, 400, 500, 600, 700]

    preselection = {}
    fMass = {"fMassKinFit": (0.0, None)}
    #chi2 = {"chi2KinFit2": (0.0, 10.0)}
    mass_windows = {"mJJ": (70.0, 150.0), "svMass": (90.0, 150.0)}
    mass_windows.update(fMass)

    ## bins are either a tuple: (n, xMin, xMax)
    ##  or
    ## a list of bin lower edges
    out = {"var": "m_vis", "bins": range(0, 200, 10) + range(200, 325, 25), "cuts": {}}
    return out


def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != 17:
            raise e


def outFileName(sFactor=0, sKey="", var="", cuts={}, tag="", **_):
    stem = root_dest + "/"
    mkdir(stem)

    if sFactor:
        print "FIXME: sFactor"
        stem += "%dx%s" % (sFactor, sKey.replace("H2hh", ""))
    stem += var
    if cutDesc(cuts):
        stem += "_%s" % cutDesc(cuts)

    return "%s%s.root" % (stem, tag)


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


def checkProcs(d):
    fakeBkgs = []
    lst = []
    for k, v in d.iteritems():
        if type(v) != list:
            sys.exit("ERROR: type of '%s' is not list." % str(v))
        else:
            lst += v

        if len(v) == 1 and v[0] == k:  # FIXME: condition is imperfect
            fakeBkgs.append(k)

    if len(set(lst)) != len(lst):
        sys.exit("ERROR: procs values has duplicates: %s." % str(sorted(lst)))

    fakeBkgs = list(set(fakeBkgs))
    if fakeBkgs:
        print "FIXME: include", sorted(fakeBkgs)
