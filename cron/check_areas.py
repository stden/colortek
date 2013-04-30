#!/usr/bin/env python
# coding: utf-8
import lib
from apps.geo.models import Subway
from areas.spb import areas

def main():
    for a in areas:
        Subway.objects.get(title__iexact=a[0])


if __name__ == '__mail__':
    main()
