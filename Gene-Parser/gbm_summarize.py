import requests
import numpy as np
import argparse
import re


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
    parser.add_argument('-g, --genes', type=str, nargs='+',
                        required=True, help='foobar', dest='genes')
    # Not sure if the bottom one will even be needed
    parser.add_argument('-p, --profile_id', type=str,
                        choices=['gbm_tcga_mutations', 'gbm_tcga_gistic'],
                        help='foobar', dest='profile_id')

    args = parser.parse_args()

    # If gene argument only has one gene mentioned then execute
    # profile_id summary method to find mutation percent,
    # count number alteration and total alteration percentages
    if len(args.genes) == 1:
        # Grab Data
        mut_data = parse_genomic_data(args.genes[0], 'gbm_tcga_mutations')
        cna_data = parse_genomic_data(args.genes[0], 'gbm_tcga_gistic')
        # Get mutation and cna alteration percentages
        mut_percent, cna_percent = gene_profile_id_summarize([mut_data, cna_data])
        # Convert data into Matrix
        gene_mat = np.column_stack((mut_data[1], cna_data[1]))
        # Get total percentage
        tot_percent = genomic_alteration_summary(gene_mat)
        # Print results
        print(args.genes[0], 'is mutated in', mut_percent,'% of all cases.')
        print(args.genes[0], 'is copy number altered in', cna_percent, '% of all cases.')
        print('Total % of cases where', args.genes[0], 'is altered by either',
              ' mutation or copy number alteration:', tot_percent, '% of all cases.')
    else:
        # Init empty lists to hold multiple mutation and cna data lists
        mut_list, cna_list = [], []
        gene_list = []
        # Iterate through gene argument list and append to lists above
        for gene in args.genes:
            mut_data = parse_genomic_data(gene, 'gbm_tcga_mutations')
            cna_data = parse_genomic_data(gene, 'gbm_tcga_gistic')
            gene_list.append(mut_data[1])
            gene_list.append(cna_data[1])
            sub_gene_mat = np.column_stack((mut_data[1], cna_data[1]))
            sub_tot_percent = genomic_alteration_summary(sub_gene_mat)
            print(gene, 'is altered in', sub_tot_percent, '% of cases.')
        gene_mat = np.column_stack(tuple(gene_list))

        tot_percent = genomic_alteration_summary(gene_mat)
        print('The gene set is altered in', tot_percent, '% of all cases')




if __name__ == "__main__":
    main()
