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
print(nan_nums)
print(nan_nums/len(d_list) * 100)

#d = d.decode('ISO-8859-1').encode('utf8')

#print(req1.content)
#rawData = pd.read_csv(req1.text, encoding='ISO-8859-1', dtype=object)
#rint(rawData)
#req2 = requests.get(url2)
#print(req2.text)
#pretty_json = json.loads(req2.text)
#print(json.dumps(pretty_json, indent=2))
