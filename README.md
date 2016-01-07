####set up
```bash
ssh lxplus.cern.ch
cmsrel CMSSW_7_1_5
cd CMSSW_7_1_5/src
cmsenv

git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
git clone https://github.com/cms-analysis/CombineHarvester.git CombineHarvester
git clone https://github.com/roger-wolf/HiggsAnalysis-HiggsToTauTau-auxiliaries.git auxiliaries
git clone https://github.com/zaixingmao/hlim.git

scram b -j 4
```

####run
```bash
cd CMSSW_7_1_5/src/hlim
cmsenv

# edit cfg.py
./multi-bdt.py
./zp.py
./lim.py
```
