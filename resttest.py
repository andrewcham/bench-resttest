import requests
import math

################################################################################
# Helper Functions
################################################################################
def sumTransAmounts(lot):
	return sum([float(t['Amount']) for t in lot])

################################################################################
# Main Logic
################################################################################
# RESTful API info
url = 'http://resttest.bench.co/'
GET_transpage_stub = url + 'transactions/{0}.json'
MAX_NUM_TRANS = 10.0 # max number of transactions on a page

'''
Download and organize data.

Alternatively, we could have used a while loop across the pages until we 
stumbled across a 404 (but then we would make assumptions that empty pages
returned 404s, and we have total number of transactions available to us anyway).
'''
r = requests.get(GET_transpage_stub.format(1)).json()
total_balance = float(r['totalBalance'])
total_count = r['totalCount']
total_pages = int(math.ceil(total_count / MAX_NUM_TRANS))
lot = r['transactions']

for page in range(2, total_pages + 1):
	r = requests.get(GET_transpage_stub.format(page)).json()
	lot.extend(r['transactions'])

# Return 
print sumTransAmounts(lot)