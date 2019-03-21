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

def foobar1(data):
    num_cases = len(data[1])

    if data[0] == 'mutation-data':
        nan_nums = data[1].count('NaN') + data[1].count('0')
        mut_nums = len(data[1]) - nan_nums

        return mut_nums, num_cases
    elif data[0] == 'copy-number-data':
        alter_nums = data[1].count('-2') + data[1].count('2')

        return alter_nums, num_cases

def foobar2(mut_nums, alter_nums, num_cases):
    mutation_percent = round(mut_nums/num_cases * 100)
    alter_percent = round(alter_nums/num_cases * 100)
    tot_percent = round((mut_nums + alter_nums)/num_cases * 100)

    return mutation_percent, alter_percent, tot_percent

def foobar3(mut_nums_arr, alter_nums_arr, num_cases):
    assert num_cases == 273
    k = len(mut_nums_arr)
    tot_muts = sum(mut_nums_arr)
    tot_alter = sum(alter_nums_arr)

    return round((tot_muts+tot_alter)/(1*num_cases) * 100)

def genomic_summarize(data):
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
            alter_nums = data[i][1].count('-2') + data[i][1].count('2')
            not_available_data = data[i][1].count('NA')
            tot = len(data[i][1]) - not_available_data
            #ones_nums = data[1].count('1') + data[1].count('-1')
            alter_percent = round(alter_nums/tot * 100)

    # Summarize data
    tot_percent = round((not_nan_nums + alter_nums)/num_cases * 100)

    # Return all three numbers
    return tot_percent, mutation_percent, alter_percent

"""

# Tests ############################################################
req2 = requests.get(url2)
##print(req2.text)
d2 = req2.text
d2 = d2.split('TP53', 1)[1]
d2_list = d2.split("\t")
d2_list.pop(0)

if d2_list[-1].endswith("\n"):
    d2_list[-1] = d2_list[-1][:-1]
#print(d2_list)

alter_nums = d2_list.count('-2')
ignore_nums = d2_list.count('-1') + d2_list.count('1')
#print(alter_nums/(len(d2_list)) * 100)
#print(len(d2_list), len(d_list))
#print(round((not_nan_nums + alter_nums)/(len(d2_list)) * 100))

g1 = 'TP53'
g2 = 'gbm_tcga_mutations'
g3 = 'gbm_tcga_gistic'
out = parse_genomic_data(g1,g3)
out2 = parse_genomic_data(g1, g2)
##print(out)
out3, out4, out5 = genomic_summarize([out, out2])
#print(out3, out4, out5)

#print('MDM2 \n')
g4 = 'MDM2'
out = parse_genomic_data(g4, g3)
out2 = parse_genomic_data(g4, g2)
#print(out)
out3, out4, out5 = genomic_summarize([out, out2])
#print(out3, out4, out5)

#print(len(out[1]))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# big Test
genes = ['TP53', 'MDM2', 'MDM4']
mut = 'gbm_tcga_mutations'
copy_alt = 'gbm_tcga_gistic'

tp53_d1 = parse_genomic_data(genes[0], mut)
tp53_d2 = parse_genomic_data(genes[0], copy_alt)
mdm2_d1 = parse_genomic_data(genes[1], mut)
mdm2_d2 = parse_genomic_data(genes[1], copy_alt)
mdm4_d1 = parse_genomic_data(genes[2], mut)
mdm4_d2 = parse_genomic_data(genes[2], copy_alt)

tp53_mut_nums, num_cases = foobar1(tp53_d1)
tp53_copy_nums, num_cases = foobar1(tp53_d2)
mdm2_mut_nums, num_cases = foobar1(mdm2_d1)
mdm2_copy_nums, num_cases = foobar1(mdm2_d2)
mdm4_mut_nums, num_cases = foobar1(mdm4_d1)
mdm4_copy_nums, num_cases = foobar1(mdm4_d2)

mut_lst = [tp53_mut_nums, mdm2_mut_nums, mdm4_mut_nums]
copy_lst = [tp53_copy_nums, mdm2_copy_nums, mdm4_copy_nums]

out = foobar3(mut_lst, copy_lst, num_cases)
#print(out, ' %')


##print(mut_lst)
##print(tp53_d1)
##print(len(tp53_d1[1]))
##print(len(mdm2_d1[1]))

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
