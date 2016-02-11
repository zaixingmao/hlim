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

    # em/et (norm)
    # cb.cp().process(signal + mc).AddSyst(cb, "CMS_lumi_%s" % era, "lnN", ch.SystMap()(1.04))  # included in BSM3G
    cb.cp().process(["TT"]).channel(['em', 'et']).AddSyst(cb, "CMS_TT_xs_%s" % era, "lnN", ch.SystMap()(1.08))
    cb.cp().process(["ZTT"]).channel(['em', 'et']).AddSyst(cb, "CMS_ZTT_xs_%s" % era, "lnN", ch.SystMap()(1.12))
    cb.cp().process(["VV"]).channel(['em', 'et']).AddSyst(cb, "CMS_VV_xs_%s" % era, "lnN", ch.SystMap()(1.15))

    # em/et (shape)
    cb.cp().process(signal + mc + dd).channel(['em', 'et']).AddSyst(cb, "CMS_scale_j_%s" % era, "shape", ch.SystMap()(1.0))
    cb.cp().process(signal + mc + dd).channel(['em', 'et']).AddSyst(cb, "CMS_scale_btag_%s" % era, "shape", ch.SystMap()(1.0))

    # em (norm)
    cb.cp().process(["QCD"]).channel(['em']).AddSyst(cb, "CMS_em_QCD_LT_%s" % era, "lnN", ch.SystMap()(1.37))
    cb.cp().process(["W"]).channel(['em']).AddSyst(cb, "CMS_em_W_LT_%s" % era, "lnN", ch.SystMap()(1.41))

    # et (norm)
    cb.cp().process(["QCD"]).channel(['et']).AddSyst(cb, "CMS_et_QCD_LT_%s" % era, "lnN", ch.SystMap()(1.164))
    cb.cp().process(["W"]).channel(['et']).AddSyst(cb, "CMS_et_W_LT_%s" % era, "lnN", ch.SystMap()(1.096))

    # et (shape)
    cb.cp().process(mc + dd).channel(['et']).AddSyst(cb, "CMS_scale_W_13TeV", "shape", ch.SystMap()(1.0))
    cb.cp().process(signal + mc + dd).channel(['et']).AddSyst(cb, "CMS_scale_t_13TeV", "shape", ch.SystMap()(1.0))

    # implementation of BSM3G (0/Zp  1/W  2/Z  3/TT  4/VV  5/QCD  6/H)
    # differences:
    # - Trig10 applies to VV
    # - Trig10 applies to emu rather than Trig30
    # - bbb handles STMC
    # - Close11 and Close15 replaced by LT params above
    # - Close31 and Close35 replaced by LT params above
    # - bID handled by shape above (losing correlation with mutau)
    # - TES handled by shape above
    # - remove TaID unc for emu
    # - remove TES  unc for emu

    # common
    cb.cp().process(signal + mc).AddSyst(cb, "lumi",    "lnN", ch.SystMap()(1.05))

    # et
    cb.cp().process(signal + mc  ).channel(['et']).AddSyst(cb, "Trig10",  "lnN", ch.SystMap()(1.01))
    cb.cp().process(["W"]        ).channel(['et']).AddSyst(cb, "ElID11",  "lnN", ch.SystMap()(1.01))
    cb.cp().process(["ZTT"]      ).channel(['et']).AddSyst(cb, "ElID12",  "lnN", ch.SystMap()(1.01))
    cb.cp().process(["TT"]       ).channel(['et']).AddSyst(cb, "ElID13",  "lnN", ch.SystMap()(1.01))
    cb.cp().process(["W", "ZTT"] ).channel(['et']).AddSyst(cb, "TaID00",  "lnN", ch.SystMap()(1.06))
    cb.cp().process(["TT"]       ).channel(['et']).AddSyst(cb, "TaID03",  "lnN", ch.SystMap()(1.06))
    cb.cp().process(["ZTT", "TT"]).channel(['et']).AddSyst(cb, "EES12",   "lnN", ch.SystMap()(1.01))
    # cb.cp().process(["ZTT"]      ).channel(['et']).AddSyst(cb, "bID02",   "lnN", ch.SystMap()(1.03))
    # cb.cp().process(["TT"]       ).channel(['et']).AddSyst(cb, "bID03",   "lnN", ch.SystMap()(1.1 ))
    # cb.cp().process(["ZTT"]      ).channel(['et']).AddSyst(cb, "TES02",   "lnN", ch.SystMap()(1.08))
    # cb.cp().process(["TT"]       ).channel(['et']).AddSyst(cb, "TES03",   "lnN", ch.SystMap()(1.08))
    # cb.cp().process(["W"]        ).channel(['et']).AddSyst(cb, "Close11", "lnN", ch.SystMap()(1.08))
    # cb.cp().process(["QCD"]      ).channel(['et']).AddSyst(cb, "Close15", "lnN", ch.SystMap()(1.15))

    # em
    cb.cp().process(signal + mc  ).channel(['em']).AddSyst(cb, "Trig10",  "lnN", ch.SystMap()(1.01)) # same as et (SingleEle)
    cb.cp().process(["W"]        ).channel(['em']).AddSyst(cb, "ElID31",  "lnN", ch.SystMap()(1.01))
    cb.cp().process(["ZTT"]      ).channel(['em']).AddSyst(cb, "ElID32",  "lnN", ch.SystMap()(1.01))
    cb.cp().process(["TT"]       ).channel(['em']).AddSyst(cb, "ElID33",  "lnN", ch.SystMap()(1.01))
    cb.cp().process(["ZTT", "TT"]).channel(['em']).AddSyst(cb, "EES32",   "lnN", ch.SystMap()(1.01))
    # cb.cp().process(["ZTT"]      ).channel(['em']).AddSyst(cb, "bID02",   "lnN", ch.SystMap()(1.03))
    # cb.cp().process(["TT"]       ).channel(['em']).AddSyst(cb, "bID03",   "lnN", ch.SystMap()(1.1 ))
    # cb.cp().process(["W"]        ).channel(['em']).AddSyst(cb, "Close11", "lnN", ch.SystMap()(1.08))
    # cb.cp().process(["QCD"]      ).channel(['em']).AddSyst(cb, "Close15", "lnN", ch.SystMap()(1.15))

    # mt
    cb.cp().process(signal + mc  ).channel(['mt']).AddSyst(cb, "Trig00",  "lnN", ch.SystMap()(1.01))
    cb.cp().process(["W", "ZTT"] ).channel(['mt']).AddSyst(cb, "TaID00",  "lnN", ch.SystMap()(1.06))
    cb.cp().process(["TT"]       ).channel(['mt']).AddSyst(cb, "TaID03",  "lnN", ch.SystMap()(1.06))
    cb.cp().process(["ZTT"]      ).channel(['mt']).AddSyst(cb, "bID02",   "lnN", ch.SystMap()(1.03))
    cb.cp().process(["TT"]       ).channel(['mt']).AddSyst(cb, "bID03",   "lnN", ch.SystMap()(1.12))
    cb.cp().process(["ZTT", "TT"]).channel(['mt']).AddSyst(cb, "MMS02",   "lnN", ch.SystMap()(1.01))
    cb.cp().process(["ZTT"]      ).channel(['mt']).AddSyst(cb, "TES02",   "lnN", ch.SystMap()(1.07))
    cb.cp().process(["TT"]       ).channel(['mt']).AddSyst(cb, "TES03",   "lnN", ch.SystMap()(1.09))
    cb.cp().process(["W"]        ).channel(['mt']).AddSyst(cb, "Close01", "lnN", ch.SystMap()(1.08))
    cb.cp().process(["QCD"]      ).channel(['mt']).AddSyst(cb, "Close05", "lnN", ch.SystMap()(1.15))

    # tt
    cb.cp().process(signal       ).channel(['tt']).AddSyst(cb, "Trig20",  "lnN", ch.SystMap()(1.21))  # only signal?
    cb.cp().process(["W"]        ).channel(['tt']).AddSyst(cb, "TaID00",  "lnN", ch.SystMap()(1.3 ))  # common?
    cb.cp().process(["ZTT"]      ).channel(['tt']).AddSyst(cb, "TaID00",  "lnN", ch.SystMap()(1.12))  # common?
    cb.cp().process(["TT"]       ).channel(['tt']).AddSyst(cb, "TaID03",  "lnN", ch.SystMap()(1.12))
    cb.cp().process(["W"]        ).channel(['tt']).AddSyst(cb, "bID20",   "lnN", ch.SystMap()(1.1 ))  # mislabeled?
    cb.cp().process(["ZTT"]      ).channel(['tt']).AddSyst(cb, "bID21",   "lnN", ch.SystMap()(1.03))  # mislabeled?
    cb.cp().process(["TT"]       ).channel(['tt']).AddSyst(cb, "bID23",   "lnN", ch.SystMap()(1.1 ))
    cb.cp().process(["W"]        ).channel(['tt']).AddSyst(cb, "TES01",   "lnN", ch.SystMap()(1.11))
    cb.cp().process(["ZTT"]      ).channel(['tt']).AddSyst(cb, "TES02",   "lnN", ch.SystMap()(1.11))
    cb.cp().process(["TT"]       ).channel(['tt']).AddSyst(cb, "TES03",   "lnN", ch.SystMap()(1.11))
    cb.cp().process(["W"]        ).channel(['tt']).AddSyst(cb, "Close01", "lnN", ch.SystMap()(1.37))
    cb.cp().process(["QCD"]      ).channel(['tt']).AddSyst(cb, "Close05", "lnN", ch.SystMap()(1.08))


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
