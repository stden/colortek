from django.http import HttpResponse
import re
from apps.geo.models import IPGeoBase, City


class GeoMiddleware(object):
    def process_request(self, request):
        path = request.META.get('X')
        pattern = re.compile('catalog')
        if not request.session.get('city'):
            ip = request.META.get('HTTP_X_FORWARDED_FOR', '194.85.174.26')

            if ip and len(ip.split(',')) >= 2:
                ip = ip.split(',')[-2].strip()
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
        # print pattern.search(path)
        return