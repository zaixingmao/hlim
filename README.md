####set up
```bash
ssh lxplus.cern.ch
export SCRAM_ARCH=slc6_amd64_gcc491
cmsrel CMSSW_7_4_7
cd CMSSW_7_4_7/src
cmsenv

git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
git checkout v6.3.0
cd ../..

git clone https://github.com/cms-analysis/CombineHarvester.git CombineHarvester
cd CombineHarvester
git checkout analysis-HIG-16-006-freeze-080416
cd ..

git clone https://github.com/zaixingmao/hlim.git
mkdir -p auxiliaries/shapes/Zp_1pb
mkdir -p auxiliaries/shapes/Zp_nominal

scram b -j 6
```

####generate .root files
```bash
cd CMSSW_7_4_7/src/hlim
cmsenv

# tt
# rm -rf Fitter/2017-06-08
mkdir -p Fitter/2017-06-08
rsync -av host:/x/y/z/NORMAL Fitter/2017-06-08/
rsync -av host:/x/y/z/UP     Fitter/2017-06-08/
rsync -av host:/x/y/z/DOWN   Fitter/2017-06-08/
./bsm2h.py
./plotFromDataCard.py --unblind --logY --width --FS=tt --subdir=Zp_1pb && cp -p bkgTemplate_tt.pdf ~/public_html/tmp/

# em/et/mt
## emacs cfg.py
## ./multi_bdt.py
cp -p Fitter/eleTau/htt_et.inputs-Zp-13TeV.root ../auxiliaries/shapes/Zp_1pb
cp -p Fitter/emu/htt_em.inputs-Zp-13TeV.root ../auxiliaries/shapes/Zp_1pb
./h2h.py
```

####run
```bash
cd CMSSW_7_4_7/src/hlim
cmsenv

./zp.py
./lim.py --limits --verbose
```
