#!/usr/bin/env python3.4

# Adapted from WMT 2016 metrics task script.

from textwrap import dedent
from scipy.stats import spearmanr
from scipy.stats import pearsonr
from collections import defaultdict
import gzip
import csv
import argparse
import sys
import glob
import math
import os
from tabulate import tabulate

alpha = 0.05

def parse_args():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
            description="""This script computes system level correlations for wmt metrics task.
            It processes all system level submissions files and produces a nice table with correlations
            for each metric and each language direction.
            """)

    parser.add_argument("--metrics",
            help="file(s) with metrics scores, if ommited or '-' used stdin will be used",
            metavar="FILE",
            nargs='+',
            #type=argparse.FileType('r'),
            default=[sys.stdin],
            )

    parser.add_argument("--human",
            help="file with the official human scores",
            required=True,
            metavar="FILE",
            #type=argparse.FileType('r'),
            )

    parser.add_argument("--samples",
            help="files with generated samples with human scores for confidence estimation",
            metavar="FILE",
            nargs='*',
            default=[],
            )

    parser.add_argument("--directions",
            help="directions you want to show correlations for",
            metavar="DIRECTION",
            nargs='*')

    parser.add_argument("--tablefmt",
            help="Output table format (used by tabulate package)",
            default="plain",
            choices=["plain","simple","grid","pipe","orgtbl","rst","mediawiki","latex"]
            )

    parser.add_argument("--plot-scores",
            help="Plot human and metric's scores for each metric and direction to specified directory",
            metavar="OUT_DIR",
            default=None,
            dest='plot_out_dir',
            )

    return parser.parse_args()

config = parse_args()

def main():
    # Load data
    data = SystemLevelMetricsData()
    for file in config.metrics:
        data.add_metrics_data(file)
    data.add_human_data(config.human)
    for filename in config.samples:
    	data.add_sample_data(filename)

    # Compute results
    if not config.directions:
        config.directions = list(data.directions)
    result_table = ResultTable(data, config.directions)

    # Print results
    print(result_table.tabulate())

class KeyAlreadySetException(Exception): pass
class NumberOfFieldsNotExpectedException(Exception): pass

class MetricLanguagePairData(dict):
    """ Dictionary like object which for a given metric and a given language direction
    stores all systems' scores. The keys are systems and values are metric's scores.
    """

    def __setitem__(self, key, val):
        """This method overrides classic dictionary element assignment.
        It's only function is to checks that no system score is assigned twice.
        """
        if key in self:
            raise KeyAlreadySetException("The system %s score is already in the data" % key)
        dict.__setitem__(self, key, val)

    def correlation(self, other, corr_type):
        """Computes the spearman or pearson correlation of metric scores and
        given human scores """

        set1 = set(self)
        set2 = set(other)
        intersection = set1 & set2

        # Checks that the sets of used systems are equal
        if set1 != set2:
            print(dedent("""\
                    The sets of system are not equal:
                    missing human: %s
                    missing metrics: %s
                    using intersection: %s
                    """) % (
                        ", ".join(sorted(set1 - set2)),
                        ", ".join(sorted(set2 - set1)),
                        ", ".join(sorted(intersection))
                        ), file=sys.stderr)

        systems_fixed_order = list(intersection)
        scores1 = list(map(self.get, systems_fixed_order))
        scores2 = list(map(other.get, systems_fixed_order))

        if corr_type == "pearson":
            corr_func = pearsonr
        else:
            corr_func = spearmanr

        correlation, p_value = corr_func(scores1, scores2)
        return correlation

class MetricData(defaultdict):
    """Dictionary like object which for a given metric stores all systems' scores for
    all language direction. The keys are language directions and values are objects
    of MetricLanguagePairData class
    """
    def __init__(self):
        defaultdict.__init__(self, MetricLanguagePairData)

class SystemLevelMetricsData(object):
    """ Stores scores for all metrics, language directions and systems. Also stores human scores
    for all language direction and systems.
    """
    def __init__(self):
        self.metrics_data = defaultdict(MetricData)
        self.sample_data_list = []
        self.directions = set()

    def iter_records(self, file_like):
        for file in glob.glob(file_like):
            with gzip.open(file, mode="rt") as f:
                for line in csv.reader(f, delimiter='\t'):
                    if len(line) != 5:
                        raise NumberOfFieldsNotExpectedException("Got %s fields in file %s" % (len(line), file))

                    metric    = line[0]
                    lang_pair = line[1]
                    test_set  = line[2]
                    system    = line[3]
                    score     = float(line[4])

                    yield metric, lang_pair, system, score


    def add_metrics_data(self, file):
        for metric, lang_pair, system, score in self.iter_records(file):
            self.metrics_data[metric][lang_pair][system] = score

    def load_human_data(self, file):
        data = MetricData()
        for metric, lang_pair, system, score in self.iter_records(file):
            data[lang_pair][system] = score
            self.directions.add(lang_pair)
        return data

    def add_human_data(self, file):
        self.human_data = self.load_human_data(file)

    def add_sample_data(self, file):
        self.sample_data_list.append(self.load_human_data(file))

    def metrics(self):
        return self.metrics_data.keys()

    def compute_correlation_confidence(self, metric, direction, corr_type):
        if metric not in self.metrics_data or direction not in self.metrics_data[metric]:
            return None, None

        correlation = self.compute_correlation(metric, direction, corr_type)
        confidence = self.compute_confidence(metric, direction, corr_type)

        return correlation, confidence

    def compute_correlation(self, metric, direction, corr_type):
        metric_scores = self.metrics_data[metric][direction]
        human_scores = self.human_data[direction]

        # Plot the scores if requested
        if (config.plot_out_dir):
            self.plot_scores(metric_scores, human_scores, metric, direction)

        return metric_scores.correlation(human_scores, corr_type)

    def compute_confidence(self, metric, direction, corr_type):
        # We may have no samples
        if not self.sample_data_list:
            return None

        metric_scores = self.metrics_data[metric][direction]

        corrs = []
        for human_data in self.sample_data_list:
            human_scores = human_data[direction]
            corr = metric_scores.correlation(human_scores, corr_type)
            corrs.append(corr)

        avg_corr = sum(corrs) / len(corrs)

        corrs.sort()

        l_corr = corrs[int(len(corrs) * alpha/2)]
        r_corr = corrs[int(len(corrs) * (1 - alpha/2))]
        return abs(l_corr - r_corr) / 2

    def plot_scores(self, metric_scores, human_scores, metric, direction):

        fig_format = "png"

        out_file_name = os.path.join(config.plot_out_dir, "scores-%s-%s.%s" % (metric, direction, fig_format))

        metric_keys = metric_scores.keys()
        human_keys = human_scores.keys()
        common_keys = list(set(metric_keys) & set(human_keys))

        y_points = [metric_scores[key] for key in common_keys ]
        x_points = [human_scores[key] for key in common_keys ]

        import matplotlib.pyplot as plt
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)
        ax.plot(x_points, y_points, 'ro')
        ax.set_xlabel('human score')
        ax.set_ylabel('metric score')

        spear, foo = spearmanr(x_points, y_points)
        pears, foo = pearsonr(x_points, y_points)

        ax.set_title("%s scores in direction %s \nSpearman: %.3f, Pearson: %.3f" % (metric, direction, spear, pears))

        for key, x, y in zip(common_keys, x_points, y_points):
            ax.annotate(
                    key,
                    (x,y),
                    xytext=(8,0),
                    textcoords = 'offset points', ha = 'left', va = 'baseline',
                    )

        fig.savefig(out_file_name)

class ResultTable(object):
    def __init__(self, data, directions):
        self.directions = directions
        self.rows = sorted(filter(None, (ResultRow(data, metric, self.directions) for metric in data.metrics())))
        self.find_col_max()

    def find_col_max(self):
        max_results = [safe_max(col) for col in zip(*[row.results for row in self.rows])]
        for row in self.rows:
            row.max_results = max_results

    def header(self):
        header_list = ["Metric"] + [direction + ' (Pearson)' for direction in self.directions] + ["Average (Pearson)" ,"Spearman"]
        if config.tablefmt == "latex":
            return ["\\textbf{%s}" % header for header in header_list]
        else:
            return header_list

    def __iter__(self):
        yield self.header()
        for row in self.rows:
            yield row

    def tabulate(self):
        return tabulate(
            self.rows,
            headers=self.header(),
            tablefmt=config.tablefmt,
            floatfmt='.3f',
            missingval='n/a',
            numalign='left',
        )


class ResultRow(object):
    def __init__(self, data, metric, directions):
        self.metric = metric

        # Compute pearson corrs for each direction
        self.results = []
        self.confidences = []
        for direction in directions:
            corr, confidence = data.compute_correlation_confidence(metric, direction, "pearson")
            self.results.append(corr)
            self.confidences.append(confidence)

        # Compute average results
        self.avg = safe_avg(self.results)
        self.results.append(self.avg)
        self.confidences.append(safe_avg(self.confidences))

        # Compute averate spearman
        spear_results = []
        spear_confidences = []
        for direction in directions:
            corr, confidence = data.compute_correlation_confidence(metric, direction, "spearman")
            spear_results.append(corr)
            spear_confidences.append(confidence)
        self.results.append(safe_avg(spear_results))
        self.confidences.append(safe_avg(spear_confidences))

    def any_none(self):
        return any([x is None for x in self.results])

    def sort_key(self):
        return (self.any_none(), -self.avg)

    def __lt__(self, other):
        return self.sort_key() < other.sort_key()

    def __iter__(self):
        if config.tablefmt == "latex":
            yield "\\metric{%s}" % self.metric
        else:
            yield self.metric

        for result, confidence, maximum in zip(self.results, self.confidences, self.max_results):
            if result is not None:
                if confidence is not None:
                    if result == maximum:
                        if config.tablefmt == "latex":
                            yield "$\\best{%.3f} \pm %.3f$" % (result,confidence)
                        else:
                            yield "%.3f±%.3f" % (result,confidence)
                    else:
                        if config.tablefmt == "latex":
                            yield "$%.3f \pm %.3f$" % (result,confidence)
                        else:
                            yield "%.3f±%.3f" % (result,confidence)
                else:
                    if result == maximum:
                        if config.tablefmt == "latex":
                            yield "\\best{%.3f}" % result
                        else:
                            yield "%.3f" % result
                    else:
                        yield "%.3f" % result
            else:
                yield None

    def __bool__(self):
        return not all([x is None for x in self.results])

def safe_max(iterable):
    maximum = None
    for item in filter(None, iterable):
        if maximum is None:
            maximum = item
        else:
            maximum = max(maximum, item)
    return maximum

def safe_avg(iterable):
    filtered = list(filter(None, iterable))
    try:
        return sum(filtered) / len(filtered)
    except ZeroDivisionError:
        return None

if __name__ == "__main__":
    main()
