from requests import get, post
from produ import Product
from time import time
import json
from bs4 import BeautifulSoup as bs
import re
from time import time
from datetime import datetime
import csv
from creds import col_url
from urllib.request import urlopen
from PIL import Image
import xml.etree.cElementTree as ET
from os import path
import urllib.request

sizes_debug = False
options_debug = False
tags_exceptions = ['manscaped', 'supply', 'jackhenry', 'luminskin', 'drinkhydrant', 'magicmind', 'blackwolfnation']
repeated_prods = ['featsocks', 'tenthousand', 'westernrise', 'manscaped']
color_options = ['color', 'colour', 'type', 'deodorant type']
size_options = ['size', 'flavor', 'scent']


class Shopify ():
    def __init__(self, name, display_name, cats, shipping, note=''):
        self.note = 'Now collections add all tags if there in multiple collections'
        if note: self.note += '\n' + note
        self.name = name
        self.dname = display_name.split ( ' - ' )[0]
        self.industry = "industry:" + display_name.split ( ' - ' )[1]
        self.cats = cats
        self.shipping = shipping
        self.size = 'Click buy for more sizing information.'
        self.file_name = self.name + 'Inventory.csv'
        self.url = ['https://' + self.name + '.com/collections/', '/products.json?limit=250&page=']
        self.link = self.url[0].split ( 'collections' )[0]
        self.reason = {'"Gift" in product': 0, 'No images': 0, 'Tags empty': 0, 'Women product': 0,
                       'Repeated product': 0, 'Sold out': 0}
        self.prods = []
        p = path.dirname ( path.abspath ( __file__ ) )
        self.csv_path = p + '/new/'
        self.info_path = p + '/info/'
        self.img_path = p + '/imgs/'
        self.headers = [
            ['Collection', 'Handle', 'Title', 'Body (HTML)', 'Vendor', 'Type', 'Tags', 'Published', 'Option1 Name',
             'Option1 Value', 'Option2 Name', 'Option2 Value', 'Option3 Name', 'Option3 Value', 'Variant SKU',
             'Variant Grams', 'Variant Inventory Tracker', 'Variant Inventory Policy', 'Variant Fulfillment Service',
             'Variant Price', 'Variant Compare At Price', 'Variant Requires Shipping', 'Variant Taxable',
             'Variant Barcode', 'Image Src', 'Image Position', 'Image Alt Text', 'Gift Card', 'SEO Title',
             'SEO Description', 'Google Shopping / Google selfuct Category', 'Google Shopping / Gender',
             'Google Shopping / Age Group', 'Google Shopping / MPN', 'Google Shopping / AdWords Grouping',
             'Google Shopping / AdWords Labels', 'Google Shopping / Condition', 'Google Shopping / Custom Product',
             'Google Shopping / Custom Label 0', 'Google Shopping / Custom Label 1', 'Google Shopping / Custom Label 2',
             'Google Shopping / Custom Label 3', 'Google Shopping / Custom Label 4', 'Variant Image',
             'Variant Weight Unit', 'Variant Tax Code', 'Cost per item']]
        self.rows = self.headers
        self.tot = 0

    def run(self):
        self.start = time ()
        old_tot = 0
        for c in self.cats:
            if c[-2:] == '-P':
                furl = [self.url[0].replace ( 'collections', 'products' ), self.url[1]]
                self.c = c[:-2]
                furl = furl[0] + self.c + furl[1] + '1'
                self.data = [json.loads ( bs ( get ( furl ).content, 'html.parser' ).getText () )['product']]
            else:
                furl = self.url
                self.c = c
                furl = furl[0] + self.c + furl[1] + '1'
                if sizes_debug:
                    print ( furl )
                self.data = json.loads ( bs ( get ( furl ).content, 'html.parser' ).getText () )['products']
            ind = 1
            while self.data:
                for d in self.data:
                    self.d = d
                    err, self.reason = self.check ()
                    if err:
                        continue
                    self.get_color_fit ()

                    for color in self.colors:
                        if color != '' and self.pos[color] == [0]:
                            continue
                        self.prod = Product ( self.d, self.c, self.name, self.dname, self.link, self.industry )

                        if color != '': self.add_color ( color )

                        if self.check_error (): continue
                        if not self.process_sizes ( color ): continue

                        if not d['body_html']:
                            details = ''
                        else:
                            details = clean_text ( d['body_html'] )
                        self.make_body ( details, self.size, self.shipping )

                        self.prods.append ( self.prod )
                        self.tot += 1
                ind += 1
                try:
                    self.data = json.loads (
                        bs ( get ( furl[0] + self.c + furl[1] + str ( ind ) ).content, 'html.parser' ).getText () )[
                        'products']
                except:
                    self.data = []
            if ind == 1:
                print ( "No products in category " + self.c )
            elif old_tot == self.tot:
                print ( "No new products added in category", self.c )
            old_tot = self.tot
        for p in self.prods: self.rows += p.get_rows ()
        print ( "Total products: " + str ( self.tot ) + "/" + str (
            sum ( list ( self.reason.values () ) ) + self.tot ) + "\nTotal Time: " + str (
            round ( time () - self.start, 2 ) ) + 's' )
        if sum ( list ( self.reason.values () ) ) != 0: print ( str ( self.reason ) )

    def get_color_fit(self):
        self.all_sizes = []
        self.colors = []
        self.fits = []
        waist = []
        length = []
        inseam = []
        title = []
        for option in self.d['options']:
            if option['name'].lower () in color_options:
                self.colors = option['values']
            elif option['name'].lower () in size_options:
                if not self.all_sizes:
                    self.all_sizes = option['values']
                else:
                    print ( 'CHECK SIZE FOR THIS PRODUCT NOW!' )
            elif (option['name'].lower () == 'fit' or option['name'] == "Style"):
                self.fits = option['values']
            elif ('waist' in option['name'].lower ()):
                waist = option['values']
                self.all_sizes = []
            elif ('length' in option['name'].lower ()):
                length = option['values']
            elif ('Inseam' == option['name']):
                inseam = option['values']
            elif ('Title' == option['name']):
                if ('title' not in option['values'][0].lower ()):
                    title = option['values']
            else:
                if options_debug: print ( "Couldnt find list for option", option['name'], "with info",
                                          option['values'] )
        if inseam and length:
            if options_debug: print ( "Inseam and Length, both have values :(" )
            if options_debug: print ( "Inseam:", inseam, "Length:", length )
        if not length and not inseam: length = ['']
        if (length or inseam) and not waist and self.all_sizes: waist, self.all_sizes = self.all_sizes, []
        if not self.all_sizes and title:
            if sizes_debug: print ( 'Title with value', title, 'was replaced with sizes' )
            self.all_sizes = title
        for w in waist:
            for l in length:
                self.all_sizes.append ( w + " / " + l ) if l != '' else self.all_sizes.append ( w )
            for i in inseam:
                self.all_sizes.append ( w + " / " + i + ' (Inseam)' )
        if self.all_sizes == []: self.all_sizes = ['OS']
        if ' / ' not in self.all_sizes[0]: self.all_sizes = [x.upper () for x in self.all_sizes]
        if len ( self.fits ) < 2: self.fits = ['']
        if not self.colors:
            self.colors = ['']
        else:
            self.pos = {}
            for color in self.colors: self.pos[color] = []
            for v in self.d['variants']:
                try:
                    color = list ( filter ( lambda x: x in v['title'], self.colors ) )[0]
                except:
                    continue
                if v.get ( 'featured_image', None ) == None:
                    self.pos[color] = [0]
                    continue
                if v['featured_image']['position'] not in self.pos[color]:
                    self.pos[color].append ( v['featured_image']['position'] )
            self.pos = {k: v for k, v in sorted ( self.pos.items (), key=lambda item: item[1] )}
            if all ( map ( lambda x: x == [0], list ( self.pos.values () ) ) ):
                for p in self.pos:
                    self.pos[p] = range ( 20 )
            lims = list ( self.pos.values () )
            for i in range ( len ( lims ) ):
                try:
                    if (len ( lims[i] ) != 1): continue
                    list.sort ( lims[i + 1] )
                    lims[i] += range ( lims[i][0] + 1, lims[i + 1][0] )
                except:
                    for _ in range ( 5 ):
                        lims[i].append ( lims[i][-1] + 1 )
            # if self.name == 'johnnie-o':
            #     self.pos[''] = []
            #     for i in self.d['images']:
            #         print(i)
            #         self.pos[i.get('alt', '')].append(i['position'])

    def add_color(self, color):
        if (color not in self.prod.title and color.upper () not in self.prod.title):
            self.prod.title += ' - ' + color
        self.prod.handle += '-' + gen_clean ( color )
        self.prod.img_pos = []
        self.prod.img_urls = []
        for img in self.d['images']:
            if (img['position'] in self.pos[color]):
                self.prod.img_urls.append ( img['src'] )
                self.prod.img_pos.append ( len ( self.prod.img_urls ) )

    def process_sizes(self, color):
        self.avail_sizes = {}
        done = False
        self.variants = []
        for v in self.d['variants']:
            for fit in self.fits:
                if color in v['title'] and fit in v['title']:
                    if (color or fit) and not done: self.prod.link += "?variant=" + str ( v["id"] ); done = True
                    if sizes_debug: print ( self.all_sizes, v['title'].upper ().split ( ' / ' ) )
                    if self.all_sizes == ['OS']:
                        size = 'OS'
                    else:
                        size = list ( filter ( lambda x: all (
                            map ( lambda a: a.strip ().upper () in v['title'].upper ().split ( ' / ' ),
                                  x.replace ( '(Inseam)', '' ).split ( ' / ' ) ) ), self.all_sizes ) )
                    if sizes_debug: print ( size )
                    if not size: continue
                    if size != 'OS': size = size[-1]
                    if size not in self.avail_sizes:
                        if fit:
                            self.avail_sizes[size + ' - ' + fit] = [v.get ( 'available', False ), v['id']]
                        else:
                            try:
                                self.avail_sizes[size] = [v['available'], v['id']]
                            except:
                                self.avail_sizes[size] = [True, v['id']]
        if not any ( list ( map ( lambda x: x[0], list ( self.avail_sizes.values () ) ) ) ):
            self.reason['Sold out'] += 1
            return False
        # proc_avail_sizes = self.proc_size_li(avail_sizes)
        if sizes_debug: print ( self.prod.title, self.avail_sizes, '\n' )
        return True

    def write_sizes(self, sizes, varaints):
        self.prod.body += "<fdsd>" + ','.join ( variants ) + "</fdsf><ff>" + ','.join ( sizes ) + "</ff>"

    def proc_size(self, inp):
        size = inp.upper ().replace ( '-', '' )
        if inp.strip ()[-1] == ')':
            size = inp.split ( '(' )[0]  # To handle (inseam) in size
        if self.name == 'twillory' and len ( inp.split ( ' / ' ) ) > 2:
            inp = inp.split ( ' / ' )[0] + ' / ' + inp.split ( ' / ' )[-1]
        if 'O/S' in size or 'OS' in size or 'ONE SIZE' == size:
            return 'OS'
        elif 'XS' == size or 'XSMALL' == size:
            return 'XS'
        elif 'S' == size or 'SMALL' == size:
            return 'S'
        elif 'M' == size or 'MEDIUM' == size:
            return 'M'
        elif 'XXXL' == size or 'XXXLARGE' == size:
            return 'XXXL'
        elif 'XXL' == size or 'XXLARGE' == size or 'DOUBLE EXTRA LARGE' == size:
            return 'XXL'
        elif 'XL' == size or 'XLARGE' == size or 'EXTRA LARGE' == size:
            return 'XL'
        elif 'L' == size or 'LARGE' == size:
            return 'L'
        else:
            # print("Size not found for", size)
            return inp

    def make_body(self, det, size, ship):
        root = ET.Element ( "sections" )
        sec1 = ET.SubElement ( root, "section", id="1" )
        ET.SubElement ( sec1, "sectionTitle" ).text = "Details"
        ET.SubElement ( sec1, "sectionBody" ).text = clean_text ( det )
        sec2 = ET.SubElement ( root, "section", id="2" )
        ET.SubElement ( sec2, "sectionTitle" ).text = "Size &amp; Fit"
        ET.SubElement ( sec2, "sectionBody" ).text = size
        sec3 = ET.SubElement ( root, "section", id="3" )
        ET.SubElement ( sec3, "sectionTitle" ).text = "Shipping &amp; Returns"
        ET.SubElement ( sec3, "sectionBody" ).text = ship
        sizes = ET.SubElement ( root, "sizes" )
        for s, data in self.avail_sizes.items ():
            size = ET.SubElement ( sizes, "size", instock=str ( data[0] ).lower () )
            ET.SubElement ( size, "string" ).text = str ( s )
            ET.SubElement ( size, "variant" ).text = str ( data[1] )
        # print(ET.tostring(root).decode("utf-8"))
        self.prod.body = ET.tostring ( root ).decode ( "utf-8" )

    def proc_size_li(self, li):
        result = []
        re = list ( map ( self.proc_size, li ) )
        [result.append ( x ) for x in re if x not in result]
        return result

    def check(self):
        out = 'gift' in self.d['title'].lower () or 'gift' in self.d['handle'].lower () or 'gift' in self.d[
            'product_type'] or 'cart-on' in self.d['title'] or float ( self.d['variants'][0]['price'] ) == 0.0
        if out: self.reason['"Gift" in product'] += 1
        out1 = False
        # out1 = not any([v['available'] for v in d['variants']])
        # if out1: reason['Sold out'] += 1
        out2 = any ( map ( lambda x: ('women' in x) and 'men' not in x, self.d['tags'] ) ) or 'women' in self.d[
            'handle'] or 'women' in self.d['product_type'] or 'women' in self.d['title'] or 'gender womens' in self.d[
                   'tags']
        if out2: self.reason['Women product'] += 1
        out3 = self.d['tags'] == []
        if self.name in tags_exceptions: out3 = False
        if out3: self.reason['Tags empty'] += 1
        return (out or out1 or out2 or out3), self.reason

    def write_info(self):
        tot = "Total products: " + str ( self.tot ) + "/" + str ( sum ( list ( self.reason.values () ) ) + self.tot )
        time_info = "Total Time: " + str ( round ( time () - self.start, 2 ) ) + 's'
        with open ( self.info_path + self.name + '.txt', "a+" ) as f:
            f.writelines (
                [str ( datetime.now ().strftime ( "%d/%m/%Y %H:%M:%S" ) ) + '\n', self.note + '\n', tot + '\n',
                 time_info + '\n', str ( self.reason ) + '\n', '\n\n'] )

    def write_csv(self):
        with open ( self.csv_path + self.file_name, 'w+' ) as csvfile:
            writer = csv.writer ( csvfile )
            writer.writerows ( self.rows )

    def post_collections(self, names, imgs=[]):
        data = {"smart_collection": {"title": self.dname + '-men:All', "rules": [
            {"column": "vendor", "relation": "contains", "condition": self.dname + "-men"}], "body_html": "1"}}
        if imgs: data["smart_collection"]["image"] = {"src": imgs[0], "width": 200, "height": 200}
        a = post ( col_url, data=json.dumps ( data ), headers={'Content-Type': 'application/json'} )
        # print(a.content)
        if self.cats == ['']: return
        for i, n in enumerate ( names ):
            c = self.cats[i]
            if c[-2:] == '-P': c = c[:-2]
            c = gen_clean ( c )
            image = self.img_finder ( c )
            if not image:
                print ( "No images for", c )
                continue
            data = {"smart_collection": {"title": self.dname + '-men:' + n, "rules": [
                {"column": "vendor", "relation": "contains", "condition": self.dname + "-men"},
                {"column": "tag", "relation": "equals", "condition": c}], "disjunctive": False,
                                         "body_html": str ( i + 2 )}}
            if imgs: data["smart_collection"]["image"] = {"src": imgs[i + 1], "width": 200, "height": 200}
            a = post ( col_url, data=json.dumps ( data ), headers={'Content-Type': 'application/json'} )
            # print(a.content)
        print ( "All collections posted" )

    def img_finder(self, find):
        url = None
        with open ( self.csv_path + self.file_name, "r" ) as f:
            reader = csv.reader ( f )
            for r in reader:
                if r[6] == '' or r[6] == 'Tags': continue
                if find and find not in r[6].split ( ', ' ): continue
                if ('.jpg' in r[24]):
                    url = r[24].split ( '.jpg' )[0] + '_350x350.jpg' + r[24].split ( '.jpg' )[1]
                    return url
                elif ('.png' in r[24]):
                    url = r[24].split ( '.png' )[0] + '_350x350.png' + r[24].split ( '.png' )[1]
                    return url

    def check_error(self):
        if (self.prod in self.prods):
            self.prods[self.prods.index ( self.prod )].tags.append ( gen_clean ( self.c ) )
            self.reason['Repeated product'] += 1
            return True
        if (self.name in repeated_prods and [a for a in self.prods if a.title == self.prod.title]):
            self.reason['Repeated product'] += 1
            return True
        if not self.prod.img_urls:
            self.reason["No images"] += 1
            return True

    def fancy(self, text):
        return text.replace ( '-', ' ' ).title ()


def clean_text(text):
    text.replace ( '\n', '.' )
    cleanr = re.compile ( '<.*?>' )
    text = re.sub ( cleanr, '', text )
    text = ' '.join ( re.sub ( "(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)", " ", text ).split () )
    text = re.sub ( '[^A-Za-z0-9]+', ' ', text )
    if 'window' in text.split (): text = ' '.join ( text.split ()[:text.split ().index ( 'window' )] )
    return text


def gen_clean(text):
    text = text.split ( '-1' )[0]
    text = re.sub ( '[^A-Za-z0-9]+', ' ', text )
    text = text.lower ().replace ( ' ', '-' )
    text = text.replace ( '/', '-' )
    text = text.replace ( "'", '' )
    return text


def gen_clean_li(li):
    return list ( map ( gen_clean, li ) )