#!/usr/bin/env python

import CombineHarvester.CombineTools.ch as ch
import os
import cfg


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


def n0(cb, procs, channels, name, val):
    cb.cp().process(procs).channel(channels).AddSyst(cb, name, "lnN", ch.SystMap()(val))


def n(cb, procs, stem, val, channels=None):
    name = "CMS_%s_%s" % (stem, era)
    if channels is not None:
        cb.cp().process(procs).channel(channels).AddSyst(cb, name, "lnN", ch.SystMap()(val))
    else:
        cb.cp().process(procs).AddSyst(cb, name, "lnN", ch.SystMap()(val))


def s(cb, procs, stem, channels, val=1.0):
    name = "CMS_%s_%s" % (stem, era)
    cb.cp().process(procs).channel(channels).AddSyst(cb, name, "shape", ch.SystMap()(val))


def add_systematics(cb):
    print '>> Adding systematic uncertainties...'

    signal = cb.cp().signals().process_set()
    mc_nw = ['ZTT', 'TT', 'VV']
    mc = mc_nw + ['W']
    dd = ['QCD']

    # common
    lumiVal = 1.027

    n(cb, signal + mc,    "lumi", lumiVal, ['tt', 'em'])
    n(cb, signal + mc_nw, "lumi", lumiVal, ['mt', 'et'])

    n(cb, ["TT"],  "zp_TT_xs",     1.08)
    n(cb, ["VV"],  "zp_VV_xs",     1.15)
    n(cb, ["ZTT"], "zp_ZTT_xs",    1.10, ['em', 'et', 'mt'])
    n(cb, ["QCD"], "zp_em_QCD_LT", 1.23, ['em'])
    n(cb, ["W"],   "zp_em_W_LT",   1.41, ['em'])
    n(cb, ["QCD"], "zp_et_QCD_LT", 1.08, ['et'])
    n(cb, ["W"]  , "zp_et_W_LT",   1.15, ['et'])
    n(cb, ["QCD"], "zp_mt_QCD_LT", 1.11, ['mt'])
    n(cb, ["W"]  , "zp_mt_W_LT",   1.08, ['mt'])

    s(cb, signal + mc + dd, "zp_scale_j",    ['em'])
    s(cb, signal + mc_nw,   "zp_scale_j",    ['mt', 'et'])        # no ddW variations
    s(cb, signal + mc + dd, "zp_scale_btag", ['em'])
    s(cb, signal + mc_nw,   "zp_scale_btag", ['mt', 'et'])        # no ddW variations
    s(cb, signal + mc_nw,   "zp_id_t",       ['tt', 'mt', 'et'])  # no ddW variations
    s(cb, signal + mc_nw,   "zp_scale_t",    ['mt', 'et'])        # no ddW variations

    # cb.cp().process(signal).channel(['em', 'et', 'mt']).AddSyst(cb, "CMS_zp_pdf_%s" % era, "shape", ch.SystMap()(0.3))  # the template represent 3.x sigma variations
    # cb.cp().process(["TT"]).channel(['em']).AddSyst(cb, "CMS_zp_topPt_%s" % era, "shape", ch.SystMap()(1.0))
    # cb.cp().process(mc + dd).channel(['mt', 'et']).AddSyst(cb, "CMS_zp_scale_W_%s" % era, "shape", ch.SystMap()(1.0))          # only for MC-W
    # cb.cp().process(signal + mc + dd).channel(['mt', 'et']).AddSyst(cb, "CMS_zp_scale_t_%s" % era, "shape", ch.SystMap()(1.0))

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
    # - bID, TID, TES,  handled by shape above

    # et
    n0(cb, signal + mc_nw,   ['et'], "Trig10", 1.01)
    n0(cb, signal + ["ZTT"], ['et'], "ElID10", 1.06)
    n0(cb, ["TT", "VV"],     ['et'], "ElID13", 1.06)
    n0(cb, signal + mc_nw,   ['et'], "EES10",  1.01)
    # cb.cp().process(["W"]).channel(['et']).AddSyst(cb, "ElID11",  "lnN", ch.SystMap()(1.01))

    n0(cb, signal + mc,      ['em'], "Trig10", 1.01) # et (SingleEle)
    n0(cb, signal + ["ZTT"], ['em'], "ElID10", 1.06) # et
    n0(cb, ["W"]           , ['em'], "ElID11", 1.06) # et
    n0(cb, ["TT", "VV"]    , ['em'], "ElID13", 1.06) # et
    n0(cb, signal + mc,      ['em'], "EES10",  1.01) # et
    n0(cb, signal + mc,      ['em'], "MuID00", 1.07) # mt
    n0(cb, signal + mc,      ['em'], "MMS00",  1.01) # mt

    # mt
    n0(cb, signal + mc_nw, ['mt'], "Trig00",  1.01)
    n0(cb, signal + mc_nw, ['mt'], "MuID00",  1.07)
    n0(cb, signal + mc_nw, ['mt'], "MMS00",   1.01)
    # n0(cb, ["W"]         , ['mt'], "Close01", 1.08)
    # n0(cb, ["ZTT"]       , ['mt'], "Close02", 1.07)
    # n0(cb, ["QCD"]       , ['mt'], "Close05", 1.68)

    # tt
    n0(cb, signal + mc     , ['tt'], "Trig20",  1.10)

    n0(cb, signal + ["ZTT"], ['tt'], "bID20",   1.03)
    n0(cb, ["W"]           , ['tt'], "bID21",   1.10)
    n0(cb, ["TT"]          , ['tt'], "bID23",   1.10)
    n0(cb, ["VV"]          , ['tt'], "bID24",   1.03)

    n0(cb, signal          , ['tt'], "TES20",   1.03)
    n0(cb, ["W"]           , ['tt'], "TES21",   1.11)
    n0(cb, ["ZTT"]         , ['tt'], "TES22",   1.11)
    n0(cb, ["TT"]          , ['tt'], "TES23",   1.11)
    n0(cb, ["VV"]          , ['tt'], "TES24",   1.08)

    n0(cb, signal          , ['tt'], "JES20",   1.02)
    n0(cb, ["W"]           , ['tt'], "JES21",   1.12)
    n0(cb, ["ZTT"]         , ['tt'], "JES22",   1.08)
    n0(cb, ["TT"]          , ['tt'], "JES23",   1.12)
    n0(cb, ["VV"]          , ['tt'], "JES24",   1.08)

    n0(cb, ["W"]           , ['tt'], "Close21", 1.05)
    n0(cb, ["ZTT"]         , ['tt'], "Close22", 1.19)
    n0(cb, ["QCD"]         , ['tt'], "Close25", 1.226)


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

    input_dirs = {'et' : "Brown",
                  'em' : "Brown",
                  'mt' : "Brown",
                  'tt' : "Zp_1pb",
                  }

    chns = sorted(input_dirs.keys())

    bkg_procs = {'et' : ['ZTT', 'W', 'QCD', 'TT', 'VV'],
                 'em' : ['ZTT', 'W', 'QCD', 'TT', 'VV'],
                 'mt' : ['ZTT', 'W', 'QCD', 'TT', 'VV'],
                 'tt' : ['ZTT', 'W', 'QCD', 'TT', 'VV'],
                 }

    sig_procs = ['ggH']

    cats = {'et_%s' % era : [(0, 'eleTau_inclusive'), ],
            'em_%s' % era : [(0, 'emu_inclusive'),    ],
            'mt_%s' % era : [(0, 'muTau_inclusive'),  ],
            'tt_%s' % era : [(0, 'tauTau_inclusive'), ],
            }

    masses = ch.ValsFromRange(",".join(["%d" % m for m in cfg.masses]))
    go(cb)
