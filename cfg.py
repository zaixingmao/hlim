import os
import sys
from root_dest import root_dest

#lumi     = 1.264e3
lumiUnit = "/pb"

rescaleX = False

# masses = [160]
# masses = [260,270,280]#range(260, 360, 10) #+ [500, 700]
masses = [500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000]
# masses = masses[:2]

substring_signal_example = "ggH%d" % masses[0]
flipped_suffix = "_WAS_FLIPPED"

_suffix = "inclusive"
categories = {# "tt": "tauTau_%s" % _suffix,
              "et": "eleTau_%s" % _suffix,
              # "mt": "muTau_%s" % _suffix,
              "em": "emu_%s" % _suffix,
              }

#bdtDir = "/nfs_scratch/zmao/samples_Iso/datacard_new/bdt_new/"
bdtDir = "root/bdt/11/"
# lumi = 2093.3  # cards before Feb. 29
lumi = 2153.0  # Feb. 29 cards
# lumi = 2246.26 # 76X

def files(category=""):
    if category == "et":
        # stem = "13TeV_zp_feb2/combined_%s_withPUWeight%s.root"  # 1,3 prong
        # stem = "13TeV_zp_feb26/combined_%s_withPUWeight%s.root"  # 1,2,3 prong
        # stem = "13TeV_zp_feb29/combined_%s_withPUWeight%s.root"  # 2.2/fb
        # stem = "13TeV_zp_mar3_dy_mbins/DY_NLO_inclusive_%s%s.root"  # DY-only
        # stem = "13TeV_zp_mar3_dy_mbins/DY_NLO_stitched_%s%s_2.root"  # DY-only
        # stem = "13TeV_zp_mar3_dy_mbins/combined_%s_withPUWeight%s.root"  # m-binned nlo dy
        # stem = "13TeV_zp_mar11/combined_%s_withPUWeight%s.root"  # updated tes
        # stem = "13TeV_zp_mar19/combined_%s_withPUWeight%s.root"  # including pdf unc.
        # stem = "13TeV_zp_74X_apr22/combined_%s_withPUWeight%s.root"  # more precise W factor
        # stem = "/user_data/zmao/datacard_Apr28/combined_%s_withPUWeight%s.root"  # data-driven W
        stem = "13TeV_zp_74X_may5/combined_%s_withPUWeight%s.root"  # apr22 et + data-driven W
        # stem = "/user_data/zmao/datacard_7_6_X_2/combined_%s_withPUWeight%s.root"
    if category == "em":
        # stem = "13TeV_zp_feb5/combined_%s_withPUWeight%s.root"
        # stem = "13TeV_zp_feb29/combined_%s_withPUWeight%s.root"  # 2.2/fb
        # stem = "13TeV_zp_mar3_dy_mbins/combined_%s_withPUWeight%s.root"  # m-binned nlo dy
        # stem = "13TeV_zp_mar19/combined_%s_withPUWeight%s.root"  # including pdf unc.
        # stem = "13TeV_zp_74X_apr22/combined_%s_withPUWeight%s.root"  # more precise W factor
        stem = "13TeV_zp_74X_may4/combined_%s_withPUWeight%s.root"  # topPt
        # stem = "/user_data/zmao/datacard_7_6_X_2/combined_%s_withPUWeight%s.root"
    assert category
    out = {"":                             stem % (category, ""),
           "_CMS_zp_scale_j_13TeVUp":      stem % (category, "_jetECUp"),
           "_CMS_zp_scale_j_13TeVDown":    stem % (category, "_jetECDown"),
           "_CMS_zp_scale_btag_13TeVUp":   stem % (category, "_bScaleUp"),  # b and light
           "_CMS_zp_scale_btag_13TeVDown": stem % (category, "_bScaleDown"),
           "_CMS_zp_pdf_13TeVUp":         stem % (category, "_pdfUp"),
           "_CMS_zp_pdf_13TeVDown":       stem % (category, "_pdfDown"),
           }
    if category == "et":
        out.update({
                # "_CMS_zp_scale_W_13TeVUp":   stem % (category, "_1.25"),
                # "_CMS_zp_scale_W_13TeVDown": stem % (category, "_1.05"),
                "_CMS_zp_scale_t_13TeVUp": stem % (category, "_tauECUp"),
                "_CMS_zp_scale_t_13TeVDown": stem % (category, "_tauECDown"),
                "_CMS_zp_id_t_13TeVUp": stem % (category, "_tauUncUp"),
                "_CMS_zp_id_t_13TeVDown": stem % (category, "_tauUncDown"),
                })
    if category == "em":
        out.update({
                "_CMS_zp_topPt_13TeVUp":   stem % (category, "_topPtUp"),
                "_CMS_zp_topPt_13TeVDown": stem % (category, ""),  # use nominal for down
                })
    return out


def transfer_factor_name(category, proc, variation, cuts=None):
    # return "L_to_T_SF_%s" % category
    # return "SS_to_OS_%s" % category
    # # Feb. 0
    # if proc == "QCD":
    #     return "Loose_to_Tight_et_1prong_3prong"
    # if proc == "WJets":
    #     return "WJets_Loose_to_Tight"

    prefix = "%s_Loose_to_Tight" % proc

    tdm = cuts.get('~tauDecayMode')
    if category == "et" and tdm:
        assert tdm == (4.5, 9.5), cuts
        return "%s_et_1prong_3prong" % prefix
    return "%s_%s" % (prefix, category)


def procs(variable="", category=""):
    assert variable
    assert category

    # first character '-' means subtract rather than add
    # first character '*' (see procs2)
    out = {"TT": ["TTJets", 'ST_antiTop_tW', 'ST_top_tW', 'ST_t-channel_antiTop_tW', 'ST_t-channel_top_tW'],
           "VV": ['VVTo2L2Nu', 'WWTo1L1Nu2Q', 'WZJets', 'WZTo1L1Nu2Q', 'WZTo1L3Nu', 'WZTo2L2Q', 'ZZTo2L2Q', 'ZZTo4L'],
           # "ZTT": ['DY_M-50-H-0to100', 'DY_M-50-H-100to200', 'DY_M-50-H-200to400', 'DY_M-50-H-400to600', 'DY_M-50-H-600toInf'] +\
           #     [], #['DY_M-5to50-H-0to100', 'DY_M-5to50-H-200to400', 'DY_M-5to50-H-400to600', 'DY_M-5to50-H-600toInf'],

           # "ZTT": ['DY_M-50'],

           # "ZTT": ['DY_M-50to100', 'DY_M-100to200', 'DY_M-200to400', 'DY_M-400to500', 'DY_M-500to700', 'DY_M-700to800', 'DY_M-800to1000', 'DY_M-1000to1500'],
           "ZTT": ['DY_M-50to200', 'DY_M-200to400', 'DY_M-400to500', 'DY_M-500to700', 'DY_M-700to800', 'DY_M-800to1000', 'DY_M-1000to1500'],

           # "W": ['WJets_HT-0to100', 'WJets_HT-100to200', 'WJets_HT-200to400', 'WJets_HT-400to600', 'WJets_HT-600toInf'],
           # "VV": ["WZ", "WW", "ZZ"],
           # "W": ["WJets"],
           # "ZTT": ["ZTT"],
           # "ZLL": ["ZL", "ZJ"],
           # "ZL": ["ZL"],
           # "ZJ": ["ZJ"],

           # "QCD": ["dataSS", "-MCSS"],
           # "data_obs": ["dataOS"],

           "W": ["WJetsLoose"],
           "QCD": ["dataLoose", "-MCLoose"],

           "data_obs": ["dataTight"],
           }
    for m in masses:
        out["ggH%d" % m] = ["Zprime_%d" % m]

    # exclusive DYs
    # out['DY_M-50'] = ['DY_M-50']
    # hs = ['0', '100', '200', '400', '600', 'Inf']
    # for i, h in enumerate(hs):
    #     if i == len(hs) - 1:
    #         continue
    #     key = "DY_M-50-H-%sto%s" % (h, hs[1 + i])
    #     out[key] = [key]

    # ms = [50, 200, 400, 500, 700, 800, 1000, 1500]
    # for i, m in enumerate(ms):
    #     if i == len(ms) - 1:
    #         continue
    #     key = "DY_M-%dto%d" % (m, ms[1 + i])
    #     out[key] = [key]

    checkProcs(out)
    return out


def procs2(variable="", category=""):
    """first character '*' means unit normalize and then use factor"""
    assert variable
    assert category
    out = {}

    # out = {"VV": ["*VV", "*singleT"],
    #        "ZLL": ["*ZLL"],
    #        }

    # out["W+QCD"] = ["W", "QCD"]

    return out


def isData(proc):
    return proc.startswith("data")


def isDataEmbedded(proc):
    return proc.startswith("DY_embed")  # fixme: dimuon


def isMcEmbedded(proc):
    return proc.endswith("tt_embed")  # first character may be minus sign


def isSignal(proc):
    return any([proc.startswith(p) for p in ["ggH", "ggA", "ggGraviton", "ggRadion", "bbH"]])


def isVariation(proc):
    return proc.endswith("Down") or proc.endswith("Up")


def isFlippedTracker(proc):
    return proc.endswith(flipped_suffix)


def reportExtra(proc):
    # don't report about MC DY and W, which are typically not used
    if proc.startswith("DY") and proc.endswith("JetsToLL"):
        return False
    if proc.startswith("W") and proc.endswith("JetsToLNu"):
        return False
    return True


def cats():
    print "FIXME: cfg.cats()"
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
    # out = {"var": "m_vis", "bins": range(0, 200, 10) + range(200, 325, 25), "cuts": {}}
    out = {"var": "m_vis", "bins": range(0, 300, 50) + [300, 400, 600, 800, 1200], "cuts": {}}
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
