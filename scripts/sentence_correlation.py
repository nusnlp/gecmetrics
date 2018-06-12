#!/usr/bin/python3.4

# Adapted from WMT 2015 metrics task script.

from collections import defaultdict
from collections import namedtuple
import gzip
import glob
import csv
import argparse
import sys
import math
import random
import time
from tabulate import tabulate

alpha = 0.05

variants_definitions = {

        'noties' : {
            '<' : { '<': 1 , '=': 0 , '>':-1  },
            '=' : { '<':'X', '=':'X', '>':'X' },
            '>' : { '<':-1 , '=': 0 , '>': 1  },
            },

        'hties' : {
            '<' : { '<': 1 , '=': 0 , '>':-1  },
            '=' : { '<': 0 , '=': 1 , '>': 0  },
            '>' : { '<':-1 , '=': 0 , '>': 1  },
            },
        }

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
            description="""This script computes segment level correlations for wmt metrics task.
            It processes all segment level submissions files and produces a nice table with correlations
            for each metric and each language direction.
            """)

    parser.add_argument("--judgments",
            help="file with human judgments, type '-' for stdin",
            required=True,
            metavar="FILE",
            #type=argparse.FileType('r')
            )

    parser.add_argument("--metrics",
            help="file(s) with segment level metrics scores, type '-' for stdin",
            required=True,
            metavar="FILE",
            nargs='+',
            #type=argparse.FileType('r')
            )

    parser.add_argument("--directions",
            help="directions you want to show correlations for",
            metavar="DIRECTION",
            #default=["fr-en","fi-en","de-en","cs-en","ru-en","en-fr","en-fi","en-de","en-cs","en-ru"],
            nargs='*'
            )

    parser.add_argument("--variant",
            help="A variant of Kendall's tau computation",
            default="hties",
            choices=sorted(variants_definitions.keys())
            )

    parser.add_argument("--bootstrap",
            help="Performs the bootstrap resampling and computes 0.95 confidence"
                 " intervals. The optional parameter specifies the number of new"
                 " randomly sampled sets of human comparisons",
            metavar="N",
            nargs='?',
            const=1000,
            default=0,
            type=int,
            )

    parser.add_argument("--rseed",
            help="Random seed used to generate samples when bootstrapping (default is unix timestamp)",
            metavar="N",
            default=int(time.time()),
            type=int,
            )

    parser.add_argument("--tablefmt",
            help="Output table format (used by tabulate package)",
            default="plain",
            choices=["plain","simple","grid","pipe","orgtbl","rst","mediawiki","latex"]
            )

    return parser.parse_args()
config = parse_args()

def main():
    # Load data
    data = SegmentLevelData()
    for file in config.metrics:
        data.add_metrics_data(file)
    data.add_human_data(config.judgments)

    # Compute results
    if not config.directions:
        config.directions = [k for k, v in data.human_comparisons.items()]
    result_table = ResultTable(data, config.directions)


    print(result_table.tabulate())

class MetricLanguagePairData(defaultdict):
    """ Stores metric scores for given metric and for given language direction.
    The keys of this dictionary like object are names of system and values are
    dictionaries mapping from segment to score """

    def __init__(self):

        # values are dictionaries mapping segment number to actual metric score
        # The underlying dictionary is indexed by system name and its
        defaultdict.__init__(self, dict)

    def kendall_tau(self, human_comparisons, variant='wmt14'):

        try:
            coeff_table = variants_definitions[variant]
        except KeyError:
            raise ValueError("There is no definition for %s variant" % variant)

        numerator = 0
        denominator = 0

        # Iterate all human comparisons
        for segment, sys1, sys2, human_comparison in human_comparisons:

            sys1_metric_score = self[sys1].get(segment, None)
            sys2_metric_score = self[sys2].get(segment, None)
            #print(sys1_metric_score, sys1_metric_score, human_comparison)
            #print(self[sys1].get(segment,None),self[sys2].get(segment,None))
            if(sys1_metric_score is None or sys2_metric_score is None):
                return None

            # Get the metric comparison
            # (here the relation '<' means "is better then")
            compare = lambda x, y: '<' if x > y else '>' if x < y else '='
            metric_comparison = compare(sys1_metric_score, sys2_metric_score)

            # Adjust the numerator and denominator according the table with coefficients
            coeff = coeff_table[human_comparison][metric_comparison]
            if coeff != 'X':
                numerator += coeff
                denominator += 1
        # Return the Kendall's tau
        if denominator == 0:
            return 1
        return numerator / denominator

class SegmentLevelData(object):
    """ Stores scores for all metrics, language directions and systems. Also stores human scores
    for all language direction and systems.
    """

    def __init__(self):
        self.metrics_data = defaultdict(MetricLanguagePairData) # indexed by tuples (metric, direction)
        self.human_comparisons = defaultdict(list) # indexed by language direction
        self.direction_systems = defaultdict(set) # indexed by language directions

    def add_metrics_data(self, file_like):
        for file in glob.glob(file_like):
            with gzip.open(file, mode="rt") as f:
                for metric, lang_pair, test_set, system, segment, score in csv.reader(f, delimiter='\t'):
                    # Convert numerical values
                    segment = int(segment)
                    score = float(score)
                    if segment not in self.metrics_data[metric, lang_pair][system]:
                        self.metrics_data[metric, lang_pair][system][segment] = score
                    else:
                        print("Warning: ", metric, lang_pair, system, segment, "Segment score already exists." ,file=sys.stderr)
                    self.direction_systems[lang_pair].add(system)
    # def add_human_data(self, file_like):
    #     for file in glob.glob(file_like):
    #         with gzip.open(file, mode="rt") as f:
    #             last_line_system_ranks = []
    #             for line in csv.DictReader(f):
    #
    #                 direction = line['system1Id'].rsplit('.', 2)[1]
    #                 segment = int(line['srcIndex'])
    #
    #                 extract_system = lambda x: '.'.join(x.split('.')[1:-2])
    #
    #                 SystemsTuple = namedtuple("SystemTuple", ["id","rank"])
    #                 systems_ranks = [
    #                     SystemsTuple(id = extract_system(line['system1Id']), rank = int(line['system1rank'])),
    #                     SystemsTuple(id = extract_system(line['system2Id']), rank = int(line['system2rank'])),
    #                     ]
    #
    #                 systems_ranks2 = systems_ranks
    #                 if "PLACEHOLDER" in line.values():
    #                     systems_ranks2 = systems_ranks2 + last_line_system_ranks
    #
    #                 last_line_system_ranks = systems_ranks
    #
    #                 # Extract all comparisons (Making sure that two systems are extracted only once)
    #                 # Also the extracted relation '<' means "is better than"
    #                 compare = lambda x, y: '<' if x < y else '>' if x > y else '='
    #                 extracted_comparisons = [
    #                         (segment, sys1.id, sys2.id, compare(sys1.rank, sys2.rank))
    #                         for idx1, sys1 in enumerate(systems_ranks)
    #                         for idx2, sys2 in enumerate(systems_ranks2)
    #                         if idx1 < idx2
    #                         and sys1.rank != -1
    #                         and sys2.rank != -1
    #                     ]
    #
    #                 self.human_comparisons[direction] += extracted_comparisons

    def add_human_data(self, file_like):
        def find_lang(code):
            langdict = {'cze':'cs', 'eng':'en', 'fre':'fr', 'ces':'cs', 'deu':'de', 'fin':'fi', 'ron':'ro', 'rus':'ru', 'tur':'tr'}
            if code in langdict:
                return langdict[code]
            else:
                return code

        for file in glob.glob(file_like):
            with gzip.open(file, mode="rt") as f:
                for line in csv.DictReader(f):

                    #direction = line['system1Id'].rsplit('.', 2)[1]
                    direction = find_lang(line['srclang']) + '-' + find_lang(line['trglang'])
                    segment = int(line['segmentId'])

                    extract_system = lambda x: '.'.join(x.split('.')[1:-1])


                    id1 = extract_system(line['system1Id'])
                    rank1 = int(line['system1rank'])
                    id2 = extract_system(line['system2Id'])
                    rank2 = int(line['system2rank'])
                    if id1 not in self.direction_systems[direction] or id2 not in self.direction_systems[direction]:
                        continue
                    # Extract all comparisons (Making sure that two systems are extracted only once)
                    # Also the extracted relation '<' means "is better than"
                    compare = lambda x, y: '<' if x < y else '>' if x > y else '='
                    extracted_comparisons = [
                            (segment, id1, id2, compare(rank1, rank2))
                        ]

                    self.human_comparisons[direction] += extracted_comparisons

    def extracted_pairs(self, direction):
        return len(self.human_comparisons[direction])

    def compute_tau_confidence(self, metric, direction, variant):

        if (metric,direction) not in self.metrics_data:
            return None, None

        metric_data = self.metrics_data[metric,direction]
        comparisons = self.human_comparisons[direction]
        #print(self.human_comparisons[direction])
        #print(metric, direction, len(metric_data.keys()))
        #print(self.metrics_data[metric,direction][0])
        #print(self.metrics_data['ParFDA.4542'])
        #print(self.metrics_data['online-A.0.'])
        tau = metric_data.kendall_tau(comparisons, variant)

        confidence = self.compute_confidence(metric_data, comparisons, variant)

        return tau, confidence

    def compute_confidence(self, metric_data, comparisons, variant):
        if config.bootstrap == 0:
            return None

        # Setting random seed here, to generate same samples for all metrics and directions
        random.seed(config.rseed)

        taus = []
        for _ in range(config.bootstrap):
            sample = (random.choice(comparisons) for _ in comparisons)
            tau = metric_data.kendall_tau(sample, variant)
            if tau is None:
                return None
            taus.append(tau)

        taus.sort()

        avg_tau = sum(taus) / len(taus)

        l_tau = taus[int(config.bootstrap * alpha/2)]
        r_tau = taus[int(config.bootstrap * (1 - alpha/2))]
        return abs(l_tau - r_tau) / 2

    def metrics(self):
        return list(set(pair[0] for pair in self.metrics_data.keys()))

class ResultTable(object):
    def __init__(self, data, directions):
        self.directions = directions
        self.variant = config.variant
        self.other_variants = sorted(set(variants_definitions.keys()) - set([config.variant]))
        self.rows = sorted(filter(None, (ResultRow(data, metric, self.directions, self.variant, self.other_variants) for metric in data.metrics())))
        self.find_col_max()

    def find_col_max(self):
        max_results = [safe_max(col) for col in zip(*[row.results for row in self.rows])]
        for row in self.rows:
            row.max_results = max_results

    def header(self):
        header_list = ["Metric"] + [direction+' ('+self.variant+')' for direction in self.directions] + ["Average (" + self.variant + ")" ] + self.other_variants
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
    def __init__(self, data, metric, directions, variant, other_variants):
        self.metric = metric

        self.results = []
        self.confidences = []
        # Compute the main kendall's tau for each direction
        for direction in directions:
            tau, confidence = data.compute_tau_confidence(metric, direction, variant)
            self.results.append(tau)
            self.confidences.append(confidence)

        # Compute the average across directions
        self.avg = safe_avg(self.results)
        self.results.append(self.avg)
        self.confidences.append(safe_avg(self.confidences))

        # Compute other variants
        for variant in other_variants:

            variant_results = []
            variant_confidences = []
            for direction in directions:
                tau, confidence = data.compute_tau_confidence(metric, direction, variant)
                variant_results.append(tau)
                variant_confidences.append(confidence)

            self.results.append(safe_avg(variant_results))
            self.confidences.append(safe_avg(variant_confidences))

    def any_none(self):
        return any([result is None for result in self.results])

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
        return not all([result is None for result in self.results])

def safe_avg(iterable):
    filtered = list(filter(None, iterable))
    try:
        return sum(filtered) / len(filtered)
    except ZeroDivisionError:
        return None

def safe_max(iterable):
    maximum = None
    for item in filter(None, iterable):
        if maximum is None:
            maximum = item
        else:
            maximum = max(maximum, item)
    return maximum

if __name__ == "__main__":
    main()
