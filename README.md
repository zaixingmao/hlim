####set up
```bash
ssh lxplus.cern.ch
export SCRAM_ARCH=slc6_amd64_gcc530
cmsrel CMSSW_8_1_0
cd CMSSW_8_1_0/src
cmsenv

git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
git checkout v7.0.9
cd ../..

git clone https://github.com/cms-analysis/CombineHarvester.git CombineHarvester

git clone https://github.com/zaixingmao/hlim.git
cd hlim
git checkout 2016
cd ..

scram b -j 6
```

####generate .root files
```bash
cd CMSSW_8_1_0/src/hlim
cmsenv

# (checkout Fitter)
mkdir -p auxiliaries/shapes/Zp_1pb
cd auxiliaries/shapes
ln -s Zp_1pb Brown
cd ../..

# tt
./bsm2h.py
./plotFromDataCard.py --unblind --logY --width --FS=tt --subdir=Zp_1pb && cp -p bkgTemplate_tt.pdf ~/public_html/tmp/

# em/et/mt
## emacs cfg.py
## ./multi_bdt.py
./plotFromDataCard.py --unblind --logY --width --FS=mt --subdir=Brown  && cp -p bkgTemplate_mt.pdf ~/public_html/tmp/
./plotFromDataCard.py --unblind --logY --width --FS=et --subdir=Brown  && cp -p bkgTemplate_et.pdf ~/public_html/tmp/
./plotFromDataCard.py --unblind --logY --width --FS=em --subdir=Brown  && cp -p bkgTemplate_em.pdf ~/public_html/tmp/
```

####run
```bash
cd CMSSW_7_4_7/src/hlim
cmsenv

./zp.py
./lim.py --limits --verbose
```
