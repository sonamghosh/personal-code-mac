import requests
import numpy as np
import json
import argparse
import re
import itertools


def parse_genomic_data(gene, genetic_profile_id):
    """
    insert documentation here
    Poggers

    note:
    consider adding more params for
    and case_set_id

    Known profile ids:
    gbm_tcga_mutations
    gbm_tcga_gistic
    """
    # Link to query
    url = 'http://www.cbioportal.org/webservice.do?'+\
          'cmd=getProfileData&genetic_profile_id='+genetic_profile_id+\
          '&id_type=gene_symbol&gene_list='+gene+'&case_set_id=gbm_tcga_cnaseq'
    # Send Request to Database
    req = requests.get(url)
    # Grab data from request
    data = req.text
    # Get all information after the string that shows the Gene
    data = data.split(gene.upper(), 1)[1]
    # Turn string into a list by looking for tab deliminator and commas
    data_list = data.split("\t")
    #data_list = re.split("\t|,", data)
    # Get Rid of first value which is a blank
    data_list.pop(0)  # TODO: Consider removing any potential blanks(?)
    # Get rid of \n in elements
    if data_list[-1].endswith("\n"):
        # Remove \n and update entry
        data_list[-1] = data_list[-1][:-1]

    # Return a tag for type of data
    if genetic_profile_id == 'gbm_tcga_mutations':
        tag = 'mutation-data'
    elif genetic_profile_id == 'gbm_tcga_gistic':
        tag = 'copy-number-data'

    # Return data and type tag as a tuple
    return (tag, data_list)


def gene_profile_id_summarize(data):
    """
    [(tag, gene_data), (tag, gene_data)]
    """
    for i in range(len(data)):
        if data[i][0] == 'mutation-data':
            nan_nums = data[i][1].count('NaN') + data[i][1].count('0')
            not_nan_nums = len(data[i][1]) - nan_nums
            num_cases = len(data[i][1])
            mutation_percent = round(not_nan_nums/num_cases * 100)

        elif data[i][0] == 'copy-number-data':
            cna_nums = data[i][1].count('-2') + data[i][1].count('2')
            not_available_data = data[i][1].count('NA')
            tot = len(data[i][1]) - not_available_data
            #ones_nums = data[1].count('1') + data[1].count('-1')
            cna_percent = round(cna_nums/tot * 100)

    return mutation_percent, cna_percent

def genomic_alteration_summary(gene_arr):
    """
    Does overall summary for single or multi gene
    Write documentation later

    """
    # Get the dimensions of the array
    r, c = gene_arr.shape
    # Set a target array of values to look for
    target = np.array(['NaN', '0', '-1', '1'])
    # Initialize counter to count number of alterations
    cnt = 0
    # Iterate through every row
    for i in range(r):
        # Array to hold bool vals if target value is found
        bool_arr = np.in1d(gene_arr[i, :], target)
        # Iterate counter iff all values are not True
        if np.count_nonzero(bool_arr) != c:
            cnt += 1

    # Divide by number of samples (corresponds to num of rows)
    tot_percent = round(cnt/r * 100)

    return tot_percent


def main():
    parser = argparse.ArgumentParser(description='TBA')
    parser.add_argument('-g, --gene', type=str, nargs='+',
                        required=True, help='foobar', dest='gene')
    # Not sure if the bottom one will even be needed
    parser.add_argument('-p, --profile_id', type=str,
                        choices=['gbm_tcga_mutations', 'gbm_tcga_gistic'],
                        help='foobar', dest='profile_id')

    args = parser.parse_args()

    # If gene argument only has one gene mentioned then execute
    # profile_id summary method to find mutation percent,
    # count number alteration and total alteration percentages
    if len(args.gene) == 1:
        # Grab Data
        mut_data = parse_genomic_data(args.gene[0], 'gbm_tcga_mutations')
        cna_data = parse_genomic_data(args.gene[0], 'gbm_tcga_gistic')
        # Get mutation and cna alteration percentages
        mut_percent, cna_percent = gene_profile_id_summarize([mut_data, cna_data])
        # Convert data into Matrix
        gene_mat = np.column_stack((mut_data[1], cna_data[1]))
        # Get total percentage
        tot_percent = genomic_alteration_summary(gene_mat)
        # Print results
        print(args.gene[0], 'is mutated in', mut_percent,'% of all cases.')
        print(args.gene[0], 'is copy number altered in', cna_percent, '% of all cases.')
        print('Total % of cases where', args.gene[0], 'is altered by either',
              ' mutation or copy number alteration:', tot_percent, '% of all cases.')



if __name__ == "__main__":
    main()

"""

genes = ['TP53', 'MDM2', 'MDM4']
mut = 'gbm_tcga_mutations'
copy_alt = 'gbm_tcga_gistic'

tp53_mut = parse_genomic_data(genes[0], mut)
tp53_cn = parse_genomic_data(genes[0], copy_alt)
mdm2_mut = parse_genomic_data(genes[1], mut)
mdm2_cn = parse_genomic_data(genes[1], copy_alt)
mdm4_mut = parse_genomic_data(genes[2], mut)
mdm4_cn = parse_genomic_data(genes[2], copy_alt)


# Turn into 273 by 6 Matrix
gen_d = np.column_stack((tp53_mut[1], tp53_cn[1],
                         mdm2_mut[1], mdm2_cn[1],
                         mdm4_mut[1], mdm4_cn[1]))



print(gen_d.shape)

cnt = 0
r, c = gen_d.shape
target = np.array(['NaN', '0', '-1', '1'])
for i in range(r):
    #bool_arr = (target[:, None] == gen_d[i, :]).any(axis=-1)
    bool_arr = np.in1d(gen_d[i, :], target)
    print('Row ', i, ' ', bool_arr)
    if np.count_nonzero(bool_arr) != c:
        cnt += 1

print('Number of genes altered out of 273 is ', cnt)

cnt = 0
tp53_d = np.column_stack((tp53_mut[1], tp53_cn[1]))
r, c = tp53_d.shape
for i in range(r):
    bool_arr = np.in1d(tp53_d[i, :], target)
    if np.count_nonzero(bool_arr) != c:
        cnt += 1

print('Number of alterations in TP53 is ', cnt)
print(cnt / 273 * 100, '%')

# Test
#out = genomic_alteration_summary(gen_d)
#print(out)
"""