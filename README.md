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
cd ../HiggsToTauTau
git checkout MSSM-paper

git clone https://github.com/zaixingmao/hlim setup-Hhh/tt
patch -p0 setup-Hhh/tt/patches.txt
cp -p setup-Hhh/tt/HTT_TT_X_template.C test/templates/
cp -p setup-Hhh/tt/test.gitignore test/.gitignore
cd ../..

scram b -j 4
```

####run
```bash
cd CMSSW_7_1_5/src
cmsenv
cd HiggsAnalysis/HiggsToTauTau/setup-Hhh/tt
./make_root_files.py
./go.py --file=root/xx.root --full
```
