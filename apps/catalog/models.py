# coding: utf-8
import caching.base
from datetime import datetime, timedelta

from apps.geo.models import City
from apps.core.helpers import get_object_or_None
from apps.catalog.managers import ItemManager, AddonManager, OrderManager

from django.db import models
from django.db.models import Manager
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.urlresolvers import reverse
from django.conf import settings

from uuid import uuid1, uuid4
from decimal import Decimal
import caching.base


# Create your models here.
from cart import Cart
TRANSLATION_OVERRIDES = (
    _("Catalog"),
    _("catalog")
)

ORDER_STATUSES = (
    ('not_confirmed', _("not confirmed")),  # in progress
    ('checking', _("checking")),
    ('approved', _('approved')),  # approved status
    ('rejected', _('rejected')),  # rejected, declined
    # ('not_processed', _('not processed')),  # not processed
    ('processed', _("processed")),  # processed
    # ('paid', _("paid")),  # paid
    ('finished', _("finished")),  # reserved status

)
FAST_TRANS_STATUS = (
    _("not_confirmed"),
)

class Service(models.Model):
    """ Service provides """
    title = models.CharField(_("title"), max_length=128)
    description = models.CharField(
        _("description"), max_length=1024,
        blank=True
    )
    codename = models.CharField(
        _('codename'),
        help_text=_(
            "alias for service for internal use, for example food or stuff"
        ),
        unique=True, max_length=32
    )
    logo = models.ImageField(
        _("logo"), help_text=_("Logo for service"), blank=True, null=True,
        upload_to=lambda s, fn: ("services/%s_%s" % (s.codename, fn)),
        max_length=256
    )
    weight = models.PositiveIntegerField(
        _('weight'), help_text=_('less is prior'),
        default=0
    )

    @property
    def containers(self):
        return self.container_service_set

    @property
    def blog_types(self):
        return self.post_type_service_set

    @property
    def categories(self):
        return self.category_service_set

    def get_top_containers(self):
        return self.containers.filter(container=None)

    def get_container_types(self):
        return self.containers.values('title').distinct()

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _("Service")
        verbose_name_plural = _("Services")
        ordering = ['weight', ]


class ServiceTerm(caching.base.CachingMixin, models.Model):
    service = models.ForeignKey(
        Service, related_name='service_term_set',
        verbose_name=_("service")
    )
    code = models.CharField(
        _('code'), help_text=_('codename for term'),
        max_length=128
    )
    term = models.CharField(
        _('term'), help_text=_("term"),
        max_length=4096
    )

    objects = caching.base.CachingManager()

    def __unicode__(self):
        return '[%(service)s] %(code)s - %(term)s' % {
            'service': self.service.title,
            'code': self.code,
            'term': self.term
        }

    class Meta:
        verbose_name = _("Service term")
        verbose_name_plural = _("Service terms")
        unique_together = (('service', 'code'),)


class AtomMeanRating(models.Model):
    """ Should be OneToOne for each user, beacuse this aggragates mean
    rating for each atom we add for voting for every owner containers
    It looks like OH MY GOD, WHAT THE HECK IS THIS, but I tried to make it
    simple without any restrictions withing choosing specific database scheme
    and other stuff or something like Pickled objects (because we can not
    search through database then).
    So just read or request documentation on this
    """
    value = models.DecimalField(
        _('value'), max_digits=10,
        decimal_places=2, default=0
    )
    atom = models.ForeignKey(
        'VoteAtom', related_name='atom_mean_rating_voteatom_set'
    )
    # denormalization
    service = models.ForeignKey(
        Service, related_name='atom_mean_rating_service_set'
    )
    owner = models.ForeignKey(
        User, related_name='atom_mean_rating_user_set'
    )

    def __unicode__(self):
        return "%s: %s" % (self.atom.title, str(self.value))

    def get_value(self):
        return int(self.value)

    class Meta:
        verbose_name = _("Atom rating")
        verbose_name_plural = _("Atom ratings")


class Category(caching.base.CachingMixin, models.Model):
    service = models.ForeignKey(
        Service,
        related_name='category_service_set',
        verbose_name=_('service'))
    title = models.CharField(
        _("Category"),
        help_text=_("container related category, spanish/chineese and so on"),
        max_length=256
    )
    weight = models.PositiveIntegerField(
        _("weight"),
        help_text=_("weight for order, less is prior"),
        default=0
    )
    parent = models.ForeignKey(
        'self',
        related_name='category_set', null=True, blank=True,
        verbose_name=_("parent")
    )
    """
    created_on = models.DateTimeField(
        _('created on'), default=datetime.now,
        null=True, blank=True
    )
    updated_on = models.DateTimeField(
        _('created on'), default=datetime.now,
        null=True, blank=True
    )
    """

    objects = caching.base.CachingManager()

    @property
    def containers(self):
        return self.container_category_set

    def get_unique_containers(self):
        return self.containers.order_by(
            'title').distinct('title').filter(container=None)

    # def __unicode__(self):
    def __unicode__(self):
        # hotfix for recursive container set
        if self == self.parent:
            return self.title

        out = self.title
        target = self
        while 1:
            if target.parent is None:
                break
            out = target.parent.title + '->' + out
            target = target.parent
        return "[%s] %s" % (self.service.title, out)
        # return "%s [%s]" % (self.title, self.service.title)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ('weight',)


class Container(caching.base.CachingMixin, models.Model):
    """ Container provides the list of catalogue for each service """
    owner = models.ForeignKey(
        User, verbose_name=_("container owner"), null=True,
        related_name='container_owner_set',
    )
    container = models.ForeignKey(
        'self', related_name='parent_container_set',
        null=True, blank=True,
        verbose_name=_('container'))
    category = models.ForeignKey(
        Category,
        related_name='container_category_set',
        null=True, blank=True,
        verbose_name=_('category')
    )
    title = models.CharField(_("title"), max_length=128)
    description = models.CharField(
        _("description"), max_length=1024,
        blank=True, null=True)
    service = models.ForeignKey(
        Service, default=1, related_name='container_service_set',
        verbose_name=_('service')
    )
    mean_rating = models.DecimalField(
        _('mean rating'), max_digits=10,
        decimal_places=2, default=0
    )

    weight = models.PositiveIntegerField(
        _('weight'), help_text=_("ordering weight bigger is prior"),
        default=0
    )
    # codename = models.CharField(
    #    _('codename'),
    #    help_text=_("for internal purporses use, must be unique"),
    #    unique=True, max_length=32)

    objects = caching.base.CachingManager()

    def get_title(self):
        return self.__unicode__()
    get_title.short_description = _("title")

    @property
    def orders(self):
        return self.order_container_set

    def reload_atom_rating(self):
        votes = Vote.objects.filter(order__container__owner=self.owner,
            is_approved=True
        )
        for atom in VoteAtom.objects.filter(klass__service=self.service):
            links = VoteLink.objects.filter(
                atom=atom,
                voteitem_votelinks_sets__in=votes.values('item')
            )
            count = links.count() or 1
            mean_atom = sum(
                [i['value'] for i in links.values('value')]) / count
            mean_atom_rating = AtomMeanRating.objects.get_or_create(
                atom=atom,
                owner=self.owner, service=self.service)
            mean_atom_rating[0].value = Decimal(str(mean_atom))
            mean_atom_rating[0].save()
        return self

    @property
    def votes(self):
        return Vote.objects.filter(
            order__container__owner=self.owner,
            is_approved=True
        )

    def get_votes_count(self):
        return self.votes.count()

    def reload_common_rating(self):
        # need to be cached
        votes = Vote.objects.filter(
            order__container__owner=self.owner,
            is_approved=True
        )
        mean_values = [i['item__mean'] for i in votes.values('item__mean')]
        mean_rating = (sum(mean_values) or 0) / (votes.count() or 1)
        if mean_rating != self.mean_rating:
            self.mean_rating = mean_rating
            self.save()
        return Decimal(str(mean_rating))

    def get_common_rating(self, reload=False):
        mean_rating = self.mean_rating
        if reload:  # or mean_rating == 0:
            mean_rating = self.reload_common_rating()
        return mean_rating

    def get_atom_ratings(self):
        return self.owner.rating_atoms.all()

    @property
    def children(self):
        return self.parent_container_set

    @property
    def item_children(self):
        return self.children.exclude(item_container_set=None)

    @property
    def addons(self):
        return self.addon_list_container_set

    def children_by_title(self):
        return Container.objects.filter(container__title__iexact=self.title)

    def get_whole_items(self):
        containers = Container.objects.filter(pk=self.pk) | self.children.all()
        return Item.objects.filter(container__in=containers)

    def __unicode__(self):
        # hotfix for recursive container set
        if self == self.container:
            return self.title

        out = self.title
        target = self
        while 1:
            if target.container is None:
                break
            out = target.container.title + '->' + out
            target = target.container
        return out

    def get_unicode_title(self):
        return self.__unicode__()

    def get_border_url(self):
        return reverse('catalog:service-page', args=(self.owner.pk, self.pk))  # self.title))

    @property
    def items(self):
        return self.item_container_set

    class Meta:
        verbose_name = _("Container")
        verbose_name_plural = _("Containers")
        ordering = ['weight', 'id', ]

    def has_parent(self):
        return bool(self.container)


class AbstractCategory(models.Model):
    """ Item's category, represents item as instance of different stuff
        for example: soda or just pizza, water-based items measure with litres
        pizza measure with counts and cocain mesures with gramms or killograms
    """
    title = models.CharField(
        _("title"), max_length=256
    )
    threshold = models.PositiveIntegerField(
        _("threshold"), default=1
    )
    rate = models.FloatField(
        _("rate")
    )
    short_title = models.CharField(
        _("short title"), max_length=16
    )
    short_rate_title = models.CharField(
        _('short rate title'), max_length=16,
        default='amount'
    )
    description = models.CharField(
        _('description'), max_length=512
    )

    def __unicode__(self):
        return "%s [%s-%s]" % (self.title, self.threshold, self.rate)

    def get_rate(self):
        value = self.rate / self.rate / self.rate
        return int(value)

    def get_title(self):
        return "[%s] %s" % (self.pk, self.title)
    get_title.short_description = _("title")

    class Meta:
        abstract = True


class ItemCategory(AbstractCategory):
    class Meta:
        verbose_name = _("Item category")
        verbose_name_plural = _("Item categories")


class AddonCategory(AbstractCategory):
    class Meta:
        verbose_name = _("Addon category")
        verbose_name_plural = _("Addon categories")

class Item(caching.base.CachingMixin, models.Model):
    """ Item provides different goods """
    title = models.CharField(_("title"), max_length=128)
    description = models.CharField(
        _("description"), max_length=1024, blank=True
    )
    container = models.ForeignKey(
        Container, default=1,
        related_name='item_container_set',
        verbose_name=_('container')
    )
    category = models.ForeignKey(
        ItemCategory, related_name='item_category_set',
        default=1,
        verbose_name=_('item category')
    )
    cost = models.DecimalField(
        _('cost'), max_digits=10,
        decimal_places=2, default=100)
    special_cost = models.DecimalField(
        _('special cost'), max_digits=10,
        decimal_places=2, default=100,
        blank=True, null=True
    )
    special_expires = models.DateTimeField(
        _("Special expires"),
        help_text=_("Date then special cost is expire for this item"),
        default=datetime.now() - timedelta(days=1),
        blank=True, null=True
    )
    is_special_active = models.BooleanField(
        _("is special active?"),
        help_text=_("is special cost for this item active?"),
        default=False
    )
    image = models.ImageField(
        _("image"), help_text=_("image for item"), blank=True, null=True,
        upload_to=lambda s, fn: ("items/%s/%s" % (s.container.id, fn)),
        max_length=256
    )
    is_special = models.BooleanField(
        _("is special?"),
        help_text=_("marks if the item is special, e.g. special dish")
    )
    created_on = models.DateTimeField(
        _('created on'), auto_now=True,
        default=datetime.now
    )
    updated_on = models.DateTimeField(
        _('updated on'), auto_now_add=True,
        default=datetime.now
    )
    weight = models.PositiveIntegerField(
        _('weight'), default=0
    )
    mass = models.PositiveIntegerField(
        _("mass"), default=None,
        null=True, blank=True,
        help_text=_('item mass')
    )
    is_deleted = models.BooleanField(
        _('is deleted'), help_text=_('deletes item'),
        default=False
    )
    # managers
    objects = ItemManager()
    whole_objects = Manager()

    def __unicode__(self):
        return self.title

    def get_generic_cost(self):
        current = self.is_special_active
        if self.special_expires:
            now = datetime.now()
            is_future = now > self.special_expires

            # saving sate
            if current and current != (not is_future):
                self.is_special_active = not is_future
                self.save()

            if self.is_special_active:
                return self.special_cost
        return self.cost

    def get_cost(self):
        cost = self.get_generic_cost()
        return cost * Decimal(str(self.category.rate))

    def get_unit_rate(self):
        """ helper for cart, retruns rate for quantity measuring """
        return self.category.rate

    class Meta:
        verbose_name = _("Item")
        verbose_name_plural = _("Items")
        ordering = ['weight', ]


class AddonList(models.Model):
    """ Provides addons for Items via its Container """
    title = models.CharField(_("title"), max_length=128)
    description = models.CharField(_("description"), max_length=1024)
    container = models.ForeignKey(
        Container, related_name='addon_list_container_set', default=1,
        verbose_name=_("container")
    )

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _("Addon List")
        verbose_name_plural = _("Addon Lists")


class Addon(models.Model):
    """ Provides single addon, for example chilly pepper """
    title = models.CharField(_("title"), max_length=128)
    description = models.CharField(_("description"), max_length=1024)
    cost = models.DecimalField(
        _('cost'), max_digits=10,
        decimal_places=2, default=100)
    list = models.ForeignKey(
        AddonList, related_name='addon_list_set', default=1,
        verbose_name=_('addon list')
    )
    is_deleted = models.BooleanField(
        _("is deleted?"), help_text=_("deletes addon"),
        default=False
    )
    category = models.ForeignKey(
        AddonCategory, related_name='addon_category_set',
        default=1,
        verbose_name=_('addon category')
    )


    objects = AddonManager()
    whole_objects = Manager()

    def __unicode__(self):
        return self.title

    def get_cost(self):
        """ item instances compatibility """
        return self.cost * Decimal(str(self.category.rate))

    def get_generic_cost(self):
        return cost * Decimal(str(self.category.rate))

    class Meta:
        verbose_name = _("Addon")
        verbose_name_plural = _("Addons")


class Special(caching.base.CachingMixin, models.Model):
    expires = models.DateTimeField(
        _("expires"), help_text=_("date and time when special expires"),
    )
    is_active = models.BooleanField(
        _('is active?'), help_text=_("if the special is active")
    )
    title = models.CharField(
        _("title"), max_length=256
    )
    description = models.CharField(
        _("description"), max_length=4096, blank=True, null=True
    )
    image = models.ImageField(
        _("image"), help_text=_("image for item"), blank=True, null=True,
        upload_to=lambda s, fn: ("specials/%s/%s" % (s.owner.id, fn)),
        max_length=256,
    )
    owner = models.ForeignKey(
        User, related_name='special_owner_set',
        verbose_name=_("owner")
    )

    objects = caching.base.CachingMixin()

    @property
    def container(self):
        """ items compatibility hack, please don't delete it """
        return self

    def __unicode__(self):
        return '%s [%s]' % (
            self.title, self.owner.service_name or service.owner.username
        )

    class Meta:
        verbose_name = _("Special")
        verbose_name_plural = _("Specials")


class OfflineClient(models.Model):
    name = models.CharField(
        _('first name'), max_length=256, null=True
    )
    email = models.EmailField(
        _('email'), max_length=256, null=True, blank=True
    )
    phone = models.CharField(
        _('phone'), help_text=_("Your contact phone"),
        max_length=15
    )
    phone2 = models.CharField(
        _('phone2'), help_text=_("Your contact phone, 2"),
        max_length=15, blank=True, null=True
    )
    city = models.ForeignKey(
        City,
        related_name='offline_client_city',
        verbose_name=_('city')
    )
    street = models.CharField(
        _('street'),
        help_text=_('street for deliver'),
        max_length=512
    )
    building = models.CharField(
        _('building'), max_length=16,
        null=True, blank=True
    )

    apartment = models.CharField(
        _('apartment'), help_text=_("apartment or office"), max_length=8
    )
    need_change = models.DecimalField(
        _('need change'), max_digits=10,
        decimal_places=2, default=100,
        null=True, blank=True
    )
    subway = models.CharField(
        _('subway'), max_length=512, null=True
    )
    code = models.CharField(
        _('code'), help_text=_('code of the domophone'), max_length=32,
        blank=True, null=True
    )

    def get_real_name(self):
        return self.name

    def get_phones(self):
        phones = ",".join(map(lambda x, y: getattr(x, y) if hasattr(x, y) else None,
            [self, self], ['phone', 'phone2'])
        )
        return phones[:-1] if phones[-1] == ',' else phones

    def get_address(self):
        return u"г. %(city)s ул. %(street)s д. %(building)s кв. %(apartment)s" % {
            'city': self.city.title,
            'street': self.street,
            'building': self.building,
            'apartment': self.apartment
        }

    @property
    def order(self):
        return get_object_or_None(self.order_offline_client_set)

    @property
    def client(self):
        return getattr(self.order, 'client')

    def __unicode__(self):
        return "%s [%s]" % (self.name, self.phone)

    class Meta:
        verbose_name = _("Offline client")
        verbose_name_plural = _("Offline clients")


class Order(models.Model):
    # items = models.ManyToManyField(Item, verbose_name=_("Items"))
    # addons = models.ManyToManyField(Addon, verbose_name=_("Addons"))
    client = models.ForeignKey(
        User, verbose_name=_("client"), related_name='order_client_set',
        blank=True, null=True
    )
    offline_client = models.ForeignKey(
        OfflineClient, verbose_name=_('offline client'),
        related_name='order_offline_client_set',
        blank=True, null=True
    )
    status = models.CharField(
        _("status"), choices=ORDER_STATUSES, max_length=16,
        default="not_confirmed",
    )
    comment = models.CharField(
        _("comment"), help_text=_("Comment to order"),
        max_length=1024, blank=True
    )
    cost = models.DecimalField(
        _('cost'), help_text=_("oreder's cost"), max_digits=10,
        decimal_places=2, default=100
    )
    discount = models.DecimalField(
        _('discount'), help_text=_("order's bonus discount"), max_digits=10,
        decimal_places=2, default=0
    )
    deliver_cost = models.DecimalField(
        _('deliver cost'), help_text=_("deliver's cost"),
        max_digits=10, decimal_places=2, default=0
    )
    deliver_date = models.DateTimeField(
        _("deliver date"), default=datetime.now,
        null=True
    )
    deliver_time = models.TimeField(
        _('deliver time'), default=datetime.now,
        null=True, blank=True
    )
    created_on = models.DateTimeField(
        _("created on"), auto_now_add=True, default=datetime.now
    )
    updated_on = models.DateTimeField(
        _("updated on"), auto_now=True, default=datetime.now
    )
    # denormalization
    service = models.ForeignKey(
        Service, related_name='order_service_set', null=True,
        verbose_name=_('service')
    )
    container = models.ForeignKey(
        Container, related_name='order_container_set',
        verbose_name=_('container')
    )
    is_paid = models.BooleanField(
        _("is payed?"), default=False
    )
    commission = models.DecimalField(
        _('commission'), help_text=_("oreder's cost"), max_digits=10,
        decimal_places=2, default=settings.COMMISSION_RATE
    )
    real_commission = models.DecimalField(
        _('real commission'), help_text=_("oreder's real commission rate"),
        max_digits=10,
        blank=True, null=True,
        decimal_places=2, default=0
    )
    promo_code = models.CharField(
        _("promo code"), 
        max_length=100, blank=True, null=True
    )

    # managers
    # objects = OrderManager()

    def __unicode__(self):
        if self.client:
            return "%s [%s]" % (self.client.username, self.status)
        return "%s [%s]" % (self.offline_client.name, self.status)

    def get_service_url(self):
        return self.container.owner.get_service_url()

    def get_service(self):
        return self.container.owner

    def get_service_name(self):
        return self.container.owner.service_name  

    def get_cost(self):
        return self.cost - self.discount

    def get_total_commission(self):
        discount = self.discount  # self.get_total_price() - self.cost
        commission = (self.get_total_price() * self.commission) - discount
        # if commission < 0:
        #    return 0
        return commission
        # Decimal(str(self.container.owner.commission))
        # settings.COMMISSION_RATE))

    def get_order_discount_score(self):
        bonus_transaction = self.bonus_order_set.filter(amount__lte=0)
        return bonus_transaction[0] if bonus_transaction else None

    @property
    def containers(self):
        """ don't mix with container,
        containers store ordered stuff (OrderContainer): items, addons
        container stores denormalization
        link to Container for better quering"""
        return self.order_container_order_set

    @property
    def is_offline(self):
        return bool(not self.client)

    def get_client(self):
        return self.client or self.offline_client

    def get_total_price(self):
        price = sum(map(
            lambda x: x['total_price'],
            self.containers.values('total_price')
        ))
        return price

    def reload_total_price(self, commit=True):
        self.cost = self.get_total_price()
        if commit:
            self.save()
        return self

    @property
    def votes(self):
        return self.vote_order_set

    def generate_vote_instance(self):
        if not self.client:
            return None

        sid = uuid1().get_hex()
        if self.votes.all():
            v = self.votes.all()[0]
            if not v.service:
                v.service = self.service
                v.save()
            return v
        else:
            v = Vote.objects.create(
                order=self, client=self.client,
                sid=sid, service=self.service
            )
            return v

    def get_online_payment_url(self):
        PROJECT_ID = settings.DO_PROJECT_ID
        amount = self.get_cost() + self.deliver_cost

        pay_url = ('https://paymentgateway.ru/?project={pid}&source={pid}'
               '&amount={amount}&nickname={nick}&order_id={order_id}')
        if self.client:
            nick = self.client.email
        url = pay_url.format(
            pid=self.container.owner.dengi_online or PROJECT_ID,
            amount=amount, nick=nick,
            order_id=self.pk
        )
        return url


    def get_item_title_list(self):
        for product in self.containers.all():
            if product.product is None:
                print product.id
        return [i.product.title for i in self.containers.all()]

    def get_item_titles(self):
        return ", ".join(self.get_item_title_list())
        
    def get_item_title_quantity_list(self):
        return ["%s (%s)" % (i.product.title, i.get_quantity()) for i in self.containers.all()]

    def get_item_title_quantity_string(self):
        return "; ".join(self.get_item_title_quantity_list())    

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")


class OrderContainer(models.Model):
    content_type = models.ForeignKey(
        ContentType,
        verbose_name=_('content type'),
        related_name="ct_set_for_%(class)s")
    object_id = models.PositiveIntegerField(verbose_name=_('object id'))
    product = generic.GenericForeignKey(
        ct_field="content_type",
        fk_field="object_id")
    parent = models.ForeignKey(
        'self',
        related_name='parent_order_container_set', null=True,
        blank=True,
        verbose_name=_('parent')
    )
    quantity = models.PositiveIntegerField(_('quantity'), default=1)
    total_price = models.DecimalField(
        _('total price'), max_digits=10,
        decimal_places=2, null=True
    )
    order = models.ForeignKey(
        Order, related_name='order_container_order_set',
        verbose_name=_('order')
    )

    def reload_price(self, commit=True):
        self.total_price = (
            self.quantity *
            self.product.cost *
            Decimal(str(self.product.category.rate))
        )
        if commit:
            self.save()
        return self

    def get_quantity(self):
        if hasattr(self.product, 'get_unit_rate'):
            return self.quantity * self.product.get_unit_rate()
        return self.quantity

    @property
    def children(self):
        return self.parent_order_container_set

    def __unicode__(self):
        f = lambda x, y: getattr(x, y) if hasattr(x, y) else ''
        return "%s [%s]" % (
            reduce(f, [self, 'product', 'title']),
            self.order.get_client().get_real_name()
        )

    class Meta:
        verbose_name = _("Order container")
        verbose_name_plural = _("Order containers")


class VoteKlass(models.Model):
    title = models.CharField(_("title"), max_length=128)
    service = models.ForeignKey(
        Service,
        related_name='voteklass_service_set', verbose_name=_('service'))

    def get_title(self):
        return "%s [%s]" % (self.title, self.service.title)
    get_title.short_description = _("title")

    def __unicode__(self):
        return self.get_title()

    class Meta:
        verbose_name = _("Vote class")
        verbose_name_plural = _("Vote classes")


class VoteAtom(models.Model):
    title = models.CharField(_("title"), max_length=128)
    klass = models.ForeignKey(
        VoteKlass, related_name='voteatom_voteklass_set',
        verbose_name=_("vote klass"))
    min = models.PositiveSmallIntegerField(
        _('min'), help_text=_("min value validate"),
        default=1, validators=[MinValueValidator(1)]
    )
    max = models.PositiveSmallIntegerField(
        _("max"), help_text=_("max value validate"),
        default=10, validators=[MaxValueValidator(255)]
    )

    def __unicode__(self):
        return "%s [%s]" % (self.title, self.klass.get_title())

    class Meta:
        verbose_name = _("Vote atom")
        verbose_name_plural = _("Vote atoms")


class VoteLink(models.Model):
    atom = models.ForeignKey(
        VoteAtom, related_name='votelink_voteatom_set',
        verbose_name=_('vote atom'))
    value = models.PositiveSmallIntegerField(
        _('value'), help_text=_("vote atom value")
    )

    def __unicode__(self):
        return "%s: %s" % (self.atom.title, self.value)

    class Meta:
        verbose_name = _("Vote link")
        verbose_name_plural = _("Vote links")


class VoteItem(models.Model):
    klass = models.ForeignKey(VoteKlass, related_name='voteitem_voteklass_set')
    links = models.ManyToManyField(
        VoteLink, related_name='voteitem_votelinks_sets',
        verbose_name=_('vote links')
    )
    mean = models.DecimalField(
        _("mean"), help_text=_("mean value"), default=0,
        max_digits=10, decimal_places=2
    )

    def reload_mean(self, save=False):
        self.mean = self.get_mean()
        if save:
            self.save()
        return self

    def get_mean(self):
        count = self.links.count() or 1  # divide by zero ;)
        values = [i['value'] for i in self.links.values('value')]
        mean = Decimal(str(float(sum(values)) / count))
        return mean

    def __unicode__(self):
        return 'voteitem %s' % self.pk

    class Meta:
        verbose_name = _("Vote item")
        verbose_name_plural = _("Vote items")


class Vote(caching.base.CachingMixin, models.Model):
    # user votes for their orders
    sid = models.CharField(
        _('sid'), help_text=_("secret id"), max_length=128
    )
    order = models.ForeignKey(
        Order, related_name='vote_order_set',
        verbose_name=_('order'))
    # denormalization, it's ok
    client = models.ForeignKey(
        User, related_name='vote_client_set',
        verbose_name=_('client'))
    is_published = models.BooleanField(_('is published?'), default=False)
    # vote items
    item = models.ForeignKey(
        VoteItem, related_name='vote_voteitem_set', blank=True,
        null=True,
        verbose_name=_('vote item')
    )
    is_proceeded = models.BooleanField(
        _("is proceeded?"), default=False
    )
    is_send = models.BooleanField(
        _("is send?"), default=False
    )
    comment = models.CharField(
        _('comment'), help_text=_("Your comment for the vote"),
        max_length=1024, default=_("No comment provided")
    )
    is_approved = models.BooleanField(
        _('is approved?'),
        help_text=_("marks if vote is approved by moderator"),
        default=False
    )
    # denormalization
    service = models.ForeignKey(
        Service, related_name='vote_service_set', null=True,
        verbose_name=_("service")
    )
    created_on = models.DateTimeField(
        _('created on'), auto_now=True,
        default=datetime.now
    )
    updated_on = models.DateTimeField(
        _('updated on'), auto_now_add=True,
        default=datetime.now
    )

    objects = caching.base.CachingManager()

    def get_avarage(self):
        if self.item:
            mean = sum([
                i['value'] for i in self.item.links.values('value')
            ])
            mean = mean / self.item.links.count()
            return int(mean)
        return 0

    def __unicode__(self):
        return "order_%s [%s]" % (self.order.pk, self.client.username)

    class Meta:
        verbose_name = _("Vote")
        verbose_name_plural = _("Votes")


class BonusTransaction(models.Model):
    # client bonus accumulator
    client = models.ForeignKey(
        User, related_name='bonus_client_set',
        verbose_name=_("client"))
    order = models.ForeignKey(
        Order, related_name='bonus_order_set',
        blank=True, null=True,
        verbose_name=_("order")
    )
    amount = models.DecimalField(
        _("amount"), help_text=_("bonus amount"), default=0,
        max_digits=10, decimal_places=2
    )
    exchange_rate = models.DecimalField(
        _("exchange rate"),
        help_text=_("real currency echange rate, measure in RUR"),
        default=str(settings.DEFAULT_EXCHANGE_RATE),
        max_digits=5, decimal_places=2
    )
    is_processed = models.BooleanField(
        _("is proccessed?"), default=False
    )
    is_discount = models.BooleanField(
        _('is discount?'), default=False
    )
    created_on = models.DateTimeField(
        _("created on"), auto_now_add=True, default=datetime.now)
    updated_on = models.DateTimeField(
        _("updated on"), auto_now=True, default=datetime.now
    )
    description = models.CharField(
        _("description"), max_length=1024, blank=True, null=True
    )

    def __unicode__(self):
        return "%s [%s]" % (self.amount, self.client.username)

    class Meta:
        verbose_name = _("Bonus transaction")
        verbose_name_plural = _("Bonus transactions")

class PaymentTransaction(models.Model):
    client = models.ForeignKey(
        User, related_name='payment_transaction_client_set',
        verbose_name=_("client"))
    order = models.ForeignKey(
        Order, related_name='payment_transaction_order_set',
        verbose_name=_('order'))
    partner = models.ForeignKey(
        User, related_name='payment_transaction_partner_set',
        verbose_name=_('partner'))
    amount = models.DecimalField(
        _('amount'), max_digits=10,
        decimal_places=2, default=0
    )
    payment_id = models.CharField(
        _('payment id'), help_text=_('service payment id'),
        max_length=512, null=True, blank=True
    )
    #
    is_processed = models.BooleanField(
        _("is processed?"), default=False)

    created_on = models.DateTimeField(
        _('created on'), auto_now=True, default=datetime.now
    )
    updated_on = models.DateTimeField(
        _('created on'), auto_now_add=True, default=datetime.now
    )

    def __unicode__(self):
        return '[%s] %s, %s' % (self.order.pk, self.client, self.partner.service_name)

    def complete(self):
        self.is_processed = True
        self.save()

    class Meta:
        verbose_name = _("Payment transaction")
        verbose_name_plural = _("Payment transactions")


def get_uuid():
    return str(uuid4())


class MailCode(models.Model):
    uuid = models.CharField(max_length=36, default=get_uuid, unique=True)

    def __unicode__(self):
        return self.uuid


# extent for django-cart without overriding existance class
class CartExtension:
    def get_total_price(self):
        total = sum(
            [
                i['quantity'] * i['unit_price']
                for i in self.cart.item_set.values(
                    'quantity', 'unit_price')
            ]
        )
        return total

    def get_total_items_count(self):
        total = sum([
            i['quantity'] for i in self.cart.item_set.values('quantity')
        ])
        return total or None

    def delete_items(self):
        """
        delete all items from cart
        original clear method is broken
        """
        self.cart.item_set.all().delete()

Cart.__bases__ = (CartExtension,) + Cart.__bases__

from apps.catalog.signals import setup_signals
setup_signals()
