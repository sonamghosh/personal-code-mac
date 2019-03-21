import requests
import numpy as np
import json
import argparse
import re
import itertools

# Mutation Query
url1 = 'http://www.cbioportal.org/webservice.do?'+\
        'cmd=getProfileData&genetic_profile_id=gbm_tcga_mutations'+\
        '&id_type=gene_symbol&gene_list=TP53&case_set_id=gbm_tcga_cnaseq'

# Copy Number allterations for TP53
url2 = 'http://www.cbioportal.org/webservice.do?'+\
    'cmd=getProfileData&genetic_profile_id=gbm_tcga_gistic'+\
    '&id_type=gene_symbol&gene_list=TP53&case_set_id=gbm_tcga_cnaseq'


# Test Requests to see how output looks like

req1 = requests.get(url1)

d = req1.text
split_txt1 = d.split("TP53", 1)[1]
#print(split_txt1)
#print(len(split_txt1))
d_list = split_txt1.split("\t")
d_list.pop(0)
#print(d_list)
if d_list[-1] == 'NaN\n':
    print('yes')
else:
    print('no')

for i in range(len(d_list)):
    if d_list[i].endswith("\n"):
        #print(i)
        d_list[i] = d_list[i][:-1]

#print(len(d_list))
#print(d_list)
nan_nums = d_list.count('NaN')
not_nan_nums = len(d_list) - nan_nums
#print(nan_nums)
#print(not_nan_nums)
#print(100 - nan_nums/len(d_list) * 100)


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
            cna_percent = round(alter_nums/tot * 100)

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
out = genomic_alteration_summary(gen_d)
print(out)
