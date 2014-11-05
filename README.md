####set up
```bash
ssh lxplus.cern.ch
cmsrel CMSSW_7_1_5
cd CMSSW_7_1_5/src
cmsenv

git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
git checkout slc6-root5.34.17
cd ../..

git clone https://github.com/cms-analysis/HiggsAnalysis-HiggsToTauTau HiggsAnalysis/HiggsToTauTau
cd HiggsAnalysis/HiggsToTauTau

git clone https://github.com/zaixingmao/hlim
git apply hlim/patches.txt
cp -p hlim/HTT_TT_X_template.C test/templates/
cp -p hlim/test.gitignore test/.gitignore
cd ../..

scram b -j 4
```

####run
```bash
cd CMSSW_7_1_5/src/HiggsAnalysis/HiggsToTauTau/hlim
cmsenv

./make_root_files.py xyz.root
./go.py --file=root/a.root --full
```
