import os
import sys
from root_dest import root_dest

rescaleX = False
lumiUnit = "/pb"
lumi = 35.9e3

masses = [500, 750, 1000, 1250, 1500, 1750, 2000, 2500, 3000, 3500, 4000]

substring_signal_example = "ggH%d" % masses[0]
flipped_suffix = "_WAS_FLIPPED"

_suffix = "inclusive"
categories = {# "tt": "tauTau_%s" % _suffix,
              "mt": "muTau_%s" % _suffix,
              "et": "eleTau_%s" % _suffix,
              "em": "emu_%s" % _suffix,
              }


def bins(ch):
    # dy_mbins = [0, 50, 100, 200, 400, 500, 700, 800, 1000, 1500]
    m6  = [85, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 225, 250, 275, 300, 400, 600, 900]
    m9  = [85, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 225, 250, 275, 300, 400, 600, 900, 1200]
    m10 = [85, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 225, 250, 275, 300, 400, 600, 800, 1000, 1300]
    m12 = [85, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 225, 250, 275, 300, 400, 600, 900, 1200, 1700]
    return {"em": m12,
            "et": m9,
            "mt": m12,
            "tt": m6,
            }.get(ch, m6)


def files(category=""):
    assert category

    if category in ["mt", "et", "em"]:
        stem = "2016_v5/combined_%s_withPUWeight%s.root"

    out = {"":                             stem % (category, ""),
           "_CMS_zp_scale_j_13TeVUp":      stem % (category, "_jetECUp"),
           "_CMS_zp_scale_j_13TeVDown":    stem % (category, "_jetECDown"),
           "_CMS_zp_scale_btag_13TeVUp":   stem % (category, "_bScaleUp"),  # b and light
           "_CMS_zp_scale_btag_13TeVDown": stem % (category, "_bScaleDown"),
           "_CMS_zp_metu_13TeVUp":         stem % (category, "_metUESUp"),
           "_CMS_zp_metu_13TeVDown":       stem % (category, "_metUESDown"),
           # "_CMS_zp_pdf_13TeVUp":         stem % (category, "_pdfUp"),
           # "_CMS_zp_pdf_13TeVDown":       stem % (category, "_pdfDown"),
           }
    if category in ["et", "mt"]:
        out.update({"_CMS_zp_scale_t_13TeVUp": stem % (category, "_tauECUp"),
                    "_CMS_zp_scale_t_13TeVDown": stem % (category, "_tauECDown"),
                    "_CMS_zp_id_t_13TeVUp": stem % (category, "_tauUncUp"),
                    "_CMS_zp_id_t_13TeVDown": stem % (category, "_tauUncDown"),
                    })
    if category == "em":
        out.update({
                # "_CMS_zp_topPt_13TeVUp":   stem % (category, "_topPtUp"),
                # "_CMS_zp_topPt_13TeVDown": stem % (category, ""),  # use nominal for down
                })
    return out


def transfer_factor_name(category, proc, variation, cuts=None):
    prefix = "%s_Loose_to_Tight" % proc

    tdm = cuts.get('~tauDecayMode')
    if tdm and category in ["mt", "et"]:
        assert tdm == (4.5, 9.5), cuts
        return "%s_%s_1prong_3prong" % (prefix, category)
    return "%s_%s" % (prefix, category)


def procs(variable="", category=""):
    assert variable
    assert category

    # first character '-' means subtract rather than add
    # first character '*' (see procs2)
    out = {"TT": ["ST_antiTop_tW", "ST_top_tW", "ST_s-channel", "ST_t-channel_antiTop_tW", "ST_t-channel_top_tW", "TTJets"],
           "VV": ["ZZTo2L2Q", "VVTo2L2Nu", "WZTo1L1Nu2Q", "WZTo1L3Nu", "ZZTo4L", "WWTo1L1Nu2Q", "WZTo2L2Q", "WZTo3LNu"],
           "W": ["WJetsLoose"], #x WJets_Loose_to_Tight_SF from WJets_Loose_to_Tight_* histogram (same as before)
           # "ZTT": ["DY_M-50to150", "DY_M-150"],
           "ZTT": ['DY_M-50to200', 'DY_M-200to400', 'DY_M-400to500', 'DY_M-500to700', 'DY_M-700to800', 'DY_M-800to1000', 'DY_M-1000to1500', 'DY_M-1500to2000', 'DY_M-2000to3000'],
           "QCD": ["QCDLoose"], # x QCD_Loose_to_Tight_SF from QCD_Loose_to_Tight_* histogram (same as before)
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
