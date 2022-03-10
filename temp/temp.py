import requests

from gen import *

start = time()  # Timing this program
tot = 0  # Number of products selected
prods = []  # All products
rows = headers
reason = {'"Gift" in product': 0, 'Sold out': 0, 'Tags empty': 0, 'Women product': 0, 'Repeated product': 0}
NAME = 'morelegant'  # e.g. onlyny | Has to be the same as on url (lowercase)
cats = []
# Add the the shipping and return details below
shipping = ''
print(NAME.title())
url = ['https://' + NAME + '.com/collections/', '/products.json?limit=250&page=']
print(url)
for c in cats:
    print ( url[0] )
    print ( url[1] )

    data = json.loads(bs(get(url[0] + c + url[1] + '1').content, 'html.parser').getText())[
        'products']  # For each category in given in above, get its json
    print ( data )
