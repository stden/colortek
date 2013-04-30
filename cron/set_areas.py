#!/usr/bin/env python
# coding: utf-8
import lib
from apps.geo.models import City, Subway, YaLink, YaType
from apps.core.helpers import get_object_or_None

def set_areas(city, areas):
    for area in areas:
        #print area[0]
        #print city.title
        subway = get_object_or_None(Subway, title__iexact=area[0], city=city)
        if not subway:
            print "there is no such subway: %s" % area[0]
            continue

        if not subway.yalinks.all():
            coord = ",".join([str(i) for i in area[1]])
            type_id = None
            create = dict(subway=subway, coords=coord)

            if len(area[1]) > 4:
                typ_id = YaType.objects.get(title='poly')
                create.update({'type': typ_id})
            YaLink.objects.create(**create)

def main():
    from areas import spb, msk
    city = City.objects.get(title=u'Санкт-Петербург')
    set_areas(city, spb.areas)
    city = City.objects.get(title=u'Москва')
    set_areas(city, msk.areas)

if __name__ == '__main__':
    main()
