from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from apps.core.helpers import get_object_or_None
# Create your models here.


class City(models.Model):
    title = models.CharField(
        _('city'), max_length=128,
        help_text=_('City or other settlement type'))
    priority = models.PositiveIntegerField(
        _("Priority"),
        help_text=_("Ordering priority"), default=1)
    codename = models.CharField(
        _('codename'), help_text=_("for fast city access requirements,"
            "for example retrieve city's subway map"
        ),
        max_length=32,
        blank=True, null=True
    )
    iso = models.CharField(
        _('iso'), max_length=256,
        help_text=_("iso name for city"), blank=True, null=True
    )

    @property
    def subways(self):
        return self.subway_city_set

    @property
    def subway_links(self):
        return YaLink.objects.filter(subway__in=self.subways.all())

    class Meta:
        verbose_name = _('City')
        verbose_name_plural = _('Cities')
        ordering = ['-priority', 'id']

    def __unicode__(self):
        return self.title


class Subway(models.Model):
    title = models.CharField(
        _('subway'), max_length=256,
        help_text=_('Subway title'))
    city = models.ForeignKey(
        City, verbose_name=_("city"), related_name='subway_city_set'
    )

    def __unicode__(self):
        return "[%s] %s" % ( self.city.title, self.title)
    
    @property
    def yalink(self):
        link = self.yalink_subway_set.all()
        if link:
            return link[0]
        return None

    def get_yalink(self):
        return self.yalink
    get_yalink.short_description = _('yalink')

    @property
    def yalinks(self):
        return self.yalink_subway_set

    class Meta:
        verbose_name = _('Subway')
        verbose_name_plural = _('Subways')
        ordering = ['-city__priority', 'city__id', 'title']


class YaType(models.Model):
    title = models.CharField(
        _("type"), help_text=_("yalink type"), default='rect',
        max_length=32
    )

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _("YaType")
        verbose_name_plural = _("YaTypes")

class YaLink(models.Model):
    subway = models.ForeignKey(
        Subway, related_name='yalink_subway_set',
        verbose_name=_('subway')
    )
    coords = models.CommaSeparatedIntegerField(
        _('coords'), help_text=_("yandex map coords"),
        max_length=512
    )
    type = models.ForeignKey(
        YaType, related_name='yalink_type_set',
        default=1,
        verbose_name=_('type')
    )

    def __unicode__(self):
        return "%s, %s [%s]" % (
            self.subway.city.title,
            self.subway.title,
            self.coords
        )

    class Meta:
        verbose_name = _("Yalink")
        verbose_name_plural = _("Yalinks")

class GlobalPosition(models.Model):
    lat = models.FloatField(
        _("latitude"), default=59.939038999999994
    )
    lng = models.FloatField(
        _('longtitude'), default=30.315784999999998
    )

    class Meta:
        abstract = True


class GPos(GlobalPosition):
    """ Google position coordinates for google maps
        the way to separate different maps services
    """
    user = models.ForeignKey(
        User, related_name='gpos_user_set',
        verbose_name=_('user')
    )
    description = models.CharField(
        _('description'), max_length=256, blank=True, null=True
    )

    def __unicode__(self):
        return "%s [%s, %s]" % (
            self.user.username, self.lat, self.lng
        )

    class Meta:
        verbose_name = _("Google position")
        verbose_name_plural = _("Goole positions")
