import argparse
import collections
import math
import requests
import sys

# Argument parser logic
parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument('-c', '--categories',
                    help='alternatively print totals in expense categories',
                    action='store_true')
group.add_argument('-d', '--daily',
                    help='alternatively print daily accumulated balances',
                    action='store_true')
group.add_argument('-dup', '--duplicate',
                    help='alternatively print all duplicate transactions',
                    action='store_true')
args = parser.parse_args()

# RESTful API info
url = 'http://resttest.bench.co/'
GET_transpage_stub = url + 'transactions/{0}.json'
MAX_NUM_TRANS = 10.0 # max number of transactions on a page

################################################################################
# Helper Functions
################################################################################
def sumTransAmounts(transactions):
    '''
    Returns the total amount from list of transactions

    Params:
        transactions - list of transactions 

    Returns:
        A float representing the total amount from all transactions
    '''
    return sum([float(t['Amount']) for t in transactions])

def expenseCategories(transactions):
    '''
    Calculates total expenses in categories

    Params:
        transactions - list of transactions

    Returns:
        A dictionary with expense categories as keys and expense totals as
        values
    '''
    categories = dict()

    for trans in transactions:
        ledger = trans['Ledger']
        if ledger not in categories:
            categories[ledger] = 0
        categories[ledger] += float(trans['Amount'])

    # Label the blank expenses 'Deposits' (that's what they seem to be)
    if '' in categories:
        categories['Deposits'] = categories.pop('')

    return categories

def dailyBalances(transactions):
    '''
    Calculates accumulative daily balances 

    Params:
        transactions - list of transactions 

    Returns:
        An ordered dictionary (by ascending date) with dates as keys and
        accumulated amount totals as values
    '''
    sorted_trans = sorted(transactions, key=lambda trans: trans['Date'])
    dates = collections.OrderedDict()
    running_total = 0.0

    for trans in sorted_trans:
        running_total += float(trans['Amount'])
        date = trans['Date']
        dates[date] = running_total

    return dates

def findDuplicates(items):
    '''
    Finds duplicates in any arbitrary list

    Params:
        items - list of items

    Returns:
        A list with duplicate items
    '''
    seen = []
    dups = []

    for item in items:
        if item in seen:
            dups.append(item)
        else:
            seen.append(item) 

    return dups

def printDict(dict):
    '''
    Prints input dictionary to console

    Params:
        dict - dictionary to print
    '''
    for key, value in dict.iteritems():
        print key + ': ' + value

################################################################################
# Main Logic
################################################################################
'''
Download and organize data.

Alternatively, we could have used a while loop across the pages until we 
stumbled across a 404 (but then we would make assumptions that empty pages
returned 404s, and we have total number of transactions available to us anyway).
'''
# Get the first page and figure out how many pages there are
r = requests.get(GET_transpage_stub.format(1))
if r.status_code != 200:
    sys.exit('There are no transactions!')
r = r.json()
total_count = r['totalCount']
total_pages = int(math.ceil(total_count / MAX_NUM_TRANS))

# Add transactions to variable
transactions = r['transactions']

# Page through API and get the rest of the transactions
if total_pages > 1:
    for page in range(2, total_pages + 1):
        r = requests.get(GET_transpage_stub.format(page)).json()
        transactions.extend(r['transactions'])

# Return information based on flags (or lack thereof)
if args.categories: # Return list of expenses categorized
    for cat, total in expenseCategories(transactions).iteritems():
        print cat + ': ' + str(total)
elif args.daily: # Return daily total transactions
    for date, total in dailyBalances(transactions).iteritems():
        print date + ': ' + str(total)
elif args.duplicate: # Return duplicate transactions
    for trans in findDuplicates(transactions):
       printDict(trans)
else: # Return the total transactions Amount
    print 'Total Transaction Amount: ' + str(sumTransAmounts(transactions))
