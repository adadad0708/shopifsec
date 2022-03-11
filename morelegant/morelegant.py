from shop import Shopify

WEB_NAME = 'morelegant' # Website name
DISPLAY_NAME = 'morelegant - Apparel'
cats =  ['floral-dresses']
cat_names = ['Shorts', 'Tees', 'Sweatshirts and Hoodies', 'Pants']
imgs = ['https://drive.google.com/uc?export=download&id=14000S734V8XrNDZ3azL1Q0xr3DmPIsOQ', 'https://drive.google.com/uc?export=download&id=1eL8DlZBZIKtke9-XWLAjy9--WEJj3HwS', 'https://drive.google.com/uc?export=download&id=1y-iCS8arkRrGH1kyDGD5UsOdwDwdQ6t8', 'https://drive.google.com/uc?export=download&id=1Rk511ctndOX6QRRYhQd83RiV3P0MGuKt', 'https://drive.google.com/uc?export=download&id=1L-lI9l7G0R5m4RaPQV8RdMlnNqCLo4Cw']
shipping = 'For any exchanges or returns we offer a 30 day return policy on unopened and unworn products. Only regular priced items may be refunded, unfortunately sale items cannot be refunded.'
note = 'New brand'

brand = Shopify(WEB_NAME, DISPLAY_NAME, cats, shipping, note)
brand.run()
brand.write_csv()
brand.write_info()
# brand.post_collections(cat_names, imgs)
