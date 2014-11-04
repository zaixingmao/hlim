#!/usr/bin/env python

import os
import sys


def opts():
    import optparse
    parser = optparse.OptionParser()

    parser.add_option("--masses",
                      dest="masses",
                      default="260 300 350",
                      help="list of masses",
                      )

    parser.add_option("--categories",
                      dest="categories",
                      default="1 2",
                      help="list of categories",
                      )

    parser.add_option("--cards",
                      dest="cards",
                      default=False,
                      action="store_true",
                      help="remove and recreate data cards")

    parser.add_option("--fits",
                      dest="fits",
                      default=False,
                      action="store_true",
                      help="do fits/limits")

    parser.add_option("--plots",
                      dest="plots",
                      default=False,
                      action="store_true",
                      help="make plots")

    parser.add_option("--postfit",
                      dest="postfit",
                      default=False,
                      action="store_true",
                      help="make post-fit plots")

    parser.add_option("--alsoObs",
                      dest="alsoObs",
                      default=False,
                      action="store_true",
                      help="plot observed limit")

    parser.add_option("--full",
                      dest="full",
                      default=False,
                      action="store_true",
                      help="--cards --fits --plots --postfit")

    parser.add_option("--file",
                      dest="file",
                      default="",
                      metavar="x.root",
                      help=" required!!")

    options, args = parser.parse_args()
    if not options.file:
        print "--file is required."
        sys.exit(1)

    file2 = os.path.expanduser(options.file)
    if not os.path.exists(file2):
        print "--file is required to exist (%s does not)." % file2
        sys.exit(1)

    if options.full:
        for item in ["cards", "fits", "plots", "postfit"]:
            setattr(options, item, True)

    return options 


if __name__ == "__main__":
    # rl.txt
    # https://twiki.cern.ch/twiki/bin/viewauth/CMS/SWGuideHiggs2TauLimits
    options = opts()
    common = "--channels=tt --Hhh-categories-tt='%s' --periods=8TeV %s" % (options.categories, options.masses)

    masses = options.masses.split()

    base = "%s/src/HiggsAnalysis/HiggsToTauTau" % os.environ["CMSSW_BASE"]
    dc = "%s/dc" % base
    lim = "%s/LIMITS/" % base
    inDir = "%s/setup-Hhh" % base

    #remove and create link
    link = "%s/tt/htt_tt.inputs-Hhh-8TeV.root" % inDir
    try:
        os.remove(link)
    except OSError as e:
        if e.errno != 2:
            print e
            sys.exit(1)
    os.system("ln -s %s %s" % (options.file, link))

    if options.cards:
        os.system("rm -rf %s" % dc)
        os.system(" ".join(["setup-datacards.py",
                            "--in=%s" % inDir,
                            "--out="+dc,
                            "--analysis=Hhh",
                            common,
                            ]))

        os.system("rm -rf %s" % lim)
        os.system("mkdir -p %s" % lim)
        os.system(" ".join(["setup-Hhh.py",
                            "--in=%s" % dc,
                            "--out=%s" % lim,
                            common,
                            ]))

    if options.fits:
        for mass in masses:
            lim1 = "%s/tt/%s" % (lim, mass)
            os.system("limit.py --max-likelihood --stable --rMin -5 --rMax 5 %s" % lim1)
            os.system("cat %s/out/mlfit.txt" % lim1)
            #os.system("limit.py --significance-frequentist %s" % lim1)
            #os.system("limit.py --pvalue-frequentist %s" % lim1)
            os.system("limit.py --asymptotic %s" % lim1)

    if options.plots:
        layouts = "%s/python/layouts" % base
        plotcommon = "%s/tt/ masspoints='%s'" % (lim, " ".join(masses))
        os.system(" ".join(["plot",
                            "--max-likelihood",
                            "%s/max-likelihood_sm.py" % layouts,
                            plotcommon,
                            ]))

        os.system(" ".join(["plot",
                            "--asymptotic",
                            "%s/limit-mssm-ggHTohh.py" % layouts,
                            plotcommon,
                            "" if options.alsoObs else "expectedOnly=True",
                            ]))

        #os.system(" ".join(["plot",
        #                    "--significance-frequentist",
        #                    "%s/significance-sm.py" % layouts,
        #                    plotcommon,
        #                    ]))
        #
        #os.system(" ".join(["plot",
        #                    "--pvalue-frequentist",
        #                    "%s/pvalue-sm.py" % layouts,
        #                    plotcommon,
        #                    ]))

    if options.postfit:
        for mass in masses:
            lim1 = "%s/tt/%s" % (lim, mass)
            test = "%s/test" % base
            os.system("cd %s && python mlfit_and_copy.py --skip %s" % (test, lim1))
            #python mlfit_and_copy.py -a mssm --skip --mA [160,350,500] --tanb [8,20,40] $CMSSW_BASE/src/LIMITS-yymmdd-mssm/bbb-mlfit/cmb/[160,350,500]

            config = "%s/setup-Hhh/tt/limits.config-sm-tt-only" % base
            os.system("cd %s && python produce_macros.py --config %s" % (test, config))
            #python produce_macros.py --config $CMSSW_BASE/src/HiggsAnalysis/HiggsToTauTau/data/limits.config-sm-yymmdd[-unblinded]
            #python produce_macros.py -a mssm --mA [160,350,500] --tanb [8,20,40] --hww-signal --config $CMSSW_BASE/src/HiggsAnalysis/HiggsToTauTau/data/limits.config-mssm-yymmdd

            os.system("cd %s && python run_macros.py --config %s" % (test, config))

            #os.system("cd %s && python summary_plots.py --config %s" % (test, config))
            #python summary_plots.py --config $CMSSW_BASE/src/HiggsAnalysis/HiggsToTauTau/data/limits.config-sm-yymmdd[-unblinded]
            #python summary_plots.py -a mssm --mA [160,350,500] --tanb [8,20,40] --hww-signal
