import re
import json


class Product:
    def __init__(self, d='', c='', name='', display_name='', url='', industry=''):
        self.industry = industry
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
        self.option3_name = ''
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

        if d:
            self.vendor = display_name + '-men'
            # self.collection = display_name+'-men'
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
            self.link = url + 'products/' + self.handle

            self.img_urls = [img['src'] for img in d['images']]
            self.img_pos = [img['position'] for img in d['images']]

            self.tags = [self.industry, gen_clean ( d['vendor'] ), gen_clean ( c )] + gen_clean_li ( d['tags'] )

    def get_first_row(self):
        tags = ', '.join ( self.tags )
        out = [self.collection, self.handle, self.title, self.body, self.vendor, self.type, tags, self.published,
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
        return (self.get_first_row () + self.get_other_rows ())

    def __eq__(self, other):
        return (self.title == other.title and self.handle == other.handle)

    def make_product(self, li):
        main = li[0]
        self.collection, self.handle, self.title, self.body, self.vendor, self.type, tags, self.published, self.option1_name, self.option1_value, self.option2_name, self.link, self.option3_name, self.option3_value, self.sku, self.weight, self.inv_tracker, self.policy, self.full_service, self.price, self.cap, self.ship, self.tax, self.barcode = main[
                                                                                                                                                                                                                                                                                                                                                          :24]
        self.tags = tags.split ( ',' )
        self.handle = gen_clean ( self.handle )
        self.img_urls = [a[24] for a in li]
        self.img_pos = [a[25] for a in li]
        self.img_alt_text = main[26]
        self.gift_card = main[27]
        self.seo_title = main[28]
        self.seo_desc = main[29]
        self.google_ship = main[30:43]
        self.var_img = main[43]
        self.var_weight_unit = main[44]
        self.variant_tax = main[45]
        self.cost_item = main[46]

    def get_json(self, prod_id=None):
        prod = {'product': {}}
        if prod_id:
            prod['product'] = {"id": prod_id, "title": self.title, "body_html": self.body, "vendor": self.vendor,
                               "product_type": self.type, "tags": self.tags, "handle": self.handle}
        else:
            prod['product'] = {"title": self.title, "body_html": self.body, "vendor": self.vendor,
                               "product_type": self.type, "tags": self.tags, "handle": self.handle}
        prod['product']['options'] = [{"name": self.option1_name, "position": 1, "value": self.option1_value}]
        prod['product']['options'] += [{"name": self.option2_name, "position": 2, "value": self.link}]
        # prod['product']['options'] += [{"name":self.option3_name, "position":3, "value":self.option3_value}]
        prod['product']['variants'] = [
            {"barcode": None, "compare_at_price": self.cap, "grams": self.weight, "option1": self.option1_value,
             "option2": self.link, "option3": self.option3_value, "inventory_management": None}]
        prod['product']['variants'][0].update (
            {"price": self.price, "sku": None, "taxable": self.tax, "fulfillment_service": self.full_service,
             "inventory_policy": self.policy, "position": 1, "requires_shipping": self.ship} )
        prod['product']['images'] = []
        for img in self.img_urls: prod['product']['images'] += [{"src": img}]
        return prod


def gen_clean(text):
    text = text.split ( '-1' )[0]
    text = re.sub ( '[^A-Za-z0-9]+', ' ', text )
    text = text.lower ().replace ( ' ', '-' )
    text = text.replace ( '/', '-' )
    text = text.replace ( "'", '' )
    return text


def gen_clean_li(li):
    return list ( map ( gen_clean, li ) )
