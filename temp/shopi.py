from requests import get, post
from time import time
import json
from bs4 import BeautifulSoup as bs
import re
from time import time
from datetime import datetime
import csv
# from creds import col_url
from urllib.request import urlopen
from PIL import Image
import xml.etree.cElementTree as ET
from os import path
import urllib.request
# tags_exceptions = ['manscaped', 'supply', 'jackhenry', 'luminskin', 'drinkhydrant', 'magicmind', 'blackwolfnation']
# repeated_prods = ['featsocks', 'tenthousand', 'westernrise', 'manscaped']
color_options = ['color', 'colour', 'type', 'deodorant type']
size_options = ['size', 'flavor', 'scent']
class Shopify():
    def __init__(self, name, display_name, cats, shipping, note=''):
        self.note = 'Now collections add all tags if there in multiple collections'
        if note: self.note += '\n' + note
        self.name = name
        self.dname = display_name.split(' - ')[0]
        self.industry = "industry:" + display_name.split(' - ')[0]
        self.cats = cats
        self.shipping = shipping
        self.size = 'Click buy for more sizing information.'
        self.file_name = self.name + 'Inventory.csv'
        self.url = ['https://' + self.name + '.com/collections/', '/products.json?limit=250&page=']
        self.link = self.url[0].split('collections')[0]
        self.reason = {'"Gift" in product': 0, 'No images': 0, 'Tags empty': 0, 'Women product': 0, 'Repeated product': 0, 'Sold out': 0}
        self.prods = []
        p = path.dirname(path.abspath(__file__))
        self.csv_path = p + '/new/'
        self.info_path = p + '/info/'
        self.img_path = p + '/imgs/'
        self.headers  = [['Collection', 'Handle', 'Title', 'Body (HTML)', 'Vendor', 'Type', 'Tags', 'Published', 'Option1 Name', 'Option1 Value', 'Option2 Name', 'Option2 Value', 'Option3 Name', 'Option3 Value', 'Variant SKU', 'Variant Grams', 'Variant Inventory Tracker', 'Variant Inventory Policy', 'Variant Fulfillment Service', 'Variant Price', 'Variant Compare At Price', 'Variant Requires Shipping', 'Variant Taxable', 'Variant Barcode', 'Image Src', 'Image Position', 'Image Alt Text', 'Gift Card', 'SEO Title', 'SEO Description', 'Google Shopping / Google selfuct Category', 'Google Shopping / Gender', 'Google Shopping / Age Group', 'Google Shopping / MPN', 'Google Shopping / AdWords Grouping', 'Google Shopping / AdWords Labels', 'Google Shopping / Condition', 'Google Shopping / Custom Product', 'Google Shopping / Custom Label 0', 'Google Shopping / Custom Label 1', 'Google Shopping / Custom Label 2', 'Google Shopping / Custom Label 3', 'Google Shopping / Custom Label 4', 'Variant Image', 'Variant Weight Unit', 'Variant Tax Code', 'Cost per item']]
        self.rows = self.headers
        self.tot = 0