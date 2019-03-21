import requests
import numpy as np
import argparse
import re


def parse_genomic_data(gene, genetic_profile_id):
    """
    @brief Retrieves genomic data for a particular @c genetic_profile_id
           and @c gene from the cBio Cancer Genenomics Portal database.

    @param gene (str), the gene that will be queried.
    @param genetic_profile_id (str), argument needed to decide which genetic
           profile to retrieve data from. Currently the options are to get
           mutation information or copy number alteration information.
           The arguments for those are given as 'gbm_tcga_mutations' and
           'gbm_tcga_gistic' respectively.

    @return (tag, data_list), tuple which provides a @c tag (str) which
            corresponding to the @c genetic_profile_id argument and the
            list of data where the data is in the form of strings in the list
            corresponding to either mutation values or copy number alteration
            values.
    """
    # Link to query
    url = 'http://www.cbioportal.org/webservice.do?' + \
          'cmd=getProfileData&genetic_profile_id='+genetic_profile_id + \
          '&id_type=gene_symbol&gene_list='+gene+'&case_set_id=gbm_tcga_cnaseq'
    # Send Request to Database
    req = requests.get(url)
    # Grab data from request
    data = req.text
    # Get all information after the string that shows the Gene
    data = data.split(gene.upper(), 1)[1]
    # Turn string into a list by looking for tab deliminator and commas
    data_list = data.split("\t")
    # data_list = re.split("\t|,", data)
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
    @brief Provides the summary for a particular gene profile tag of either
           mutations or copy number alterations.

           In the case of mutations:
           NaN or 0 - no mutation
           String value (e.g. V216M) - mutation

           In the case of copy number alterations:
           0 - No change
           NA - Data not available
           1 or +1 - Single copy of gene is lost or gained (not an alteration)
           -2 - both copies of the gene are deleted (alteration)
           2 - multiple copies of the gene are observed (alteration)

           The method counts the number of non NaN values to find the
           the percentage of alterations caused by mutations and it counts
           the number of values that are -2 or 2 to find the percentage of
           alterations caused by copy number alterations.

    @note  This method would only be called when the user passes
           a single gene argument.

    @param data (2-dim list of tuples), contains the data and corresponding
           tag that will be used for calculations. List must contain one
           tuple with a mutation-data tag and one with a copy-number-data tag.

    @return mutation_percent (int), cna_percent (int) The values given as a
            percent for alterations caused by mutations and
            copy number alterations.
    """
    for i in range(len(data)):
        if data[i][0] == 'mutation-data':
            # Count values corresponding to no mutation
            nan_nums = data[i][1].count('NaN') + data[i][1].count('0')
            # Subtract number of nans from number of samples to get mutations
            mut_nums = len(data[i][1]) - nan_nums
            # Calculate percentage and round to whole number
            mutation_percent = round(mut_nums/len(data[i][1]) * 100)

        elif data[i][0] == 'copy-number-data':
            # Count values corresponding to copy number alterations
            cna_nums = data[i][1].count('-2') + data[i][1].count('2')
            # Find if theres any cases with no available data
            not_available_data = data[i][1].count('NA')
            # Adjust the number of cases iff there is no available data cases
            tot = len(data[i][1]) - not_available_data
            # Calculate percentage and round to whole number
            cna_percent = round(cna_nums/tot * 100)

    return mutation_percent, cna_percent

def genomic_alteration_summary(gene_arr):
    """
    @brief Calculates the total percentage of cases where a
           particular gene is altered by either a mutation or copy
           number alteration.

           The method counts a value as an alteration as long as it shows up
           once in any combination of all the mutation and copy number
           alteration data combined across a gene or set of genes.

    @note  The method is called for single gene queries as well as
           multi gene queries.

    @param gene_arr (R by C numpy.ndarray), multi dimensional array
           which contains all relevant genetic information for all profile id
           tags. The number of rows (R) corresponds to number of samples and
           the number of columns (C) corresponds to two times the number of
           genes since each gene will carry a mutation column and
           copy number alteration column.

    @return tot_percent (int), Total percentage of cases a gene or set of
            genes is altered by either a mutation or copy number alteration.
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
    """
    Command line arguments to run this script from the
    terminal or a bash script.
    """
    parser = argparse.ArgumentParser(description='cBio Cancer Genomics Portal'+\
                                     'genomics parser and summarizer')
    parser.add_argument('-g, --genes', type=str, nargs='+',
                        required=True, help='Genes to be queried',
                        dest='genes')
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
              'mutation or copy number alteration:', tot_percent, '% of all cases.')
    else:
        # Init empty list to hold multiple mutation and cna data lists
        gene_list = []
        # Iterate through gene argument list and append to lists above
        for gene in args.genes:
            # Retrieve mutation and copy number alteration data for each gene
            mut_data = parse_genomic_data(gene, 'gbm_tcga_mutations')
            cna_data = parse_genomic_data(gene, 'gbm_tcga_gistic')
            # Send to master list
            gene_list.append(mut_data[1])
            gene_list.append(cna_data[1])
            # Calculate the individual total percentages by the single gene alone
            sub_gene_mat = np.column_stack((mut_data[1], cna_data[1]))
            sub_tot_percent = genomic_alteration_summary(sub_gene_mat)
            print(gene, 'is altered in', sub_tot_percent, '% of cases.')
        # Create r by c matrix to hold genetic data
        gene_mat = np.column_stack(tuple(gene_list))
        # Calculate total alteration percent in the gene set
        tot_percent = genomic_alteration_summary(gene_mat)
        print('The gene set is altered in', tot_percent, '% of all cases')


if __name__ == "__main__":
    main()
