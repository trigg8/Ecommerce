from store.models import Product
from decimal import Decimal


class Cart():
    '''
    A base Cart class, providing some default behaviors that can inherited or overrided, as necessary.
    '''
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('skey')
        if 'skey' not in request.session:
            cart = self.session['skey'] = {}
        self.cart = cart


    def add(self, product, qty):
        '''
        Adding and updating the users cart session data
        '''
        product_id = str(product.id)

        if product_id in self.cart:
            self.cart[product_id]['qty'] = qty
        else:
            self.cart[product_id] = {'price': str(product.price), 'qty': qty}

        self.save()


    def __iter__(self):
        '''
        Collect the product_id in the session data to query the database and return products
        '''
        product_ids = self.cart.keys()
        products = Product.products.filter(id__in=product_ids)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['qty']
            yield item



    def __len__(self):
        '''
        Get the cart data and count the qty of items
        '''
        return sum(item['qty'] for item in self.cart.values())


    def get_total_price(self):
        return sum(Decimal(item['price']) * item['qty'] for item in self.cart.values())


    def delete(self, product):
        '''
        Delete item from session data
        '''
        product_id = str(product)

        if product_id in self.cart:
            del self.cart[product_id]
        
        self.save()

    
    def update(self, product, qty):
        '''
        Update values in session data
        '''
        product_id = str(product)

        if product_id in self.cart:
            self.cart[product_id]['qty'] = qty
        
        self.save()

    def save(self):
        self.session.modified = True
        
