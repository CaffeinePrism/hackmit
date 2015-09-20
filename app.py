import json
import redis
import tornado.ioloop
import tornado.httpclient
import tornado.web

try:
    import config
except ImportError:
    import example_config as config
import urllib.parse

import distance_helpers

r = redis.StrictRedis(host='dev.richardli.me', port=6379, db=0)


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
        del post_args['lat']
        del post_args['lng']
        # post_args is now a dictionary with urls as keys and corresponding tags
        # for values (each url has only one tag)

        closest_shelter = self.shelters[distance_helpers.get_closest(post_lat, post_lng, self.shelters)]

        http = tornado.httpclient.AsyncHTTPClient()

        params = {
            'manifest': ','.join(['%s,%s' % (x, post_args[x]) for x in post_args.keys()]),
            'pickup_name': 'Pickup Place',
            'pickup_address': getAddressFromGeo(post_lat, post_lng),
            'pickup_phone_number': '111-111-1111',
            'dropoff_name': closest_shelter['name'],
            'dropoff_address': getAddressFromGeo(closest_shelter['lat'], closest_shelter['lng']),
            'dropoff_phone_number': closest_shelter['phone'],
            'robo_pickup': "00:00:01",
            'robo_pickup_complete': "00:00:02",
            'robo_dropoff': "00:00:03",
            'robo_delivered': "00:03:00"
        }
        request = tornado.httpclient.HTTPRequest(
            'https://api.postmates.com/v1/customers/%s/deliveries' % config.USER,
            method='POST',
            auth_username=config.POSTMATES_API_KEY,
            body=urllib.parse.urlencode(params)
            )
        response = yield tornado.gen.Task(http.fetch, request)
        response = json.loads(response.body.decode())
        r.set(response['id'], json.dumps(post_args))

        self.write(response)

class PostmatesWebhookHandler(tornado.web.RequestHandler):
    def initialize(self, couriers):
        self.couriers = couriers

    def get(self):
        self.write(json.dumps(self.couriers))

    def post(self):
        request = tornado.escape.json_decode(self.request.body)
        print('ping!')
        kind = request['kind']
        delivery_id = request['delivery_id']
        print(kind == 'event.courier_update')
        if kind == 'event.delivery_status':
            if request['status'] == 'dropoff':
                self.couriers[delivery_id] = request['data']['courier']
            elif request['status'] == 'delivered':
                if self.couriers.get(delivery_id):
                    del self.couriers[delivery_id]
        elif kind == 'event.courier_update':
            self.couriers[delivery_id] = request['data']['courier']
            print(self.couriers)

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

def make_app():
    couriers = {}
    return tornado.web.Application([
        (r'/create_delivery', PostmatesHandler),
        (r'/list_delivery', PostmatesHandler),
        (r'/active_delivery', PostmatesWebhookHandler, dict(couriers=couriers)),
        (r'/delivery_status/([^/]+)', DeliveryStatusHandler),
        (r'/cancel_delivery/([^/]+)', CancelDeliveryHandler),
        (r'/api/latlng', PostmatesHandler),
        (r'/api/webhook', PostmatesWebhookHandler, dict(couriers=couriers)),
        (r'/(.*)',tornado.web.StaticFileHandler, {'path': './vis', 'default_filename': 'index.html'})
    ], debug=True)

app = make_app()
if __name__ == '__main__':
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()
