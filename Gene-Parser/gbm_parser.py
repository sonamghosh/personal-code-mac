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


def parse_mutation_data(gene):
    """
    insert documentation here
    Poggers

    note:
    consider adding more params for genetic_profile_id
    and case_set_id
    """
    # Link to query
    url = 'http://www.cbioportal.org/webservice.do?'+\
          'cmd=getProfileData&genetic_profile_id=gbm_tcga_mutations'+\
          '&id_type=gene_symbol&gene_list='+gene+'&case_set_id=gbm_tcga_cnaseq'
    # Send Request to Database
    req = requests.get(url)

    data = req.text
    # Get all information after the string that shows the Gene
    data = data.split(gene.upper(), 1)[1]
    # Turn string into a list by looking for tab deliminator
    data_list = data.split("\t")
    # Get Rid of first value which is a blank
    data_list.pop(0)  # TODO: Consider removing any potential blanks(?)
    # Get rid of \n in elements
    for i in range(len(data_list)):
        if data_list[i].endswith("\n"):
            # Remove \n and update entry
            data_list[i] = data_list[i][:-1]  # TODO: Check if this only happens on the last elem and avoid loop

    return data_list


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
print(alter_nums/len(d2_list) * 100)
print(len(d2_list), len(d_list))
print((round(not_nan_nums) + round(alter_nums))/(len(d2_list)) * 100)

#pretty_json = json.loads(req2.text)
#print(json.dumps(pretty_json, indent=2))
