#!/usr/bin/env python
import lib
from apps.geo.models import City, Subway
from metros import METROS as METROES

def update_metroes():
    for city in METROES.keys():
        c = City.objects.get_or_create(title=city)
        for sub in METROES[city]:
            if not Subway.objects.filter(city=c[0], title=sub):
                Subway.objects.create(city=c[0], title=sub)


if __name__ == '__main__':
    update_metroes()
