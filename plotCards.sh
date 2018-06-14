#!/bin/sh

./plotFromDataCard.py --unblind --logY --width --FS=mt --subdir=Brown  && cp -p bkgTemplate_mt.pdf ~/public_html/tmp/
./plotFromDataCard.py --unblind --logY --width --FS=et --subdir=Brown  && cp -p bkgTemplate_et.pdf ~/public_html/tmp/
./plotFromDataCard.py --unblind --logY --width --FS=em --subdir=Brown  && cp -p bkgTemplate_em.pdf ~/public_html/tmp/
./plotFromDataCard.py --unblind --logY --width --FS=tt --subdir=Zp_1pb && cp -p bkgTemplate_tt.pdf ~/public_html/tmp/
