import requests

from gen import *

start = time()  # Timing this program
tot = 0  # Number of products selected
prods = []  # All products
rows = headers
reason = {'"Gift" in product': 0, 'Sold out': 0, 'Tags empty': 0, 'Women product': 0, 'Repeated product': 0}
NAME = 'morelegant'  # e.g. onlyny | Has to be the same as on url (lowercase)
cats = ['floral-dresses']
# Add the the shipping and return details below
shipping = ''
print(NAME.title())
url = ['https://' + NAME + '.com/collections/', '/products.json?limit=10&page=']
print(url)
for c in cats:
     data = json.loads(bs(get(url[0] + c + url[1] + '1').content, 'html.parser').getText())[
        'products']  # For each category in given in above, get its json
     while data:
        for d in data:
            err, reason = check ( d, reason )
            if err: continue
            colors = []
            all_sizes = []
            fits = []
            waist = []
            length = []
            for option in d['options']:
                if option['name'].lower () == 'color':
                    colors = option['values']
                elif 'size' in option['name'].lower():
                    all_sizes = option['values']
                elif option['name'].lower() == 'fit':
                    fits = option['values']
                elif 'waist' in option['name'].lower():
                    waist = option['values']
                elif 'length' in option['name'].lower():
                    length = option['values']
                # else:
                #     print("Couldnt find list for option", option['name'], "with info", option['values'])
            if length == []: length = ['']
            for w in waist:
                for l in length:
                    all_sizes.append ( w + " / " + l ) if l != '' else all_sizes.append ( w )
            if len ( all_sizes ) < 2: all_sizes = ['OS']
            if len ( fits ) < 1: fits = ['']
            pos = {}
            if len ( colors ) > 2:
                for color in colors: pos[color] = []
                for v in d['variants']:
                    color = list ( filter ( lambda x: x in v['title'], colors ) )[0]
                    if v['featured_image'] == None:
                        pos[color] = [0]
                        continue
                    if v['featured_image']['position'] not in pos[color]:
                        pos[color].append ( v['featured_image']['position'] )
                pos = {k: v for k, v in sorted ( pos.items (), key=lambda item: item[1] )}
                if all ( map ( lambda x: x == [0], list ( pos.values () ) ) ):
                    for p in pos:
                        pos[p] = range ( 20 )
                lims = list ( pos.values () )
                for i in range ( len ( lims ) ):
                    try:
                        if (len ( lims[i] ) != 1): continue
                        list.sort ( lims[i + 1] )
                        lims[i] += range ( lims[i][0] + 1, lims[i + 1][0] )
                    except Exception as e:
                        for j in range ( 20 ):
                            lims[i].append ( lims[i][-1] + 1 )
                else:
                  colors = ['']

                for color in colors:
                    if color != '' and pos[color] == [0]: continue
                    for fit in fits:
                        prod = Shopify ( d, c, NAME )  # Intialize Shopify product
                        if color != '':
                            prod.title += ' - ' + color
                            prod.img_pos = []
                            prod.img_urls = []
                            for img in d['images']:
                                print(img)
                                if (img['position'] in pos[color]):
                                    prod.img_urls.append ( img['src'] )
                                    print ( prod.img_urls )
                                    prod.img_pos.append ( len ( prod.img_urls ) )

                        if fit != '': prod.title += ' - ' + fit
                        if (prod in prods):  # Check if this product has already been seen
                            reason['Repeated product'] += 1
                            continue

