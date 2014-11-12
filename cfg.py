import os
import sys

if "CMSSW_BASE" not in os.environ:
    sys.exit("Set up the CMSSW environment.")

root_dest = "%s/src/auxiliaries/shapes/Brown" % os.environ["CMSSW_BASE"]

#masses_spin0 = [260, 300, 350][:1]
masses_spin0 = range(260, 360, 10) #+ [500, 700]
masses_spin2 = [500, 700]

categories = {"MM_LM": "tauTau_2jet2tag",
              #"2M": "tauTau_2jet2tag",
              #"1M": "tauTau_2jet1tag",
              }

multi_vars = ["",
              #"fMassKinFit_0.0.chi2KinFit2.10.0",
              #"fMassKinFit_70.0.mJJ.150.0_90.0.svMass.150.0",
              "fMassKinFit_0.0.fMassKinFit_70.0.mJJ.150.0_90.0.svMass.150.0",
              "BDT_260",
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
