This is an adaptation of scripts from https://github.com/ygraham/significance-williams to calculate significance of correlations by William's Test.  The modified scripts assume that higher metric scores indicate better output, and vice versa.

```
Instructions for William's Significance Test for Evaluation of Automatic MT Metrics 
-----------------------------------------------------------------------------------

Contact: graham.yvette@gmail.com

-----------------------------------------------------------------------------------

Requirements:

1. "R Statistical Software"
	- To install R on the command line: 
	  > sudo apt-get install r-base

2. R's "psych" package 

	To install R's "psych" package:
	- IF your institution uses a proxy server, you need to tell R about it BEFORE 
	  installing any package, here's what to do:
		A) Open your R command line, by typing "R"
		B) Type the following commmand into R, remembering to provide your 
		   actual credentials and proxy server details:

        > Sys.setenv(http_proxy="http://myusername:mypasssord@myproxyserver.com:8080/")

        IF NOT, continue on below. 

	- Open R command line (by typing "R") and enter the following: 

        > install.packages("psych")

	  You'll be given an option of a CRAN site, when you have one selected, you 
          might need to answer "y" to some questions. When "psych" is finished 
          installing, type the following to quit R:

        > quit("no")

-----------------------------------------------------------------------------------

Usage:

bash williams-sig.sh <language pair> <human scores filename> <metric scores filename> <directory to write results>

Example:
bash williams-sig.sh es-en example-data/mt-systems-scored-by-humans example-data/mt-systems-scored-by-metrics example-data

The above command produces two files, the first containing Pearson correlations of 
each metric with human scores: 
	example-data/pearson-corr.es-en
Another containing the resulting p-value of William's test for the pair of metrics: 
	example-data/williams-results.es-en

To check everything ran correctly, you can compare the above files produced by the 
scripts with the following two files included in the download:
	example-output/orig.pearson-corr.es-en
	example-output/orig.williams-results.es-en

The version of William's test carried out is a one-tailed test. The resulting p-value 
of the test will be printed in the ROW of the metric with HIGHEST absolute Pearson 
correlation with human scores. The opposite cell for that same pair of metrics (in the 
row of the lowest absolute Pearson correlation metric) will contain "-". The test 
carried out is for significance of the DIFFERENCE in correlation between a pair of 
metric's absolute Pearson correlation with human scores. 

The script can be run on data for more than two metrics. Example data are included 
in this directory: "example-data-multi". The same command is used to call the script 
on this example data for multiple metrics:

bash williams-sig.sh es-en example-data-multi/mt-systems-scored-by-humans example-data-multi/mt-systems-scored-by-metrics example-data-multi

The input files can contain multiple language pairs data, as in example-data-multi. 
For example, to run the script for "en-fr" language pair, simply specify that language 
pair:

bash williams-sig.sh en-fr example-data-multi/mt-systems-scored-by-humans example-data-multi/mt-systems-scored-by-metrics example-data-multi

-----------------------------------------------------------------------------------

Example Data:

Example data is the Spanish-English shared translation task MT systems from WMT-12. 
They are scored by humans, in addition to all participating metrics in WMT'12 metrics 
shared task. To run the scripts on new data, simply provide scores in the format in 
the example files "example-data/mt-systems-scored-by-humans" and 
"example-data/mt-systems-scored-by-metrics". The required format is also decribed in 
detail below.

You should provide the script with the locations of two input files containing:
	(1) human scores;
	(2) metric scores. 
Below is a detailed description of their required format.

Human Scores File:
------------------
You need to provide the scripts with a tab-delimited file containing the human 
scores for a number of MT systems. The file must have the header row as in 
"example-data/mt-systems-scored-by-humans" (see below), the column METRIC should 
specify "HUMAN" for all human scores and the contents of the LP column should match 
the language pair abbreviation you use to call the script on the command line 
(eg "es-en" as below):
-------------------------------------------------------
METRIC	LP	TESTSET	SYSTEM	SCORE	          <--HEADER ROW SHOULD LOOK LIKE THIS
HUMAN	es-en	newstest2012	onlineA	61.9384
HUMAN	es-en	newstest2012	onlineB	61.3861
HUMAN	es-en	newstest2012	QCRI--primary	60.373
HUMAN	es-en	newstest2012	uedin-wmt12	58.4963
HUMAN	es-en	newstest2012	UPC	56.5355
HUMAN	es-en	newstest2012	GTH-UPM	52.3248
HUMAN	es-en	newstest2012	onlineD	51.1139
HUMAN	es-en	newstest2012	jhu-hiero	47.8846
HUMAN	es-en	newstest2012	onlineC	46.1035
HUMAN	es-en	newstest2012	onlineF	42.2644
HUMAN	es-en	newstest2012	onlineE	41.9155
HUMAN	es-en	newstest2012	uk-dan-moses	18.7297
-------------------------------------------------------

Metrics Scores File:
--------------------
You need to provide a tab-delimited file containing automatic metric scores for the 
same set of MT systems as the human scores file (also provided by you). Each MT 
system should be scored exactly once by each metric and a minimum of two metrics 
should be tested. It is fine just to include two metrics, for example BLEU (as a 
baseline) and your own metric. If more than two metrics are included in this file, 
the script will carry out significance tests for all pairs of metrics and produce 
a matrix of p-values. The header of the metrics scores file you provide to the 
script needs to read as the first line below (same as human file header) as in 
example-data/mt-systems-scored-by-humans (see below). The column LP should contain 
the same abbreviation you use to call the script and METRIC should specify the name 
of the correpsonding metric. You can include multiple language pairs data in the input 
files.
----------------------------------------------------------------------
METRIC	LP	TESTSET	SYSTEM	SCORE
AMBER	es-en	newstest2012	GTH-UPM	0.2107
AMBER	es-en	newstest2012	jhu-hiero	0.2104
AMBER	es-en	newstest2012	onlineA	0.2178
AMBER	es-en	newstest2012	onlineB	0.2224
AMBER	es-en	newstest2012	onlineC	0.1915
AMBER	es-en	newstest2012	onlineD	0.1922
AMBER	es-en	newstest2012	onlineE	0.1890
AMBER	es-en	newstest2012	onlineF	0.1822
AMBER	es-en	newstest2012	QCRI--primary	0.2186
AMBER	es-en	newstest2012	uedin-wmt12	0.2168
AMBER	es-en	newstest2012	uk-dan-moses	0.1759
AMBER	es-en	newstest2012	UPC	0.2167
BLEU_4_closest_cased	es-en	newstest2012	GTH-UPM	0.2888
BLEU_4_closest_cased	es-en	newstest2012	QCRI--primary	0.3286
BLEU_4_closest_cased	es-en	newstest2012	UPC	0.3202
BLEU_4_closest_cased	es-en	newstest2012	jhu-hiero	0.2922
BLEU_4_closest_cased	es-en	newstest2012	onlineA	0.3138
BLEU_4_closest_cased	es-en	newstest2012	onlineB	0.3753
BLEU_4_closest_cased	es-en	newstest2012	onlineC	0.2294
BLEU_4_closest_cased	es-en	newstest2012	onlineD	0.2299
BLEU_4_closest_cased	es-en	newstest2012	onlineE	0.2200
BLEU_4_closest_cased	es-en	newstest2012	onlineF	0.2171
BLEU_4_closest_cased	es-en	newstest2012	uedin-wmt12	0.3343
BLEU_4_closest_cased	es-en	newstest2012	uk-dan-moses	0.2240
posF	es-en	newstest2012	GTH-UPM	50.8772 
posF	es-en	newstest2012	jhu-hiero	50.7861 
posF	es-en	newstest2012	onlineA	52.4084 
posF	es-en	newstest2012	onlineB	52.5585 
posF	es-en	newstest2012	onlineC	48.6851 
posF	es-en	newstest2012	onlineD	48.9753 
posF	es-en	newstest2012	onlineE	47.2743 
posF	es-en	newstest2012	onlineF	47.5800 
posF	es-en	newstest2012	QCRI--primary	54.0183 
posF	es-en	newstest2012	uedin-wmt12	54.2129 
posF	es-en	newstest2012	uk-dan-moses	43.8312 
posF	es-en	newstest2012	UPC	53.6285 
-----------------------------------------------------------------------------------

Publication:

The signigicance test provided is described in detail in: 
"Testing for Significance of Increased Correlation with Human Judgment", 
Yvette Graham & Timothy Baldwin, EMNLP 2014.

-----------------------------------------------------------------------------------

```
