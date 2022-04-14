


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