# Genomics Data Parser and Summarizer

The following includes a command line tool to call a python script to parse genomic data from the [cBio Cancer Genomics Portal](https://www.cbioportal.org/) and summarize information about the mutations and gene alterations in the a set of cases

## Installation

Clone the folder in my `personal-code-mac` repo

```
git clone https://github.com/sonamghosh/personal-code-mac/tree/master/Gene-Parser
```

## Usage

```python
import foobar

foobar.pluralize('word') # returns 'words'
foobar.pluralize('goose') # returns 'geese'
foobar.singularize('phenomena') # returns 'phenomenon'
```

There are two ways of utilizing the code in this repo either by
using the bash script with command line arguments or directly
calling the python script with command line arguments.

The user can either execute the program with a single gene query to obtain
a summary on the percentage of alterations caused by mutations and copy number alterations as well as a total percentage caused by mutations or copy number alterations:

```bash
# Single gene call with bash
./gbm_summarize.sh TP53
# Single gene call with python
python3 gbm_summarize.py -g TP53
```

Output:

```
TP53 is mutated in 29 % of all cases.

TP53 is copy number altered in 2 % of all cases.
Total % of cases where TP53 is altered by either mutation or copy number alteration: 30 % of all cases.
```

The user can also execute the program with a multi gene query to obtain
a total percentage of cases altered for each individual gene along with
the entire gene set.

```bash
# Multi gene call with bash
./gbm_summarize.sh TP53 MDM2 MDM4
# Multi gene call with python
python3 gbm_summarize.py -g TP53 MDM2 MDM4
```

Output:

```
TP53 is altered in 30 % of cases.
MDM2 is altered in 10 % of cases.

MDM4 is altered in 10 % of cases.
The gene set is altered in 48 % of all cases
```

## Requirements
Should have Python 3.X installed with NumPy.

Potential Issue:

When running `.gbm_summarize.sh` from the terminal, if the terminal
gives a `Permission denied` message. Run the following command on terminal:

```bash
sudo chmod 755 gbm_summarize.sh
```

After running the command, you should be able to run the script normally.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
