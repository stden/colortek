from django.contrib.gis.utils import GeoIP
from django_ipgeobase.models import IPGeoBase
from apps.geo.models import City

class LookupDict(object):
    def __init__(self, geo):
        self.geo = geo

    def __getitem__(self, item):
        return self.geo[item]

    def __iter__(self):
        raise TypeError("LookupDict is not iterable")

class GeoIPLookupDict(object):
    def __init__(self, ip):
        self.geoip = GeoIP()
        self.ip = ip

    def __getitem__(self, item):
        call = getattr(self.geoip, item) if hasattr(self.geoip, item) else lambda x: None
        if self.ip:
            return call(self.ip)
        return None

    def __iter__(self):
        raise TypeError("GeoIPLookupDict is not iterable")

def geoip(request):
    ip = request.META.get('HTTP_X_REAL_IP', None)
    print request
    print 'IP', ip
    geop = IPGeoBase.objects.by_ip(ip)
    if geop.exists():
        geop = geop[0]
    city_id = request.session.get('city', None)
    city_not_in_list = None
    if not city_id:    
        try:
            city_id = request.user.city.id
        except AttributeError:
            city_id = None
    if geop and not city_id and geop.city:
        try:
            city = City.objects.get(title=geop.city)
        except City.DoesNotExist:
            city = None
        if city:
            request.session['city'] = city.pk
            request.session['city_title'] = city.title
            request.session.save()
        else:
            city_not_in_list = True  
                                      
    return {
        'geoip': GeoIPLookupDict(ip),
        'rgeoip': geop,
        'city_not_in_list': city_not_in_list
    }
