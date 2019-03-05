import argparse
import os
import sys
import json
import pandas as pd
import scipy.io
from SoluteParser import SoluteParser


aparser = argparse.ArgumentParser()
required_arguments = aparser.add_argument_group('required arguments')
required_arguments.add_argument('--results-dir', '--rd',
                                help='path to the directory containing all the configurations. Results will be stored '
                                     'in that directory', required=True)
args = aparser.parse_args()

res_dir = os.path.realpath(args.results_dir)

supported_variables = ['Bulk_d', 'DisperL', 'DisperT', 'DifW', 'SnkL1', 'Conc', 'h']

with open(os.path.join(res_dir, 'configurations.json')) as configurations:
    configuration_details = json.load(configurations)

data = {var: [] for var in supported_variables + ['t', 'CumCh1', 'configuration', 'group']}


for var in supported_variables:
    for conf_dir in configuration_details[var].keys():
        print(f'extracting results from {conf_dir}')
        if not os.path.isdir(os.path.join(res_dir, conf_dir)):
            continue
        solute_file = os.path.join(res_dir, conf_dir, 'solute1.out')
        if not os.path.exists(solute_file):
            print(f'{conf_dir} does not contain the expected result file, please run HYDRUS before running this script')
            sys.exit(1)
        solute = SoluteParser(solute_file)
        for t, cum_ch in solute:
            for v in supported_variables:
                data[v].append(configuration_details[var][conf_dir][v])
            data['configuration'].append(conf_dir.replace('_', ' ').replace('configuration', 'config'))
            data['t'].append(float(t))
            data['CumCh1'].append(float(cum_ch))
            data['group'].append(var)
    
print(f'formatting results...')
df = pd.DataFrame(data)
print(f'saving pickle file...')
df.to_pickle(os.path.join(res_dir, 'results.pkl'))
print(f'saving excel file...')
df.to_excel(os.path.join(res_dir, 'results.xlsx'))
print(f'saving MATLAB file...')
scipy.io.savemat(os.path.join(res_dir, 'res.mat'), mdict={'res':res.values[:,:9], 'other':res.values[:,9:]})
