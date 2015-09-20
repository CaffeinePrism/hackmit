import random
import json
import config

import distance_helpers

import urllib.request
import base64

def getAddressFromGeo(lat, lng):
    url = 'http://maps.googleapis.com/maps/api/geocode/json'
    with urllib.request.urlopen('%s?latlng=%s,%s&sensor=false' %
                            (url, lat, lng)) as response:
        data = json.loads(response.read().decode())
        if data['status'] == 'ZERO_RESULTS':
            return 'No address found'
        return data['results'][0]['formatted_address']



lat, lng = (42.358901, -71.096952)
lat += (random.random()-0.5)*8/100
lng += (random.random()-0.5)*8/100

shelters = json.load(open('shelters.json', 'r'))
closest_shelter = shelters[distance_helpers.get_closest(lat, lng, shelters)]
params = {
    'manifest': 'http://lorempixel.com/400/200/food/,food',
    'pickup_name': 'Pickup Place',
    'pickup_address': getAddressFromGeo(lat, lng),
    'pickup_phone_number': '111-111-1111',
    'dropoff_name': closest_shelter['name'],
    'dropoff_address': getAddressFromGeo(closest_shelter['lat'], closest_shelter['lng']),
    'dropoff_phone_number': closest_shelter['phone'],
    'robo_pickup': "00:00:01",
    'robo_pickup_complete': "00:00:02",
    'robo_dropoff': "00:00:03",
    'robo_delivered': "00:04:00"
}
request = urllib.request.Request(
    'https://api.postmates.com/v1/customers/%s/deliveries' % config.USER,
    method='POST',
    headers={'Authorization': 'Basic ' + base64.b64encode(bytes(config.POSTMATES_API_KEY + ':', 'utf-8')).decode() },
    data=urllib.parse.urlencode(params).encode('utf-8')
    )

urllib.request.urlopen(request)
