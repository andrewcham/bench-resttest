import argparse
import collections
import re
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
group.add_argument('-l', '--list',
                    help='alternatively print out all transaction details ' +
                         '(with garbage removed)',
                    action='store_true')
args = parser.parse_args()

# RESTful API info
url = 'http://resttest.bench.co/'
GET_transpage_stub = url + 'transactions/{0}.json'

################################################################################
# Helper Functions
################################################################################
def sumTransAmounts(transactions):
    '''
    Returns the total amount from list of transactions.

    Params:
        transactions - list of transactions 

    Returns:
        A float representing the total amount from all transactions
    '''
    return sum([float(t['Amount']) for t in transactions])

def expenseCategories(transactions):
    '''
    Calculates total expenses in categories.

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
    Calculates accumulative daily balances.

    Params:
        transactions - list of transactions 

    Returns:
        An ordered dictionary (by ascending date) with dates as keys and
        accumulated amount totals as values
    '''
    sorted_trans = sorted(transactions, key=lambda t: t['Date'])
    dates = collections.OrderedDict()
    running_total = 0.0

    for trans in sorted_trans:
        running_total += float(trans['Amount'])
        date = trans['Date']
        dates[date] = running_total

    return dates

def removeGarbage(transactions):
    '''
    (Attempts to) Remove garbage text from transaction vendor names.

    Params:
        transactions - list of transactions 
    '''
    garbage = re.compile(r'\w*[#@\d]\w*|\b(USD)\b|')
    for trans in transactions:
        trans['Company'] = garbage.sub('', trans['Company'])

def findDuplicates(items):
    '''
    Finds duplicates in any arbitrary list.

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
    Prints input dictionary to console.

    Params:
        dict - dictionary to print
    '''
    for key, value in dict.iteritems():
        print key + ': ' + value

def GETcheck404(url, err):
    '''
    Checks for a 404 response in a GET response, returns the response if it
    doesn't have one.

    Params:
        url - the url which is requested
        err - the error thrown on exit

    Returns:
        A valid response
    '''
    res = requests.get(url)
    if res.status_code == 404:
        sys.exit(err)

    return res

################################################################################
# Main Logic
################################################################################
# Download and organize data
page = 1
res = GETcheck404(GET_transpage_stub.format(page),
                  'There are no transactions!').json()
total_count = res['totalCount']
transactions = res['transactions']

# Page through API and get the rest of the transactions
while len(transactions) != total_count:
    page += 1
    res = GETcheck404(GET_transpage_stub.format(page),
                      'There is an invalid page lurking between pages.').json()
    transactions.extend(res['transactions'])

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
elif args.list: # Returns list of transaction details
    removeGarbage(transactions)
    for trans in sorted(transactions, key=lambda t: t['Date'], reverse=True):
        printDict(trans)
else: # Return the total transactions Amount
    print 'Total Transaction Amount: ' + str(sumTransAmounts(transactions))
