#!/usr/bin/env python

import CombineHarvester.CombineTools.ch as ch
import os

cb = ch.CombineHarvester()

auxiliaries  = os.environ['CMSSW_BASE'] + '/src/auxiliaries/'
aux_shapes   = auxiliaries +'shapes/'
era = "13TeV"

input_dirs = {
  'et' : 'Brown',
  'em' : 'Brown',
}
chns = sorted(input_dirs.keys())

bkg_procs = {
  'et' : ['ZTT', 'W', 'QCD', 'TT', 'VV'],
  'em' : ['ZTT', 'W', 'QCD', 'TT', 'VV'],
}

sig_procs = ['ggH']

cats = {
  'et_%s' % era : [
    (0, 'eleTau_inclusive'), 
  ],
  'em_%s' % era : [
    (0, 'emu_inclusive'), 
  ],
}

masses = ch.ValsFromRange('500:2000|500')

print '>> Creating processes and observations...'

for chn in chns:
    cats_chn = cats["%s_%s" % (chn, era)]
    cb.AddObservations(  ['*'],  ['htt'], [era], [chn],                 cats_chn      )
    cb.AddProcesses(     ['*'],  ['htt'], [era], [chn], bkg_procs[chn], cats_chn, False  )
    cb.AddProcesses(     masses, ['htt'], [era], [chn], sig_procs,      cats_chn, True   )


print '>> Extracting histograms from input root files...'
for chn in chns:
    file = aux_shapes + input_dirs[chn] + "/htt_" + chn + ".inputs-Zp-%s.root"  % era
    cb.cp().channel([chn]).era([era]).backgrounds().ExtractShapes(
        file, '$BIN/$PROCESS', '$BIN/$PROCESS_$SYSTEMATIC')
    cb.cp().channel([chn]).era([era]).signals().ExtractShapes(
        file, '$BIN/$PROCESS$MASS', '$BIN/$PROCESS$MASS_$SYSTEMATIC')

print '>> Merging bin errors and generating bbb uncertainties...'
bbb = ch.BinByBinFactory()
bbb.SetAddThreshold(0.1).SetMergeThreshold(0.5).SetFixNorm(True)

for chn in chns:
    cb_chn = cb.cp().channel([chn])
    bbb.MergeAndAdd(cb_chn.cp().era([era]).bin_id([0, 1, 2]).process(bkg_procs[chn]), cb)

print '>> Setting standardised bin names...'
ch.SetStandardBinNames(cb)

writer = ch.CardWriter('LIMITS/$TAG/$MASS/$ANALYSIS_$CHANNEL_$BINID_$ERA.txt',
                       'LIMITS/$TAG/common/$ANALYSIS_$CHANNEL.input.root')
#writer.SetVerbosity(1)
writer.WriteCards('cmb', cb)
for chn in chns:
    writer.WriteCards(chn,cb.cp().channel([chn]))

print '>> Done!'
