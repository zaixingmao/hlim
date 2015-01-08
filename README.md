####set up
```bash
ssh lxplus.cern.ch
cmsrel CMSSW_7_1_5
cd CMSSW_7_1_5/src
cmsenv

git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
git checkout v5.0.1
cd ../..

git clone https://github.com/cms-analysis/HiggsAnalysis-HiggsToTauTau HiggsAnalysis/HiggsToTauTau
cd HiggsAnalysis/HiggsToTauTau
source environment.sh

git clone https://github.com/zaixingmao/hlim
cp -p hlim/test.gitignore test/.gitignore
cd ../..

scram b -j 4
```

####run
```bash
cd CMSSW_7_1_5/src/HiggsAnalysis/HiggsToTauTau/hlim
cmsenv

# edit cfg.py
./make_root_files.py
./go.py --file=root/a.root --full
```
