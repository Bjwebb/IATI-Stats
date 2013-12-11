from settings import *
from collections import defaultdict
import inspect
import json
import os
import copy
import decimal
import argparse
import statsfunctions

parser = argparse.ArgumentParser()
parser.add_argument("--stats-module", help="Name of module to import stats from", default='stats')
args = parser.parse_args()

import importlib
stats = importlib.import_module(args.stats_module)


def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError

def dict_sum_inplace(d1, d2):
    for k,v in d2.items():
        if type(v) == dict or type(v) == defaultdict:
            dict_sum_inplace(d1[k], v)
        elif (type(d1) != defaultdict and not k in d1) or d1[k] is None:
            continue
        else:
            d1[k] += v

def make_blank():
    blank = {}
    for stats_object in [ stats.ActivityStats(), stats.ActivityFileStats(), stats.OrganisationStats(), stats.OrganisationFileStats(), stats.PublisherStats() ]:
        stats_object.blank = True
        for name, function in inspect.getmembers(stats_object, predicate=inspect.ismethod):
            if not statsfunctions.use_stat(stats_object, name): continue
            blank[name] = function()
    return blank

def aggregate():
    for newdir in ['aggregated', 'aggregated-file']:
        try:
            os.mkdir(newdir)
        except OSError: pass

    blank = make_blank()
    total = copy.deepcopy(blank)
    for folder in os.listdir(OUTPUT_DIR):
        publisher_total = copy.deepcopy(blank)

        for jsonfile in os.listdir(os.path.join(OUTPUT_DIR, folder)):
            subtotal = copy.deepcopy(blank)
            with open(os.path.join(OUTPUT_DIR, folder, jsonfile)) as jsonfp:
                stats_json = json.load(jsonfp, parse_float=decimal.Decimal)
                for activity_json in stats_json['elements']:
                    dict_sum_inplace(subtotal, activity_json)
                dict_sum_inplace(subtotal, stats_json['file'])

                with open(os.path.join('aggregated-file', jsonfile+'.json'), 'w') as fp:
                    json.dump(subtotal, fp, sort_keys=True, indent=2, default=decimal_default)
            dict_sum_inplace(publisher_total, subtotal)

        publisher_stats = stats.PublisherStats()
        publisher_stats.aggregated = publisher_total
        for name, function in inspect.getmembers(publisher_stats, predicate=inspect.ismethod):
            if not statsfunctions.use_stat(publisher_stats, name): continue
            publisher_total[name] = function()

        dict_sum_inplace(total, publisher_total)
        with open(os.path.join('aggregated', folder+'.json'), 'w') as fp:
            json.dump(publisher_total, fp, sort_keys=True, indent=2, default=decimal_default)

    with open('aggregated.json', 'w') as fp:
        json.dump(total, fp, sort_keys=True, indent=2, default=decimal_default)

if __name__ == '__main__':
    aggregate()
