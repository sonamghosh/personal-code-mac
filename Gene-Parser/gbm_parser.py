import requests
import numpy as np
import pandas as pd
import json
import io

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
print(req1.text)
print(req1.encoding)


d = req1.text
split_txt1 = d.split("TP53", 1)[1]
print(split_txt1)
print(len(split_txt1))
d_list = split_txt1.split("\t")
d_list.pop(0)
print(d_list)
if d_list[-1] == 'NaN\n':
    print('yes')
else:
    print('no')

for i in range(len(d_list)):
    if d_list[i].endswith("\n"):
        print(i)
        d_list[i] = d_list[i][:-1]

print(len(d_list))
print(d_list)
nan_nums = d_list.count('NaN')
not_nan_nums = len(d_list) - nan_nums
print(nan_nums)
print(not_nan_nums)
print(100 - nan_nums/len(d_list) * 100)


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
    # Turn string into a list by looking for tab deliminator
    data_list = data.split("\t")
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


def genomic_summarize(data):
    if data[0] == 'mutation-data':
        nan_nums = data[1].count('NaN') + data[1].count('0')
        not_nan_nums = len(data[1]) - nan_nums
        mutation_percent = round(not_nan_nums/len(data[1]) * 100)

        return mutation_percent
    elif data[0] == 'copy-number-data':
        alter_nums = data[1].count('-2')
        not_available_data = data[1].count('NA')
        tot = len(data[1]) - not_available_data
        #ones_nums = data[1].count('1') + data[1].count('-1')
        alter_percent = round(alter_nums/tot * 100)

        return alter_percent


#d = d.decode('ISO-8859-1').encode('utf8')

#print(req1.content)
#rawData = pd.read_csv(req1.text, encoding='ISO-8859-1', dtype=object)
#rint(rawData)
req2 = requests.get(url2)
#print(req2.text)
d2 = req2.text
d2 = d2.split('TP53', 1)[1]
d2_list = d2.split("\t")
d2_list.pop(0)

if d2_list[-1].endswith("\n"):
    d2_list[-1] = d2_list[-1][:-1]
print(d2_list)

alter_nums = d2_list.count('-2')
ignore_nums = d2_list.count('-1') + d2_list.count('1')
print(alter_nums/(len(d2_list)) * 100)
print(len(d2_list), len(d_list))
print(round((not_nan_nums + alter_nums)/(len(d2_list)) * 100))

g1 = 'TP53'
g2 = 'gbm_tcga_mutations'
g3 = 'gbm_tcga_gistic'
out = parse_genomic_data(g1,g3)
#print(out)
out2 = genomic_summarize(out)
print(out2)
