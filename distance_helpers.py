import math
def haversine(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 3959 # miles

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d

def approximate_distances(lat, lng, dataset):
    '''
    Returns a list of shelters close to current lat/lng
    '''
    nearby = []
    for i,item in dataset.items():
        lat1, lng1 = item['lat'], item['lng']
        if (lat1-0.1 <= lat <= lat1+0.1) and (lng1-0.1 <= lng <= lng1+0.1): # ~6.8mi radius
            nearby.append(i)
    return nearby

def get_closest(lat, lng, dataset):
    dict = {}
    for pos in approximate_distances(lat, lng, dataset):
        lat1, lng1 = dataset[pos]['lat'], dataset[pos]['lng']
        dict[pos] = haversine((lat1, lng1), (lat, lng))

    return min(dict, key=dict.get)
