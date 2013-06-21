import re

from datetime import datetime
from functools import partial

from django.core.serializers import serialize
from django.db import models
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, UserManager
from django.contrib.auth.admin import UserAdmin
from django.conf import settings
from django import forms
from django.core.urlresolvers import reverse
from apps.core.helpers import get_object_or_None
import caching.base

User.__bases__ = (caching.base.CachingMixin, models.Model)
UserManager.__bases__ = (caching.base.CachingManager, models.Manager)

User.add_to_class(
    'invites', models.PositiveSmallIntegerField(
        _('invites'), help_text=_("intites count"), default=0)
)
User.add_to_class(
    'city', models.ForeignKey('geo.City', verbose_name=_("city"), default=1))
User.add_to_class(
    'middle_name',
    models.CharField(
        _('middle name'), max_length=128, blank=True, null=True)
)
User.add_to_class(
    'is_partner', models.BooleanField(
        verbose_name=_('is partner?'),
        default=False, blank=True
    )
)
User.add_to_class(
    'phone',
    models.CharField(
        _('Phone'), max_length=15, blank=True,
        help_text='7 9xx xxx xx xx', null=True)
)
User.add_to_class(
    'service',
    models.ForeignKey('catalog.Service', blank=True, null=True,
                      verbose_name=_("service")))
User.add_to_class(
    'service_name',
    models.CharField(
        _("service name"), null=True, blank=True, max_length=265)
)
User.add_to_class(
    'address', models.CharField(
        _('address'), help_text=_("for example: <i>Petrogradskaya</i>"),
        max_length=512, null=True)
)
User.add_to_class(
    'apartment', models.CharField(
        _('aparment'), help_text=_("Apartment number, for example:<i>17</i>"),
        max_length=16, blank=True, null=True)
)
User.add_to_class(
    'building', models.CharField(
    _('building'), help_text=_("for example: <i>2/2 attr 3</i>"),
    max_length=32, null=True)
)
User.add_to_class(
    'site', models.URLField(
    _('site url'), help_text=_("Your company site url"),
    blank=True, null=True)
)
User.add_to_class(
    'subway', models.ForeignKey(
    'geo.Subway', verbose_name=_("subway"),
    help_text=_("the nearest subway station"),
    blank=True, null=True)
)
User.add_to_class(
    'avarage_cost', models.DecimalField(
    _("mean cost"), help_text=_("Avarage cost for purchase with deliver for\
free"),
    max_digits=10, decimal_places=2,
    null=True, blank=True)
)
User.add_to_class(
    'avarage_deliver_time', models.CharField(
    _("avarage delive time"), null=True, blank=True,
    help_text=_("1d10h15m"),
    max_length=32)
)
# User.add_to_class(
#    'deliver_time_multiplier', models.PositiveSmallIntegerField(
#        _('deliver time multiplier'), null=True, blank=True,
#        default=1
#    )
# )
User.add_to_class(
    'avarage_deliver_cost', models.DecimalField(
    _('deliver cost'), help_text=_("Avarage cost for deliver"),
    max_digits=10, decimal_places=2, null=True, blank=True
    )
)
User.add_to_class(
    'minimal_cost', models.DecimalField(
        _('minimal cost'), help_text=_("Minimal cost allowed to order"),
        max_digits=10, decimal_places=2, default=0,
    )
)
User.add_to_class(
    'description', models.TextField(
    _('description'),
    help_text=_("partner given description"),
    null=True, blank=True, max_length=4096)
)
User.add_to_class(
    'bonus_score', models.DecimalField(
        _("bonus score"), help_text=_("bonus score"), default=0,
        max_digits=10, decimal_places=2
    )
)
User.add_to_class(
    'logo', models.ImageField(
        _("logo"), help_text=_("service logo"), blank=True, null=True,
        upload_to=lambda s, fn: ("service/%s/%s" % (s.service.id, fn)),
        max_length=256
    )
)
User.add_to_class(
    'glat', models.FloatField(
        _("google latitude"), help_text=_('google maps latitude coordinate'),
        blank=True, null=True
    )
)
User.add_to_class(
    'glng', models.FloatField(
        _("google longitude"),
        help_text=_('google maps longitude coordinate'),
        blank=True, null=True
    )
)
User.add_to_class(
    'is_operator', models.BooleanField(
        verbose_name=_('is operator?'), default=False, blank=True
    )
)
User.add_to_class(
    'has_online_payment', models.BooleanField(
        _('has online payment?'), default=False
     )
)
User.add_to_class(
    'birthday', models.DateTimeField(
        _("birthday"), null=True, blank=True
    )
)
User.add_to_class(
    'commission', models.DecimalField(
        _('commission'), null=True, blank=True,
        default=settings.COMMISSION_RATE,
        help_text=_("commission value should be lower than 1, "
            "for example: 0.1 - 10%, 0.15 - 15% and so on"
        ),
        max_digits=10, decimal_places=2,
    )
)
User.add_to_class(
    'is_published', models.BooleanField(
        _('is published?'), default=False
    )
)
User.add_to_class(
    'published_once', models.BooleanField(
        _('published once'), default=False
    )
)
User.add_to_class(
    'additional', models.TextField(
        _("additional"),
        help_text=_("additional information"), null=True, blank=True
    )
)
User.add_to_class(
    'is_verified', models.BooleanField(
        _('is verified?'),
        help_text=_("marks if user passed through "
        "post-registration verification"),
        default=False
    )
)
User.add_to_class(
    'publish_date', models.DateTimeField(
        _('publish date'), help_text=_(
            "date when the service was approved to use"
            " in the user search output list"
        ), default=datetime.now, null=True, blank=True

    )
)
User.add_to_class(
    'dengi_online', models.PositiveIntegerField(
        _('dengi online'),
        help_text=_("dengi online projectid"),
        null=True, blank=True
    )
)


User._meta.get_field_by_name('email')[0].formfield = forms.EmailField
PartnerBooleanField = partial(forms.BooleanField, required=False,
                              label=_("is partner?"))
OperatorBooleanField = partial(forms.BooleanField, required=False,
                               label=_("is operator?"))

TextField = partial(
    forms.CharField,
    required=False
)

User._meta.get_field_by_name('is_partner')[0].formfield = PartnerBooleanField
User._meta.get_field_by_name('is_operator')[0].formfield = OperatorBooleanField


def export_as_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    serialize("csv", queryset, stream=response,
              fields=('username', 'first_name', 'phone', 'city',
                      'address', 'building', 'apartment', 'birthday'))
    response['Content-Disposition'] = 'attachment; filename="users.csv"'
    return response

UserAdmin.fieldsets += (
    (_('Profile'), {
        'fields': (
            'phone', 'dengi_online', 'is_partner', 'is_operator',
            'has_online_payment', 'service', 'service_name', 'city',
            'subway', 'avarage_cost', 'avarage_deliver_cost',
            'minimal_cost', 'avarage_deliver_time', 'logo',
            'commission', 'is_published', 'birthday',
            'description', 'additional'
        ),
        'classes': ('collapse',),
    }
    ),
)
creation_fields = (
    'username', 'email', 'phone', 'service', 'dengi_online',
    'is_partner', 'is_operator', 'password1', 'password2'
)
UserAdmin.list_display += (
    'service_name', 'dengi_online', 'is_partner', 'is_operator',
    'has_online_payment', 'is_published', 'is_verified',
)
UserAdmin.list_filter += (
    'has_online_payment', 'is_partner', 'is_published', 'is_verified',
    'is_operator',
)
UserAdmin.list_editable = ('is_published', 'is_verified')
UserAdmin.search_fields += ('service_name', 'dengi_online',)
UserAdmin.add_fieldsets[0][1]['fields'] = creation_fields
UserAdmin.search_fields += ('phone',)
UserAdmin.actions = [export_as_csv, ]


class UserExtenssion(object):
    """ overrides, extenssions and so on """
    @property
    def rating_atoms(self):
        return self.atom_mean_rating_user_set

    @property
    def bonus_transaction(self):
        return self.bonus_client_set

    def reload_bonus_score(self, rebuild=True):
        if not rebuild:
            # fast bonus score rebuild, looking just for unprocessed
            # transactions
            bonuses = self.bonus_transaction.filter(is_processed=False)
            amount = sum([i['amount'] for i in bonuses.values('amount')])
            self.bonus_score += amount
            bonuses.update(is_processed=True)
        else:
            # rebuilds bonus score looking for every iteration
            # it could be slow but it restores bonus score withing
            # its transaction history
            self.bonus_score = 0  # initial
            bonuses = self.bonus_transaction.all()
            amount = sum([i['amount'] for i in bonuses.values('amount')])
            self.bonus_score += amount
            bonuses.filter(is_processed=False).update(is_processed=True)
        if self.bonus_score < 0:
            self.bonus_score = 0
        self.save()

    def get_real_name(self):
        if self.last_name and self.first_name:
            return "%s %s" % (self.last_name, self.first_name)
        elif self.last_name or self.first_name:
            return "%s" % (self.last_name or self.first_name)
        return self.username

    def get_phone(self):
        return self.phone if self.phone else '-'

    @property
    def phones(self):
        return self.phone_user_set
        
    @property
    def emails(self):
        return self.email_user_set 
        
    def get_emails(self):
        emails = [i.email for i in self.email_user_set.all()]
        emails.append(self.email)  
        return emails

    @property
    def orders(self):
        return self.order_client_set

    def has_orders(self):
        return bool(self.orders.count())

    def get_bonus_score(self):
        return int(self.bonus_score)

    @property
    def votes(self):
        from apps.catalog.models import Vote
        return Vote.objects.filter(
            order__container__owner=self, is_approved=True
        )

    def get_votes_count(self):
        return self.votes.count()

    @property
    def containers(self):
        return self.container_owner_set

    @property
    def markers(self):
        return self.gpos_user_set

    def get_specials(self):
        from apps.catalog.models import Item
        now = datetime.now().replace(second=0, microsecond=0)
        items = Item.objects.filter(
            container__in=self.containers.all(),
            is_special_active=True,
            special_expires__gte=now
        )
        return items

    def get_all_specials(self):
        items = self.get_specials()
        specials = self.get_active_specials()
        return (items, specials)

    @property
    def addons(self):
        from apps.catalog.models import AddonList
        return AddonList.objects.filter(container__in=self.containers.all())

    @property
    def items(self):
        return self.item_container_set

    @property
    def specials(self):
        return self.special_owner_set

    @property
    def categories(self):
        from apps.catalog.models import Category
        return Category.objects.filter(container_category_set__in=
                                       self.containers.all()).distinct()

    @property
    def schedule(self):
        schedule = self.schedule_user_set.all()
        if schedule:
            return schedule[0]
        return None

    @property
    def verification(self):
        return get_object_or_None(self.verification_user_set)

    def get_active_specials(self):
        return self.specials.filter(is_active=True)

    def get_top_containers(self):
        return self.containers.filter(container=None)

    def get_avarage_rating(self):
        container = self.containers.latest('id')
        return int(container.get_common_rating())

    @property
    def vote_atoms(self):
        from apps.catalog.models import VoteAtom
        atoms = VoteAtom.objects.filter(klass__service=self.service)
        return atoms

    def get_service_url(self):
        return reverse('catalog:service-page', args=(self.pk,))

    def get_max_rates(self):
        atoms = self.vote_atoms.all()
        if atoms.count():
            return sum([
                i['max'] for i in atoms.values('max')]) / atoms.count() or 1
        return 0

    def get_logo(self):
        return self.logo if self.logo else '/media/img/no-logo.png'

    @property
    def deliver_cost(self):
        return self.deliver_cost_user_set

    def get_deliver_cost(self, threshold):
        if self.avarage_cost is not None:
            return 0 if (threshold >= self.avarage_cost) else\
                self.avarage_deliver_cost\
            if self.avarage_deliver_cost is not None else 0
        return self.avarage_deliver_cost if self.avarage_deliver_cost is not\
            None else 0

    def get_deliver_time(self):
        dt = self.avarage_deliver_time
        if ':' in self.avarage_deliver_time:
            dt = '0d%sh%sm' % (dt.split(':')[0], dt.split(':')[1])

        days = "".join(re.findall('(\d+)d', dt))
        hours = "".join(re.findall('(\d+)h', dt))
        minutes = "".join(re.findall('(\d+)m', dt))

        return {
            'days': int(days) if days.isdigit() else days,
            'hours': int(hours) if hours.isdigit() else hours,
            'minutes': int(minutes) if minutes.isdigit() else minutes,
        }

    def get_deliver_price(self, lat, lng):
        from apps.geo.helpers import l2distance
        meters = l2distance((self.glat, self.glng), (lat, lng))
        kms = meters / 1000
        cost = (
            self.deliver_cost.filter(min__gte=kms) |
            self.deliver_cost.filter(max__gte=kms)
        )
        if cost:
            return {'success': True, 'deliver_cost': cost[0].cost}

        return {
            'success': False,
            'message': unicode(_(
                "We apologize, but You can not order with"
                "given service because"
                "it does not work in your coverage area,"
                "please select another place to order"
                )
            )
        }

User.__bases__ = (UserExtenssion,) + User.__bases__


# Create your models here.
