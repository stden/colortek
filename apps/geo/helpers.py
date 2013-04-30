import math

def l2distance(origin, destination, si=10):
    lat1, lng1 = origin
    lat2, lng2 = destination
    radius = 6371 #km meters

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lng2-lng1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d * 1000 # meters

def ltos(deg, si=1):
    return (deg/111000) * 10**si #meters
