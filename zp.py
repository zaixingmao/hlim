#!/usr/bin/env python

import CombineHarvester.CombineTools.ch as ch
import os


def add_processes_and_observations(cb):
    print '>> Creating processes and observations...'
    for chn in chns:
        cats_chn = cats["%s_%s" % (chn, era)]
        cb.AddObservations(  ['*'],  ['htt'], [era], [chn],                 cats_chn      )
        cb.AddProcesses(     ['*'],  ['htt'], [era], [chn], bkg_procs[chn], cats_chn, False  )
        cb.AddProcesses(     masses, ['htt'], [era], [chn], sig_procs,      cats_chn, True   )


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
    mc = ['ZTT','TT','VV', 'W']
    dd = ['QCD']

    # common (norm)
    cb.cp().process(signal + mc).AddSyst(cb, "CMS_lumi_%s" % era, "lnN", ch.SystMap()(1.04))
    cb.cp().process(["TT"]).AddSyst(cb, "CMS_TT_xs_%s" % era, "lnN", ch.SystMap()(1.08))
    cb.cp().process(["ZTT"]).AddSyst(cb, "CMS_ZTT_xs_%s" % era, "lnN", ch.SystMap()(1.12))
    cb.cp().process(["VV"]).AddSyst(cb, "CMS_VV_xs_%s" % era, "lnN", ch.SystMap()(1.15))

    # common (shape)
    cb.cp().process(signal + mc + dd).AddSyst(cb, "CMS_scale_j_%s" % era, "shape", ch.SystMap()(1.0))
    cb.cp().process(signal + mc + dd).AddSyst(cb, "CMS_scale_btag_%s" % era, "shape", ch.SystMap()(1.0))

    # em (norm)
    cb.cp().process(["QCD"]).channel(['em']).AddSyst(cb, "CMS_em_QCD_LT_%s" % era, "lnN", ch.SystMap()(1.37))
    cb.cp().process(["W"]).channel(['em']).AddSyst(cb, "CMS_em_W_LT_%s" % era, "lnN", ch.SystMap()(1.41))

    # et (norm)
    cb.cp().process(["QCD"]).channel(['et']).AddSyst(cb, "CMS_et_QCD_LT_%s" % era, "lnN", ch.SystMap()(1.164))
    cb.cp().process(["W"]).channel(['et']).AddSyst(cb, "CMS_et_W_LT_%s" % era, "lnN", ch.SystMap()(1.096))

    # et (shape)
    cb.cp().process(mc + dd).channel(['et']).AddSyst(cb, "CMS_scale_W_13TeV", "shape", ch.SystMap()(1.0))
    cb.cp().process(signal + mc + dd).channel(['et']).AddSyst(cb, "CMS_scale_t_13TeV", "shape", ch.SystMap()(1.0))


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

    input_dirs = {'et' : 'Brown',
                  'em' : 'Brown',
                  # 'mt' : 'BSM3G',
                  # 'tt' : 'BSM3G',
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
            (0, 'eleTau_inclusive'),
            ],
        'tt_%s' % era : [
            (0, 'eleTau_inclusive'),
            ],
        }

    masses = ch.ValsFromRange('500:3000|500')
    go(cb)
