
import json
import re
from requests import get, post
from bs4 import BeautifulSoup as bs

from time import time
from datetime import datetime
import csv
from urllib.request import urlopen

path = "csv/"

headers = [['Collection', 'Handle', 'Title', 'Body (HTML)', 'Vendor', 'Type', 'Tags', 'Published', 'Option1 Name',
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


class Shopify:
    def __init__(self, d='', c='', name='', display_name=''):
        url = ['https://' + name + '.com/', 'collections/products.json?limit=250&page=']
        self.collection = ''
        self.handle = ''
        self.title = ''
        self.body = ''
        self.vendor = ''
        self.type = ''
        self.tags = ''
        self.published = ''
        self.option1_name = 'Title'
        self.option1_value = 'Default Title'
        self.option2_name = 'Link'
        self.link = ''
        self.option3_name = 'Sizes'
        self.option3_value = ''
        self.sku = ''
        self.weight = ''
        self.inv_tracker = ''
        self.policy = 'deny'
        self.full_service = 'manual'
        self.price = ''
        self.cap = ''
        self.ship = ''
        self.tax = ''
        self.barcode = ''
        self.img_urls = []
        self.img_pos = []
        self.img_alt_text = ''
        self.gift_card = 'FALSE'
        self.seo_title = ''
        self.seo_desc = ''
        self.google_ship = [''] * 13
        self.var_img = ''
        self.var_weight_unit = ''
        self.variant_tax = ''
        self.cost_item = ''

        self.vendor = display_name + '-men'
        self.collection = display_name + '-men'
        self.title = d['title']
        self.handle = d['handle']
        self.type = d['product_type'].lower ()

        var = d['variants'][0]
        self.price = var['price']
        self.weight = var['grams']
        self.tax = var['taxable']
        self.ship = var['requires_shipping']
        # self.sku = var['sku']
        self.cap = var['compare_at_price']
        self.link = url[0] + 'products/' + self.handle + "?variant="

        self.img_urls = [img['src'] for img in d['images']]
        self.img_pos = [img['position'] for img in d['images']]

        self.tags = [gen_clean ( d['vendor'] ), gen_clean ( c )] + gen_clean_li ( d['tags'] )

    def get_first_row(self):
        self.tags = ', '.join ( self.tags )
        out = [self.collection, self.handle, self.title, self.body, self.vendor, self.type, self.tags, self.published,
               self.option1_name, self.option1_value, self.option2_name, self.link, self.option3_name]
        out += [self.option3_value, self.sku, self.weight, self.inv_tracker, self.policy, self.full_service, self.price,
                self.cap, self.ship, self.tax, self.barcode, self.img_urls[0], self.img_pos[0]]
        out += [self.img_alt_text, self.gift_card, self.seo_title, self.seo_desc] + self.google_ship + [self.var_img,
                                                                                                        self.var_weight_unit,
                                                                                                        self.variant_tax,
                                                                                                        self.cost_item]
        return [out]

    def get_other_rows(self):
        rows = []
        for i in range ( len ( self.img_urls[1:] ) ):
            rows.append ( [self.collection, self.handle] + ([''] * 22) + [self.img_urls[i + 1], self.img_pos[i + 1]] )
        return rows

    def get_rows(self):
        return self.get_first_row () + self.get_other_rows ()

    def write_sizes(self, all_sizes, avail_sizes):
        self.option3_value = ','.join ( all_sizes ) + '|' + ','.join ( avail_sizes )

    def __eq__(self, other):
        return self.title == other.title and self.handle == other.handle


def write_csv(file_name, rows):
    with open ( path + file_name, 'w+' ) as csvfile:
        writer = csv.writer ( csvfile )
        writer.writerows ( rows )


def clean_text(text):
    text.replace ( '\n', '.' )
    cleanr = re.compile ( '<.*?>' )
    text = re.sub ( cleanr, '', text )
    text = ' '.join ( re.sub ( "(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)", " ", text ).split () )
    text = re.sub ( '[^A-Za-z0-9]+', ' ', text )
    if 'window' in text.split (): text = ' '.join ( text.split ()[:text.split ().index ( 'window' )] )
    return text


def make_body(det, size, ship):
    out = '<sections><section id="1"><sectionTitle>Details</sectionTitle><sectionBody>' + clean_text (
        det ) + '</sectionBody></section>'
    out += '<section id="2"><sectionTitle>Size &amp; Fit</sectionTitle><sectionBody>' + size + '</sectionBody></section>'
    out += '<section id="3"><sectionTitle>Shipping &amp; Returns</sectionTitle><sectionBody>' + ship + '</sectionBody></section></sections>'
    return out


def gen_clean(text):
    text = text.split ( '-1' )[0]
    text = text.lower ().replace ( ' ', '-' )
    text = text.replace ( '/', '-' )
    text = text.replace ( "'", '' )
    return text


def gen_clean_li(li):
    return list ( map ( gen_clean, li ) )


def check(d, reason):
    out = 'gift' in d['title'].lower () or 'gift' in d['handle'].lower () or 'gift' in d['product_type']
    if out: reason['"Gift" in product'] += 1
    out1 = False
    # out1 = not any([v['available'] for v in d['variants']])
    # if out1: reason['Sold out'] += 1
    out2 = 'women' in d['tags'] or 'womens' in d['tags'] or 'women' in d['handle'] or 'women' in d[
        'product_type'] or 'women' in d['title']
    if out2: reason['Women product'] += 1
    out3 = d['tags'] == []
    if out3: reason['Tags empty'] += 1
    return (out or out1 or out2 or out3), reason


def proc_size(size):
    size = size.upper ().replace ( '-', '' )
    if 'O/S' in size or 'OS' in size or ('O' in size and 'S' in size):
        return 'OS'
    elif 'XS' in size or 'XSMALL' in size:
        return 'XS'
    elif 'S' in size or 'SMALL' in size:
        return 'S'
    elif 'M' in size or 'MEDIUM' in size:
        return 'M'
    elif 'L' in size or 'LARGE' in size:
        return 'L'
    elif 'XL' in size or 'XLARGE' in size:
        return 'XL'
    elif 'XXL' in size or 'XXLARGE' in size:
        return 'XXL'
    elif 'XXXL' in size or 'XXXLARGE' in size:
        return 'XXXL'
    else:
        # print("Size not found for", size)
        return size


def proc_size_li(li):
    return list ( set ( map ( proc_size, li ) ) )


def write_file(name, tot, time, reason, note=''):
    with open ( "info/" + name + '.txt', "a+" ) as f:
        f.writelines (
            [str ( datetime.now ().strftime ( "%d/%m/%Y %H:%M:%S" ) ) + '\n', note + '\n', tot + '\n', time + '\n',
             str ( reason ) + '\n', '\n\n'] )


def fancy(text):
    return text.replace ( '-', ' ' ).title ()


def post_collections(file_name, name, cats):
    if not cats or cats == ['']:
        image = finder ( file_name, None )
        data = {"smart_collection": {"title": name + '-men:All', "rules": [
            {"column": "vendor", "relation": "contains", "condition": name + "-men"}], "image": {"src": image}}}
        a = post ( data=json.dumps ( data ), headers={'Content-Type': 'application/json'} )
        print ( a.content )
        return

    for c in cats:
        image = finder ( file_name, gen_clean ( c ) )
        print ( image )
        if not image: continue
        data = {"smart_collection": {"title": name + '-men:' + fancy ( c ),
                                     "rules": [{"column": "vendor", "relation": "contains", "condition": name + "-men"},
                                               {"column": "tag", "relation": "equals", "condition": gen_clean ( c )}],
                                     "disjunctive": False, "image": {"src": image, "alt": gen_clean ( c )}}}
        a = post ( data=json.dumps ( data ), headers={'Content-Type': 'application/json'} )
        print ( a.content )


def finder(name, find):
    url = None
    with open ( 'csv/' + name.title () + "Inventory.csv", "r" ) as f:
        reader = csv.reader ( f )
        for r in reader:
            if r[6] == '' or r[6] == 'Tags': continue
            if find and find != r[6].split ( ',' )[1].strip (): continue
            if ".jpg" in r[24]:
                url = r[24].split ( '.jpg' )[0] + '_350x350.jpg' + r[24].split ( '.jpg' )[1]
                return url
            elif '.png' in r[24]:
                url = r[24].split ( '.png' )[0] + '_350x350.png' + r[24].split ( '.png' )[1]
                return url
