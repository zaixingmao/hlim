#!/usr/bin/env python

import CombineHarvester.CombineTools.ch as ch
import os


def add_processes_and_observations(cb, prefix="zp"):
    print '>> Creating processes and observations...'
    for chn in chns:
        cats_chn = cats["%s_%s" % (chn, era)]
        cb.AddObservations(  ['*'],  [prefix], [era], [chn],                 cats_chn      )
        cb.AddProcesses(     ['*'],  [prefix], [era], [chn], bkg_procs[chn], cats_chn, False  )
        cb.AddProcesses(     masses, [prefix], [era], [chn], sig_procs,      cats_chn, True   )


def add_shapes(cb):
    print '>> Extracting histograms from input root files...'
    for chn in chns:
        file = aux_shapes + input_dirs[chn] + "/htt_" + chn + ".inputs-Zp-%s.root"  % era
        cb.cp().channel([chn]).era([era]).backgrounds().ExtractShapes(
            file, '$BIN/$PROCESS', '$BIN/$PROCESS_$SYSTEMATIC')
        cb.cp().channel([chn]).era([era]).signals().ExtractShapes(
            file, '$BIN/$PROCESS$MASS', '$BIN/$PROCESS$MASS_$SYSTEMATIC')


def add_bbb(cb):
    print '>> Merging bin errors and generating bbb uncertainties...'
    bbb = ch.BinByBinFactory()
    bbb.SetAddThreshold(0.1).SetMergeThreshold(0.5).SetFixNorm(True)

    for chn in chns:
        cb_chn = cb.cp().channel([chn])
        bbb.MergeAndAdd(cb_chn.cp().era([era]).bin_id([0]).process(bkg_procs[chn]), cb)


def rename_and_write(cb):
    print '>> Setting standardised bin names...'
    ch.SetStandardBinNames(cb)

    writer = ch.CardWriter('LIMITS/$TAG/$MASS/$ANALYSIS_$CHANNEL_$BINID_$ERA.txt',
                           'LIMITS/$TAG/common/$ANALYSIS_$CHANNEL.input.root')

    # writer.SetVerbosity(1)
    writer.WriteCards('cmb', cb)
    for chn in chns:
        writer.WriteCards(chn, cb.cp().channel([chn]))
    print '>> Done!'


def print_cb(cb):
    for s in ["Obs", "Procs", "Systs", "Params"]:
        print "* %s *" % s
        getattr(cb, "Print%s" % s)()
        print


def add_systematics(cb):
    print '>> Adding systematic uncertainties...'

    signal = cb.cp().signals().process_set()
    mc_nw = ['ZTT', 'TT', 'VV']
    mc = mc_nw + ['W']
    dd = ['QCD']

    # common
    lumiName = "CMS_lumi_%s" % era
    lumiVal = 1.046
    cb.cp().process(signal + mc).channel(['tt', 'et', 'em']).AddSyst(cb, lumiName, "lnN", ch.SystMap()(lumiVal))
    cb.cp().process(signal + mc_nw).channel(['mt']).AddSyst(cb, lumiName, "lnN", ch.SystMap()(lumiVal))
    cb.cp().process(["TT"]).AddSyst(cb, "CMS_zp_TT_xs_%s" % era, "lnN", ch.SystMap()(1.08))
    cb.cp().process(["VV"]).AddSyst(cb, "CMS_zp_VV_xs_%s" % era, "lnN", ch.SystMap()(1.15))

    # em/et (norm)
    cb.cp().process(["ZTT"]).channel(['em', 'et']).AddSyst(cb, "CMS_zp_ZTT_xs_%s" % era, "lnN", ch.SystMap()(1.10))

    # em/et (shape)
    cb.cp().process(signal + mc + dd).channel(['em', 'et']).AddSyst(cb, "CMS_zp_scale_j_%s" % era, "shape", ch.SystMap()(1.0))
    cb.cp().process(signal + mc + dd).channel(['em', 'et']).AddSyst(cb, "CMS_zp_scale_btag_%s" % era, "shape", ch.SystMap()(1.0))
    cb.cp().process(signal          ).channel(['em', 'et']).AddSyst(cb, "CMS_zp_pdf_%s" % era, "shape", ch.SystMap()(1.0))

    # em (norm)
    cb.cp().process(["QCD"]).channel(['em']).AddSyst(cb, "CMS_zp_em_QCD_LT_%s" % era, "lnN", ch.SystMap()(1.37))
    cb.cp().process(["W"]).channel(['em']).AddSyst(cb, "CMS_zp_em_W_LT_%s" % era, "lnN", ch.SystMap()(1.41))

    # em (shape)
    cb.cp().process(["TT"]).channel(['em']).AddSyst(cb, "CMS_zp_topPt_%s" % era, "shape", ch.SystMap()(1.0))

    # et (norm)
    cb.cp().process(["QCD"]).channel(['et']).AddSyst(cb, "CMS_zp_et_QCD_LT_%s" % era, "lnN", ch.SystMap()(1.164))
    cb.cp().process(["W"]).channel(['et']).AddSyst(cb, "CMS_zp_et_W_LT_%s" % era, "lnN", ch.SystMap()(1.096))

    # et (shape)
    cb.cp().process(mc + dd).channel(['et']).AddSyst(cb, "CMS_zp_scale_W_%s" % era, "shape", ch.SystMap()(1.0))
    cb.cp().process(signal + mc + dd).channel(['et']).AddSyst(cb, "CMS_zp_scale_t_%s" % era, "shape", ch.SystMap()(1.0))
    cb.cp().process(signal + mc + dd).channel(['et']).AddSyst(cb, "CMS_zp_id_t_%s" % era, "shape", ch.SystMap()(1.0))

    # BSM3G codes
    #
    # (0/mt  1/et 2/tt 3/em)
    # (0/Zp  1/W  2/Z  3/TT  4/VV  5/QCD  6/H)
    #
    # e.g. Trig10 is intended to apply to et/Zp
    #
    #
    # NOTES
    # - bbb shapes supersede STMC
    # - bID handled by shape above (losing correlation with mutau)
    # - TES handled by shape above
    # - mt: TES,JES included for backgrounds within bbb

    # et
    cb.cp().process(signal + mc     ).channel(['et']).AddSyst(cb, "Trig10",  "lnN", ch.SystMap()(1.01))

    cb.cp().process(signal + ["ZTT"]).channel(['et']).AddSyst(cb, "ElID10",  "lnN", ch.SystMap()(1.01))
    cb.cp().process(["W"]           ).channel(['et']).AddSyst(cb, "ElID11",  "lnN", ch.SystMap()(1.01))
    cb.cp().process(["TT", "VV"]    ).channel(['et']).AddSyst(cb, "ElID13",  "lnN", ch.SystMap()(1.01))
    cb.cp().process(signal + mc     ).channel(['et']).AddSyst(cb, "EES10",   "lnN", ch.SystMap()(1.01))

    cb.cp().process(signal + ["ZTT"]).channel(['et']).AddSyst(cb, "TaID00",  "lnN", ch.SystMap()(1.06)) # mt
    cb.cp().process(["W"]           ).channel(['et']).AddSyst(cb, "TaID11",  "lnN", ch.SystMap()(1.06))
    cb.cp().process(["TT", "VV"]    ).channel(['et']).AddSyst(cb, "TaID03",  "lnN", ch.SystMap()(1.06)) # mt

    # em
    cb.cp().process(signal + mc     ).channel(['em']).AddSyst(cb, "Trig10",  "lnN", ch.SystMap()(1.01)) # et (SingleEle)

    cb.cp().process(signal + ["ZTT"]).channel(['em']).AddSyst(cb, "ElID10",  "lnN", ch.SystMap()(1.01)) # et
    cb.cp().process(["W"]           ).channel(['em']).AddSyst(cb, "ElID11",  "lnN", ch.SystMap()(1.01)) # et
    cb.cp().process(["TT", "VV"]    ).channel(['em']).AddSyst(cb, "ElID13",  "lnN", ch.SystMap()(1.01)) # et
    cb.cp().process(signal + mc     ).channel(['em']).AddSyst(cb, "EES10",   "lnN", ch.SystMap()(1.01)) # et

    cb.cp().process(signal + mc     ).channel(['em']).AddSyst(cb, "MuID00",  "lnN", ch.SystMap()(1.01)) # mt
    cb.cp().process(signal + mc     ).channel(['em']).AddSyst(cb, "MMS00",   "lnN", ch.SystMap()(1.01)) # mt


    # mt
    cb.cp().process(signal + mc_nw  ).channel(['mt']).AddSyst(cb, "Trig00",  "lnN", ch.SystMap()(1.01))

    cb.cp().process(signal + ["ZTT"]).channel(['mt']).AddSyst(cb, "TaID00",  "lnN", ch.SystMap()(1.06))
    cb.cp().process(["TT", "VV"]    ).channel(['mt']).AddSyst(cb, "TaID03",  "lnN", ch.SystMap()(1.06))

    cb.cp().process(signal + ["ZTT"]).channel(['mt']).AddSyst(cb, "bID00",   "lnN", ch.SystMap()(1.03))
    cb.cp().process(["TT"]          ).channel(['mt']).AddSyst(cb, "bID03",   "lnN", ch.SystMap()(1.12))
    cb.cp().process(["VV"]          ).channel(['mt']).AddSyst(cb, "bID04",   "lnN", ch.SystMap()(1.03))

    cb.cp().process(signal + mc_nw  ).channel(['mt']).AddSyst(cb, "MuID00",  "lnN", ch.SystMap()(1.01))
    cb.cp().process(signal + mc_nw  ).channel(['mt']).AddSyst(cb, "MMS00",   "lnN", ch.SystMap()(1.01))

    cb.cp().process(signal          ).channel(['mt']).AddSyst(cb, "TES00",   "lnN", ch.SystMap()(1.03))
    # cb.cp().process(["ZTT"]         ).channel(['mt']).AddSyst(cb, "TES02",   "lnN", ch.SystMap()(1.07)) # bbb
    # cb.cp().process(["TT", "VV"]    ).channel(['mt']).AddSyst(cb, "TES03",   "lnN", ch.SystMap()(1.09)) # bbb

    cb.cp().process(signal          ).channel(['mt']).AddSyst(cb, "JES00",   "lnN", ch.SystMap()(1.02))

    cb.cp().process(["W"]           ).channel(['mt']).AddSyst(cb, "Close01", "lnN", ch.SystMap()(1.08))
    cb.cp().process(["ZTT"]         ).channel(['mt']).AddSyst(cb, "Close02", "lnN", ch.SystMap()(1.07))
    cb.cp().process(["QCD"]         ).channel(['mt']).AddSyst(cb, "Close05", "lnN", ch.SystMap()(1.68))


    # tt
    cb.cp().process(signal + mc     ).channel(['tt']).AddSyst(cb, "Trig20",  "lnN", ch.SystMap()(1.10))

    cb.cp().process(signal + ["ZTT"]).channel(['tt']).AddSyst(cb, "TaID00",  "lnN", ch.SystMap()(1.12)) # mt
    cb.cp().process(["W"]           ).channel(['tt']).AddSyst(cb, "TaID11",  "lnN", ch.SystMap()(1.30)) # et
    cb.cp().process(["TT", "VV"]    ).channel(['tt']).AddSyst(cb, "TaID03",  "lnN", ch.SystMap()(1.12)) # mt

    cb.cp().process(signal + ["ZTT"]).channel(['tt']).AddSyst(cb, "bID20",   "lnN", ch.SystMap()(1.03))
    cb.cp().process(["W"]           ).channel(['tt']).AddSyst(cb, "bID21",   "lnN", ch.SystMap()(1.10))
    cb.cp().process(["TT"]          ).channel(['tt']).AddSyst(cb, "bID23",   "lnN", ch.SystMap()(1.10))
    cb.cp().process(["VV"]          ).channel(['tt']).AddSyst(cb, "bID24",   "lnN", ch.SystMap()(1.03))

    cb.cp().process(signal          ).channel(['tt']).AddSyst(cb, "TES20",   "lnN", ch.SystMap()(1.03))
    cb.cp().process(["W"]           ).channel(['tt']).AddSyst(cb, "TES21",   "lnN", ch.SystMap()(1.11))
    cb.cp().process(["ZTT"]         ).channel(['tt']).AddSyst(cb, "TES22",   "lnN", ch.SystMap()(1.11))
    cb.cp().process(["TT"]          ).channel(['tt']).AddSyst(cb, "TES23",   "lnN", ch.SystMap()(1.11))
    cb.cp().process(["VV"]          ).channel(['tt']).AddSyst(cb, "TES24",   "lnN", ch.SystMap()(1.08))

    cb.cp().process(signal          ).channel(['tt']).AddSyst(cb, "JES20",   "lnN", ch.SystMap()(1.02))
    cb.cp().process(["W"]           ).channel(['tt']).AddSyst(cb, "JES21",   "lnN", ch.SystMap()(1.12))
    cb.cp().process(["ZTT"]         ).channel(['tt']).AddSyst(cb, "JES22",   "lnN", ch.SystMap()(1.08))
    cb.cp().process(["TT"]          ).channel(['tt']).AddSyst(cb, "JES23",   "lnN", ch.SystMap()(1.12))
    cb.cp().process(["VV"]          ).channel(['tt']).AddSyst(cb, "JES24",   "lnN", ch.SystMap()(1.08))

    cb.cp().process(["W"]           ).channel(['tt']).AddSyst(cb, "Close21", "lnN", ch.SystMap()(1.05))
    cb.cp().process(["ZTT"]         ).channel(['tt']).AddSyst(cb, "Close22", "lnN", ch.SystMap()(1.19))
    cb.cp().process(["QCD"]         ).channel(['tt']).AddSyst(cb, "Close25", "lnN", ch.SystMap()(1.226))
    # cb.cp().process(["QCD"]         ).channel(['tt']).AddSyst(cb, "Close25", "lnN", ch.SystMap()(1.303))  # 76-mockup


def go(cb):
    add_processes_and_observations(cb)
    add_systematics(cb)
    add_shapes(cb)
    add_bbb(cb)
    rename_and_write(cb)
    print_cb(cb)


if __name__ == "__main__":
    cb = ch.CombineHarvester()

    auxiliaries  = os.environ['CMSSW_BASE'] + '/src/auxiliaries/'
    aux_shapes   = auxiliaries +'shapes/'
    era = "13TeV"

    input_dir = ["Zp_1pb", "Zp_nominal"][0]
    input_dirs = {'et' : input_dir,
                  'em' : input_dir,
                  'mt' : input_dir,
                  'tt' : input_dir,
                  }
    chns = sorted(input_dirs.keys())

    bkg_procs = {'et' : ['ZTT', 'W', 'QCD', 'TT', 'VV'],
                 'em' : ['ZTT', 'W', 'QCD', 'TT', 'VV'],
                 'mt' : ['ZTT', 'W', 'QCD', 'TT', 'VV'],
                 'tt' : ['ZTT', 'W', 'QCD', 'TT', 'VV'],
                 }

    sig_procs = ['ggH']

    cats = {
        'et_%s' % era : [
            (0, 'eleTau_inclusive'),
            ],
        'em_%s' % era : [
            (0, 'emu_inclusive'),
            ],
        'mt_%s' % era : [
            (0, 'muTau_inclusive'),
            ],
        'tt_%s' % era : [
            (0, 'tauTau_inclusive'),
            ],
        }

    masses = ch.ValsFromRange('500:3000|500')
    go(cb)
