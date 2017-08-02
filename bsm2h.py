#!/usr/bin/env python

import array, os, sys
import ROOT as r
import cfg, xs
import make_root_files, multi_bdt


def merge(stems=None, inDir=None, subDirs=None, outDir=None, suffix=None, tag="", dest="", bins=None):
    assert dest
    outFile = r.TFile("%s/src/auxiliaries/shapes/%s/htt_%s.inputs-Zp-13TeV.root" % (os.environ["CMSSW_BASE"], dest, tag), "RECREATE")
    outFile.mkdir(outDir)

    for (key, hName) in subDirs.iteritems():
        oneKey(key, inDir, stems, suffix, hName, bins, outFile, outDir)

    outFile.Close()

    variations = set()
    variables = set()
    for key, value in subDirs.iteritems():
        variations.add(key.replace("Up", "").replace("Down", ""))
        variables.add(value[1 + value.find("/"):])
    assert len(variables) == 1, variables
    var = variables.pop()
    ch = tag
    masses = []
    for stem in stems:
        if stem.startswith("Zprime"):
            masses.append(stem.replace("Zprime", ""))
    args = "--file1=Zp_1pb/htt_%s.inputs-Zp-13TeV.root --file2='' --masses='%s' --xtitle='%s (GeV)'" % (ch, " ".join(masses), var)
    args += " --bands=%s" % ",".join([v.replace("_CMS", "CMS") for v in variations])
    multi_bdt.compare(args, variations, var, ch)


def oneKey(key, inDir, stems, suffix, hName, bins, outFile, outDir):
    name_map = [("QCD_all", "QCD"),
                ("QCDdatadriven", "QCD"),
                # ("QCD_76XMVAID", "QCD"),
                # ("QCD_76XMVAID2", "QCD"),
                ("Zprime", "ggH"),
                ("ZPrime_", "ggH"),
                ("ZprimeToTauTau_M_", "ggH"),
                ("Data", "data_obs"),
                ("Diboson", "VV"),
                ("TTBar", "TT"),
                ("WJets", "W"),
                ("ZJets", "ZTT"),

                ("tbar{t}", "TT"),
                ("W+Jets", "W"),
                ("DY+Jets", "ZTT"),

                ("eleTau_Z", "eleTau_ZTT"),
                ("emu_Z", "emu_ZTT"),
                ("eleTau_", ""),
                ("emu_", ""),
                ]

    sumb = None
    sumb_keys = []
    procs = []
    for stem in stems:
        inFileName = inDir + stem + suffix
        inFile = r.TFile(inFileName)
        if inFile.IsZombie():
            sys.exit("")

        h1 = inFile.Get(hName)
        if not h1:
            sys.exit("%s:%s not found" % (inFileName, hName))

        proc = stem
        for old, new in name_map:
            proc = proc.replace(old, new)
        procs.append(proc)

        h = h1.Clone(proc + key)
        h.SetDirectory(0)
        inFile.Close()

        if bins:
            h = h.Rebin(len(bins) - 1, "", array.array('d', bins))
            make_root_files.shift(h)

        scale_signal_to_pb = False
        if scale_signal_to_pb and proc.startswith("ggH"):
            print "FIXME: resolve 2015 vs. 2016"
            mass = int(proc.replace("ggH", ""))
            if xs_pb(mass):
                h.Scale(1.0 / xs_pb(mass))  # some xs_pb --> 1 pb
            else:
                print proc, mass, "xs not found"

        outFile.cd(outDir)
        h.Write()

        if proc.startswith("data") or proc.startswith("ggH"):
            print "excluding %s from sum_b" % proc
            continue
        elif sumb:
            sumb_keys.append(h.GetName())
            sumb.Add(h)
        else:
            sumb = h.Clone("sum_b")
            sumb_keys.append(h.GetName())

    if sumb:
        sumb.Write()
        l = " " * 4
        suffix = key
        if suffix:
            make_root_files.describe(sumb, l, sorted([x.replace(suffix, "") for x in sumb_keys]), onlyLast=True)
        else:
            make_root_files.describe(sumb, l, sumb_keys)

        if "data_obs" not in procs:
            print "WARNING! Using sum_b for data_obs"
            sumb.Write("data_obs")


def mu():
    stems = ["ZprimeToTauTau_M_%d" % i for i in [500, 1000, 1500, 2000, 2500, 3000]]
    stems += ["Data", "Diboson", "QCDdatadriven", "TTBar", "WJets", "ZJets"]
    # d = "Fitter/"
    d = "Fitter/muTau_1or3prong/"
    hName = "DiJetMass"
    merge(stems=stems, hName=hName, inDir=d, outDir="muTau_inclusive", suffix="_muTauSR_ForFitter.root", tag="mt", dest="Zp_nominal")
    merge(stems=stems, hName=hName, inDir=d, outDir="muTau_inclusive", suffix="_muTauSR_ForFitter.root", tag="mt", dest="Zp_1pb", scale_signal_to_pb=True)


def had():
    stems = ["Zprime%d" % i for i in [1750, 2000, 2500, 3000, 3500]]
    # stems = []
    stems += ["VV", "QCD", # "Data",
              "tbar{t}", "W+Jets", "DY+Jets"]
    # d = "Fitter/SR2/"
    # d = "Fitter/SR2_097/"
    # d = "Fitter/RESULTS_1or3prong_bJet_DY_HT_Binned/"
    # d = "Fitter/CR_C_June/"

    # d = "Fitter/SR_DY_madgraphMLM-pythia8/"  # likely wrong DY cross section
    # d = "Fitter/SR095_DY_amcatnloFXFX-pythia8/"
    # d = "Fitter/CR_C_Klass/"
    # d = "Fitter/SR097_DY_amcatnloFXFX-pythia8/"

    d = "Fitter/SR097_DY_amcatnloFXFX-fixedUnc/"
    variations = {"": "NDiTauCombinations/DiTauReconstructableMass",
                  "_CMS_zp_id_t_13TeVUp": "Tau_weight_Up/DiTauReconstructableMass",
                  "_CMS_zp_id_t_13TeVDown": "Tau_weight_Down/DiTauReconstructableMass",
                  }

    merge(stems=stems, inDir=d, subDirs=variations, outDir="tauTau_inclusive", suffix=".root", tag="tt", dest="Zp_1pb", bins=cfg.bins("tt"))


def to_h(prefix=""):
    stems = ["%s_ZPrime_%d" % (prefix, i) for i in [500, 1000, 1500, 2000, 2500, 3000]]
    stems += ["%s_VV" % prefix, "%s_QCD" % prefix, "%s_TT" % prefix, "%s_W" % prefix, "%s_Z" % prefix, "%s_data_obs" % prefix]
    d = "Fitter/%s/" % prefix
    hName = "m_effective"
    merge(stems=stems, hName=hName, inDir=d, outDir="%s_inclusive" % prefix, suffix=".root", tag={"eleTau": "et", "emu": "em"}[prefix], dest=".", scale_signal_to_pb=True)


if __name__ == "__main__":
    # m1("eleTau")
    # m1("emu")
    # m2()
    # mu()
    had()
    # to_h("eleTau")
    # to_h("emu")
