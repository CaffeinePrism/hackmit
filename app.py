import json
import tornado.ioloop
import tornado.httpclient
import tornado.web
import urllib

try:
    import config
except ImportError:
    import example_config as config

def getAddressFromGeo(lat, lng):
    http = tornado.httpclient.HTTPClient()
    url = 'http://maps.googleapis.com/maps/api/geocode/json'
    try:
        response = http.fetch('%s?latlng=%s,%s&sensor=false' % 
                                (url, lat, lng))
        data = json.loads(response.body.decode())
    except tornado.httpclient.HTTPError as e:
        return 'Error: %s' % e
    except Exception as e:
        return 'Error: %s' % e
    http.close()
    if data['status'] == 'ZERO_RESULTS':
        return 'No address found'
    return data['results'][0]['formatted_address']

class PostmateHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        http = tornado.httpclient.AsyncHTTPClient()
        request = tornado.httpclient.HTTPRequest(
            'https://api.postmates.com/v1/customers/%s/deliveries' % config.USER,
            method='GET',
            auth_username=config.API_KEY,
            )
        response = yield tornado.gen.Task(http.fetch, request)
        self.write(response.body)
        
    @tornado.gen.coroutine
    def post(self):
        post_args = self.request.arguments
        http = tornado.httpclient.AsyncHTTPClient()
        user = 'cus_KUqa0QKBdSyjO-'
        request_body = {
            'manifest': 'Food delivery',
            'pickup_name': 'Place',
            'pickup_address': getAddressFromGeo(post_args['lat'][0], post_args['lng'][0]),
            'pickup_phone_number': '111-111-1111',
            'dropoff_name': 'MIT',
            'dropoff_address': '77 Massachusetts Ave, Cambridge, MA 02139',
            'dropoff_phone_number': '111-111-2222'
        }
        request_body = urllib.urlencode(request_body)
        request = tornado.httpclient.HTTPRequest(
            'https://api.postmates.com/v1/customers/%s/deliveries' % config.USER,
            method='POST',
            auth_username=config.API_KEY,
            body=request_body
            )
        response = yield tornado.gen.Task(http.fetch, request)
        self.write(response.body)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('web/index.html')

def make_app():
    return tornado.web.Application([
        (r'/', MainHandler),
        (r'/create_delivery', PostmateHandler),
        (r'/list_delivery', PostmateHandler),
        (r'/color/(.*)',tornado.web.StaticFileHandler, {'path': './web/color'}),
        (r'/css/(.*)',tornado.web.StaticFileHandler, {'path': './web/css'}),
        (r'/font-awesome/(.*)',tornado.web.StaticFileHandler, {'path': './web/font-awesome'}),
        (r'/fonts/(.*)',tornado.web.StaticFileHandler, {'path': './web/fonts'}),
        (r'/img/(.*)',tornado.web.StaticFileHandler, {'path': './web/img'}),
        (r'/js/(.*)',tornado.web.StaticFileHandler, {'path': './web/js'}),
    ])

if __name__ == '__main__':
    app = make_app()
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()
