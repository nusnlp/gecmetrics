## A Reassessment of Reference-Based Grammatical Error Correction Metrics

If you use the data/code from this repository, please cite the following paper:
```
@InProceedings{chollampatt2018reassessment,
  author    = {Chollampatt, Shamil and Ng, Hwee Tou},
  title     = {A Reassessment of Reference-Based Grammatical Error Correction Metrics},
  booktitle = {Proceedings of the  27th International Conference on Computational Linguistics },
  month     = {August},
  year      = {2018},
  address   = {Santa Fe, New Mexico},
  note      = {To appear}
}
```

The directory structure is as follows:
```
├── data
│   └── conll14st-test
│       ├── conll14st-test.ieval.xml
│       ├── conll14st-test.m2
│       ├── conll14st-test.tok.src
│       └── refs
│           ├── conll14st-test.tok.trg0
│           └── conll14st-test.tok.trg1
├── README.md
├── run.sh
├── scores
│   ├── sentence_pairwiseranks_humans
│   │   ├── expanded.csv.gz
│   │   └── unexpanded.csv.gz
│   ├── sentence_scores_metrics
│   │   ├── gleu.txt.gz
│   │   ├── imeasure.txt.gz
│   │   └── m2score.txt.gz
│   ├── system_scores_humans
│   │   ├── expected_wins.txt.gz
│   │   └── trueskill.txt.gz
│   └── system_scores_metrics
│       ├── gleu.txt.gz
│       ├── imeasure.txt.gz
│       └── m2score.txt.gz
├── scripts
│   ├── sentence_correlation.py
│   └── system_correlation.py
└── tools
    └── significance-williams

```

* The `scores/system_scores_{humans,metrics}`/ directory contains human and metric scores at system level

* The `scores/sentence_scores_metrics}`/ directory contains metric scores at sentence level.

* The `scores/sentence_pairwiseranks_humans}`/ directory contains human pairwise rankings of system output sentences.


* Human judgments are obtained from: [https://github.com/grammatical/evaluation/](https://github.com/grammatical/evaluation/)

* Three automatic GEC metrics are used:
 1. [GLEU](https://github.com/cnap/gec-ranking/commit/50b5032a4ef2444b9381fb47a55b3bac0654a6d7)
 2. [I-measure](https://github.com/mfelice/imeasure/commit/fc79fdfd36d338299274b8a357c3cd09cc19d8a5)
 3. [MaxMatch or M^2 score](https://github.com/nusnlp/m2scorer/tree/2122ffd0f7a17b6e969131e42fa3a4eae7cff389)

* Data used to run metrics are from CoNLL-2014 shared task (given in `data/` directory)

* Scripts to find system-level and sentence-level correlations are adapted from WMT (given in `scripts/` directory)

* William's significance test was done using the code in `tools/significance-williams/` directory.

#### Running

To run the system and obtain system-level (+significance tests) and sentence-level scores, run:
`./run.sh`

The results are stored in `results/` directory.
