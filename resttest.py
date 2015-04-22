import requests
import math
import argparse

# Argument parser logic
parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument('-c', '--categories',
                    help='alternatively print totals in expense categories',
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

################################################################################
# Main Logic
################################################################################
'''
Download and organize data.

Alternatively, we could have used a while loop across the pages until we 
stumbled across a 404 (but then we would make assumptions that empty pages
returned 404s, and we have total number of transactions available to us anyway).
'''
r = requests.get(GET_transpage_stub.format(1)).json()
total_count = r['totalCount']
total_pages = int(math.ceil(total_count / MAX_NUM_TRANS))
transactions = r['transactions']

for page in range(2, total_pages + 1):
    r = requests.get(GET_transpage_stub.format(page)).json()
    transactions.extend(r['transactions'])

# Return the total transactions amount
if args.categories: # Return list of expenses categorized
    for cat, total in expenseCategories(transactions).iteritems():
        print cat + ': ' + str(total)
else:
    print 'Total Transaction Amount: ' + str(sumTransAmounts(transactions))
