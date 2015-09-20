import json
import tornado.ioloop
import tornado.httpclient
import tornado.web

try:
    import config
except ImportError:
    import example_config as config
import urllib.parse

import distance_helpers

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

class PostmatesHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.shelters = json.load(open('shelters.json', 'r'))

    @tornado.gen.coroutine
    def get(self):
        http = tornado.httpclient.AsyncHTTPClient()
        request = tornado.httpclient.HTTPRequest(
            'https://api.postmates.com/v1/customers/%s/deliveries' % config.USER,
            method='GET',
            auth_username=config.POSTMATES_API_KEY,
            )
        response = yield tornado.gen.Task(http.fetch, request)
        self.write(response.body)

    def process_images(self, urls):
        http = tornado.httpclient.HTTPClient()
        d = {}
        for url in urls:
            request = tornado.httpclient.HTTPRequest(
                'https://api.clarifai.com/v1/tag/?url=%s' % url,
                method='GET',
                headers={'Authorization': 'Bearer %s' % config.CLARIFAI_API_KEY}
            )

            response = http.fetch(request)
            response = json.loads(response.body.decode())
            d[url] = response['results'][0]['result']['tag']['classes'][0:3]
        return d

    @tornado.gen.coroutine
    def post(self):

        post_args = tornado.escape.json_decode(self.request.body)
        post_lat, post_lng = post_args['lat'], post_args['lng']
        urls = post_args['image_urls']

        tags = self.process_images(urls)

        closest_shelter = self.shelters[distance_helpers.get_closest(post_lat, post_lng, self.shelters)]

        http = tornado.httpclient.AsyncHTTPClient()

        params = {
            'manifest': 'Food delivery',
            'pickup_name': 'Place',
            'pickup_address': getAddressFromGeo(post_lat, post_lng),
            'pickup_phone_number': '111-111-1111',
            'dropoff_name': 'Delivery Place',
            'dropoff_address': getAddressFromGeo(closest_shelter['lat'], closest_shelter['lng']),
            'dropoff_phone_number': '111-111-2222',
        }
        request = tornado.httpclient.HTTPRequest(
            'https://api.postmates.com/v1/customers/%s/deliveries' % config.USER,
            method='POST',
            auth_username=config.POSTMATES_API_KEY,
            body=urllib.parse.urlencode(params)
            )
        response = yield tornado.gen.Task(http.fetch, request)
        response = json.loads(response.body.decode())

        response['clarifai_tags'] = tags
        self.write(response)


class DeliveryStatusHandler(tornado.web.RequestHandler):
        
    # Get updated info on a single delivery
    @tornado.gen.coroutine
    def get(self, delivery_id):
        http = tornado.httpclient.AsyncHTTPClient()
        request = tornado.httpclient.HTTPRequest(
            'https://api.postmates.com/v1/customers/%s/deliveries/%s' % 
            (config.USER, delivery_id),
            method='GET',
            auth_username=config.POSTMATES_API_KEY,
            )
        response = yield tornado.gen.Task(http.fetch, request)
        self.write(response.body)

class CancelDeliveryHandler(tornado.web.RequestHandler):

    # Cancel delivery
    @tornado.gen.coroutine
    def post(self, delivery_id):
        http = tornado.httpclient.AsyncHTTPClient()

        request = tornado.httpclient.HTTPRequest(
            'https://api.postmates.com/v1/customers/%s/deliveries/%s/cancel' % 
            (config.USER, delivery_id),
            method='POST',
            auth_username=config.POSTMATES_API_KEY,
            body=urllib.parse.urlencode({'this': 'needs a body'})

            )
        response = yield tornado.gen.Task(http.fetch, request)
        response = json.loads(response.body.decode())

        self.write(response)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('web/index.html')

def make_app():
    return tornado.web.Application([
        (r'/', MainHandler),
        (r'/create_delivery', PostmatesHandler),
        (r'/list_delivery', PostmatesHandler),
        (r'/delivery_status/([^/]+)', DeliveryStatusHandler),
        (r'/cancel_delivery/([^/]+)', CancelDeliveryHandler),
        (r'/color/(.*)',tornado.web.StaticFileHandler, {'path': './web/color'}),
        (r'/css/(.*)',tornado.web.StaticFileHandler, {'path': './web/css'}),
        (r'/font-awesome/(.*)',tornado.web.StaticFileHandler, {'path': './web/font-awesome'}),
        (r'/fonts/(.*)',tornado.web.StaticFileHandler, {'path': './web/fonts'}),
        (r'/img/(.*)',tornado.web.StaticFileHandler, {'path': './web/img'}),
        (r'/js/(.*)',tornado.web.StaticFileHandler, {'path': './web/js'}),
        (r'/api/latlng', PostmatesHandler)
    ], debug=True)

if __name__ == '__main__':
    app = make_app()
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()
