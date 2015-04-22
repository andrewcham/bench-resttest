import argparse
import collections
import math
import requests

# Argument parser logic
parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument('-c', '--categories',
                    help='alternatively print totals in expense categories',
                    action='store_true')
group.add_argument('-d', '--daily',
                    help='alternatively print daily accumulated balances',
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
    return sum([float(t['Amount']) for t in transactions])

def expenseCategories(transactions):
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
    sorted_trans = sorted(transactions, key=lambda trans: trans['Date'])
    dates = collections.OrderedDict()
    running_total = 0.0

    for trans in sorted_trans:
        running_total += float(trans['Amount'])
        date = trans['Date']
        dates[date] = running_total

    return dates

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
r = requests.get(GET_transpage_stub.format(1)).json()
total_count = r['totalCount']
total_pages = int(math.ceil(total_count / MAX_NUM_TRANS))

# Add transactions to variable
transactions = r['transactions']

# Page through API and get the rest of the transactions
for page in range(2, total_pages + 1):
    r = requests.get(GET_transpage_stub.format(page)).json()
    transactions.extend(r['transactions'])

# Return information based on flags (or lack thereof)
if args.categories: # Return list of expenses categorized
    for cat, total in expenseCategories(transactions).iteritems():
        print cat + ': ' + str(total)
if args.daily: # Return daily total transactions
    for date, total in dailyBalances(transactions).iteritems():
        print date + ': ' + str(total)
else: # Return the total transactions amount
    print 'Total Transaction Amount: ' + str(sumTransAmounts(transactions))
