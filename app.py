import json
import tornado.ioloop
import tornado.httpclient
import tornado.web

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
    def post(self):
        post_args = tornado.escape.json_decode(self.request.body)
        http = tornado.httpclient.AsyncHTTPClient()
        user = 'cus_KUqa0QKBdSyjO-'
        request = tornado.httpclient.HTTPRequest(
            'https://api.postmates.com/v1/customers/%s/deliveries' % user, 
            method='POST',
            manifest='Food delivery',
            pickup_name='Place',
            pickup_address=getAddressFromGeo(post_args['lat'], post_args['lng']),
            pickup_phone_number='111-111-1111',
            dropoff_name='Delivery Place',
            dropoff_address='Delivery Address',
            dropoff_phone_number='111-111-2222'
            )
        response = yield tornado.gen.Task(http.fetch, request)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('web/index.html')

def make_app():
    return tornado.web.Application([
        (r'/', MainHandler),
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
