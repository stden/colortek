# -*- coding: utf-8 -*-
import sys
import re

from functools import partial
from datetime import datetime, timedelta
from django import forms
from django.forms.util import ErrorList
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from apps.catalog.models import (
    Container, Item, AddonList, Addon, Order, Vote, VoteKlass,
    VoteAtom, VoteLink, VoteItem, BonusTransaction,
    OfflineClient, Special, OrderContainer, Category,
    ItemCategory
)
from apps.sms.models import SMSLogger
from django.core.mail import send_mail
from apps.core.forms import TextareaForm, RequestModelForm
from apps.core.helpers import (
    get_object_or_None, get_model_content_type
)
from apps.geo.models import City
from django.contrib import messages

from cart import Cart, ItemAlreadyExists, ItemDoesNotExist
from decimal import Decimal
from uuid import uuid1


class AddContainerForm(RequestModelForm, TextareaForm):
    next = forms.CharField(required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(AddContainerForm, self).__init__(*args, **kwargs)
        containers = Container.objects.filter(owner=self.request.user)
        if self.instance:
            containers = containers.exclude(pk=self.instance.pk)
        self.fields['container'].queryset = containers

    def clean_container(self):
        container = self.cleaned_data['container']
        if not container:
            return container
        if (self.instance == container) and self.instance is not None:
            raise forms.ValidationError(
                _("You can not assign container on itself")
            )
        return container

    class Meta:
        model = Container
        exclude = ['owner', 'service', 'mean_rating', ]
        widgets = {
            'description': forms.Textarea()
        }


class AddItemForm(RequestModelForm, TextareaForm):
    class Meta:
        model = Item
        exclude = []
        widgets = {
            'description': forms.Textarea()
        }


class AddAddonForm(RequestModelForm, TextareaForm):
    container = forms.ModelChoiceField(
        queryset=Container.objects,
        widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        super(AddAddonForm, self).__init__(*args, **kwargs)
        if not hasattr(self, 'request'):
            raise ImproperlyConfigured("request kwarg is required to proceed")

        #if not all(self.data or (None,)):
        #self.base_fields['container'].queryset = Container.objects.filter(
        #    owner=self.request.user
        #)
        self.fields['container'].queryset = Container.objects.filter(
            owner=self.request.user
        )

    def save(self, commit=True):
        container = self.cleaned_data['container']
        addon_list = AddonList.objects.get_or_create(container=container)
        addon_list = addon_list[0]
        if not addon_list.title:
            addon_list.title = container.title
            addon_list.save()
        self.instance.list = addon_list
        super(AddAddonForm, self).save(commit=commit)
        return self.instance

    class Meta:
        model = Addon
        exclude = ['list', 'description', 'is_deleted']


class AddAddonToCartForm(forms.Form):
    addons = forms.ModelMultipleChoiceField(queryset=Addon.objects)

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs['request']
            del kwargs['request']
        super(AddAddonToCartForm, self).__init__(*args, **kwargs)
        if any(self.data or [None,]):
            if not hasattr(self, 'request'):
                raise ImproperlyConfigured("You should pass 'request' object to proceed")

    def clean_addons(self):
        addons = self.cleaned_data['addons']
        cart = Cart(self.request)
        item_ct = get_model_content_type(Item)
        product = cart.cart.item_set.filter(content_type=item_ct)
        if not product:
            raise forms.ValidationError(_("You can not order addons without any items"))
        owner = product[0].product.container.owner
        for addon in addons:
            if owner != addon.list.container.owner:
                #messages.info(
                #    self.request,
                #    _("You can not order stuff with"
                #    "another services or providers")
                #)
                raise forms.ValidationError(_("You can not choose addons of the side services"))
        return addons

    def save(self):
        addons = self.cleaned_data['addons']
        addon_ct = get_model_content_type(Addon)
        cart = Cart(self.request)
        for addon in addons:
            quantity = self.data.get('quantity-%s' % addon.pk, 0)
            addon_pk = addon.pk
            try:
                if int(quantity) > 0:
                    cart.add(addon, addon.get_cost(), quantity)
            except ItemAlreadyExists:
                cart_item = cart.cart.item_set.get(
                    object_id=addon_pk, content_type=addon_ct
                )
                cart_item.quantity += int(quantity)
                cart_item.save()
        return

class OrderForm(RequestModelForm, TextareaForm):
    agree = forms.BooleanField(
        label=_("Service terms agreement"), required=True
    )
    discount = forms.IntegerField(
        required=False,
        label=_("discount"),
        help_text=_("up to 10% you can payed by your bonus points"),
        initial=0,
    )
    payment_redirect = forms.ChoiceField(
        label=_("Payment redirect"), choices=(
            ('deliver', _("delivery boy")),
            ('online', _("online payment"))
        ), initial='deliver', required=False
    )
    name = forms.CharField(label=_("Name"))
    phone = forms.CharField(label=_("Phone"))
    phone2 = forms.CharField(label=_("Phone2"), required=False)
    city = forms.ModelChoiceField(queryset=City.objects)
    street = forms.CharField(label=_("Street"))
    building = forms.CharField(label=_("Building"))
    building_attr = forms.CharField(label=_("Building attr"), required=False)
    apartment = forms.CharField(label=_("Apartment"), required=True)
    need_change = forms.IntegerField(label=_("Need change"), required=False)
    deliver_date = forms.DateField(label=_("Deliver Date"), required=False)
    deliver_time = forms.TimeField(label=_("Deliver Time"), required=False)
    deliver_cost = forms.IntegerField(
        widget=forms.HiddenInput(), required=True
    )
    subway = forms.CharField(label=_("Subway"), required=False)
    code = forms.CharField(label=_("Code"), required=False)
    is_register = forms.BooleanField(required=False)
    email = forms.EmailField(required=False)

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not phone.isdigit():
            raise forms.ValidationError(_("Only numbers allowed"))
        return phone

    """
    def clean_phone2(self):
        phone = self.cleaned_data['phone2']
        if not phone.isdigit():
            raise forms.ValidationError(_("Only numbers allowed"))
        return phone
    """

    def clean_deliver_date(self):
        deliver_date = self.cleaned_data['deliver_date']
        if deliver_date:
            now = datetime.now()
            offset = datetime(now.year, now.month, now.day) - timedelta(days=1)
            dd = datetime(deliver_date.year, deliver_date.month, deliver_date.day)
            if dd <= offset:
                raise forms.ValidationError(_("You can not order in the past"))
        return deliver_date


    def clean_deliver_cost(self):
        deliver_cost = self.cleaned_data['deliver_cost']
        _cart = Cart(self.request)
        item_ct = get_model_content_type(Item)
        items = _cart.cart.item_set.filter(content_type=item_ct)
        if items:
            owner = items[0].product.container.owner
            dcost = owner.get_deliver_cost(_cart.get_total_price())
            if dcost > deliver_cost:
                raise forms.ValidationError(
                    _("Deliver cost should not be lower than"
                    "'%s' value") % dcost
                )
        return deliver_cost

    def clean_need_change(self):
        need_change = self.cleaned_data['need_change']
        if need_change < 0:
            raise forms.ValidationError(_("You may pass only positive amount of money"))
        return need_change

    def clean_email(self):
        email = self.cleaned_data['email']
        user = User.objects.filter(email__iexact=email)
        if user and self.request.user not in user:
            raise forms.ValidationError(_("User with such email exists, please login"))
        return email

    def clean_discount(self):
        discount = self.cleaned_data['discount'] or None
        if discount:
            if discount > self.request.user.bonus_score:
                raise forms.ValidationError(
                    _("You can not spend more bonus points than you have")
                )
            cart = Cart(self.request)
            price = cart.get_total_price()
            threshold = settings.DEFAULT_BONUS_PAY_THRESHOLD_AMOUNT
            exchange = settings.DEFAULT_EXCHANGE_RATE

            msg = _(
                """Maxium discount you can get
                is '%(percent)s' of '%(amount)s is %(max)s'""") % {
                'percent': str(threshold * 100) + '%',
                'amount': price,
                'max': str(round(price * Decimal(str(threshold))))
            }
            if Decimal(str(discount * exchange)) > (price * Decimal(str(threshold))):
                raise forms.ValidationError(msg)
            if discount < 0:
                raise forms.ValidationError(
                    _("You can not proceed negative values for discount")
                )
        return discount

    def clean(self):
        # deliver_date, deliver_time
        dd = self.cleaned_data.get('deliver_date', None)
        dt = self.cleaned_data.get('deliver_time', None)

        cart = Cart(self.request)
        total_price = cart.get_total_price()
        item_ct = get_model_content_type(Item)
        item = cart.cart.item_set.filter(content_type=item_ct)

        minimal_cost = item[0].product.container.owner.minimal_cost if len(item) else 0
        if total_price < minimal_cost and total_price > 0:
            msg = _("Minimal cost for order is '%s' for this service, "
            "you should get more items to process") % minimal_cost
            self._errors['name'] = ErrorList([msg])

        if all((dd, dt)):
            now = datetime.now()
            offset = now + timedelta(minutes=30)
            st = datetime(dd.year, dd.month, dd.day, dt.hour, dt.minute, dt.second)
            if st <= offset:
                msg = _("You can not order in the past")
                self._errors['deliver_date'] = ErrorList([msg])

        return self.cleaned_data

    def save_offline_client(self):
        import os
        fields = [
            'name', 'phone', 'phone2', 'city', 'street',
            'apartment', 'need_change', 'subway', 'code',
            'email'
        ]
        building = os.path.join(
            self.cleaned_data['building'], self.cleaned_data['building_attr'] or ''
        )
        building = building[:-1] if building[-1] == '/' else building
        building = building[0:15] if len(building) > 16 else building

        data = {}
        for field in fields:
            data.update({field: self.cleaned_data.get(field)})
        data.update({'building': building})
        #todo: validate data before create
        instance = OfflineClient.objects.create(**data)
        # saving user
        is_authenticated = reduce(
            lambda x,y: getattr(x, y) if hasattr(x, y) else None,
            [self.request, 'user', 'is_authenticated']
        )

        if is_authenticated():
            user = self.request.user
            fields = ['apartment', 'building']
            commit = False
            for field in fields:
                if not getattr(user, field):
                    setattr(user, field, data[field])
                    commit = True

            if data['street']:
                user.address = data['street']
                commit = True

            if commit:
                user.save()
        return instance

    def save(self, commit=True):
        """ if not commit, please add items manual """
        instance = self.instance
        cart = Cart(self.request)
        discount = self.cleaned_data['discount'] or 0
        exchange = settings.DEFAULT_EXCHANGE_RATE
        total_price = cart.get_total_price()

        instance.cost = total_price  # - Decimal(str(discount * exchange))
        instance.discount = Decimal(str(discount * exchange))

        new_user = None
        if all((self.cleaned_data['is_register'], self.cleaned_data['email'])):
            new_user = User.objects.create(
                email=self.cleaned_data['email'],
                username=self.cleaned_data['email'],
                phone=self.cleaned_data['phone']
            )
            new_password = uuid1().hex[:6]
            new_user.set_password(new_password)
            new_user.save()

            email = new_user.email
            link = settings.SITE_URL + '/login'
            login = new_user.username

            send_mail(
                subject=unicode(_(u"Регистрация на uzevezu.ru")),
                message=unicode(settings.ORDER_REGISTER_MESSAGE % {
                    'password': new_password,
                    'login': login,
                    'link': link
                }),
                from_email=settings.EMAIL_FROM,
                recipient_list=[email, ],
                fail_silently=True
            )
        if self.request.user.is_authenticated() or new_user:
            instance.client = new_user or self.request.user
        super(OrderForm, self).save(commit)

        is_authenticated = reduce(
            lambda x,y: getattr(x, y) if hasattr(x, y) else None,
            [self.request, 'user', 'is_authenticated']
        )
        if not is_authenticated():
            # send sms
            sms = SMSLogger.objects.create(
                provider='disms',
                phone=self.cleaned_data['phone'],
                text=settings.ANONYMOUS_ORDER_MESSAGE
            )
            sms.send_message()
            sms.save()
            return self.instance

        # reloading bonus score
        self.request.user.reload_bonus_score(rebuild=True)
        return self.instance

    class Meta:
        model = Order
        exclude = [
            'cost', 'client', 'items', 'status', 'service', 'container',
            'addons', 'offline_client', 'is_paid', 'commission',
            'real_commission',
        ]
        widgets = {
            'comment': forms.Textarea()
        }


class OrderUpdateForm(forms.ModelForm):
    def save(self, commit=True):
        quantities, containers = map(self.data.getlist, ['quantity', 'container'])
        for quantity, container in zip(quantities, containers):
            order_container = get_object_or_None(OrderContainer, pk=container)
            if order_container and quantity.isdigit():
                order_container.quantity = int(quantity)
                order_container.save()

        if commit:
            self.instance.save()
        return self.instance

    class Meta:
        model = Order
        fields = ('status', 'comment')


class SearchPartnerOrderForm(forms.ModelForm):
    comment = forms.CharField(required=False)
    cost = forms.CharField(required=False)

    class Meta:
        model = Order
        exclude = ['service', 'container']


class CartItemAddForm(forms.Form):
    item = forms.IntegerField(required=True)
    quantity = forms.IntegerField(initial=1)

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs['request']
            del kwargs['request']
        super(CartItemAddForm, self).__init__(*args, **kwargs)

        if all(self.data or (None, )):
            if not hasattr(self, 'request'):
                raise ImproperlyConfigured(
                    "You should pass request instance within form initialization"
                )

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity < 0:
            raise forms.ValidationError(_("Quantity should be possitive"))
        return quantity

    def clean_item(self):
        item = self.cleaned_data['item']
        item_instance = get_object_or_None(Item, pk=item)
        if not item_instance:
            raise forms.ValidationError(_("No such item found"))
        return item

    def clean(self):
        cd = self.cleaned_data
        item = self.cleaned_data.get('item') or None
        item_instance = get_object_or_None(Item, pk=item)

        if item_instance:
            cart = Cart(self.request)
            item_ct = get_model_content_type(Item)
            items = cart.cart.item_set.filter(content_type=item_ct)
            if items:
                cart_item = items[0].product
                if cart_item.container.owner != item_instance.container.owner:
                    dst = item_instance.container.owner.service_name or "-"
                    src = cart_item.container.owner.service_name or "-"

                    msg = _("You can not add multiply service items")
                    if settings.PARTNER_ORDER_ITEM_MESSAGES_WARNING:
                        messages.warning(
                            self.request,
                            _('You\'re trying to stock items from "%(dst)s" delivery. '
                            'Do you want to cleanse "%(src)s" items?') % {
                                'dst': dst,
                                'src': src
                            },
                            extra_tags='cleanse_cart'
                        )

                    self._errors['item'] = ErrorList([msg, 400])
                    if 'item' in cd:
                        del cd['item']
        else:
            msg = _("No item was found with such id")
            self._errors['item'] = ErrorList([msg])
            if 'item' in cd:
                del cd['item']
        return cd


class AddSpecialForm(forms.ModelForm):
    class Meta:
        model = Special
        widgets = {
            'description': forms.Textarea()
        }
        exclude = ['owner', ]
    class Media:
        js = (
            '/media/js/tiny_mce/tiny_mce_src.js',
            '/media/js/textareas.js'
        )


class VoteOrderForm(RequestModelForm):
    def __init__(self, *args, **kwargs):
        super(VoteOrderForm, self).__init__(*args, **kwargs)
        #if self.data:
        #    if not hasattr(self, 'request'):
        #        raise ImproperlyConfigured(
        #    "Please pass the request to proceed")
        # adding fields for voting, proceeding request data
        #instance = self.instance
        #atoms = VoteAtom.objects.filter(klass__service=instance.service)
        #for atom in atoms:
        #    self.fields['atom_%s' % atom.pk] = forms.CharField(
        #        label=_('%s' % atom.title), required=True
        #    )

    def clean(self):
        cd = self.cleaned_data

        #clean vote atoms
        atoms = [i for i in cd.keys() if 'atom_' in i]
        for atom in atoms:
            value = int(cd[atom])
            atom = VoteAtom.objects.get(id=atom.replace('atom_', ''))
            if value < int(atom.min) or value > int(atom.max):
                msg = _(
                    "You should use values in range of '%(min)s'..'%(max)s'"
                ) % {
                    'min': atom.min,
                    'max': atom.max
                }
                self._errors['atom_%s' % atom.pk] = ErrorList([msg])
                if atom in cd:
                    del cd[atom]
        return cd

    def save(self, commit=True):
        self.instance.is_published = True
        fields = [i for i in self.fields.keys() if 'atom_' in i]
        klass = VoteKlass.objects.get(service=self.instance.service)

        vote = VoteItem.objects.create(klass=klass)
        self.instance.item = vote
        for field in fields:
            value = self.cleaned_data[field]
            atom = VoteAtom.objects.get(pk=field.replace('atom_', ''))
            link = VoteLink.objects.create(atom=atom, value=value)
            vote.links.add(link)
        vote.mean = vote.get_mean()
        vote.save()

        super(VoteOrderForm, self).save(commit=commit)
        return self.instance

    class Meta:
        model = Vote
        exclude = [
            'sid', 'service', 'order',
            'client', 'item', 'is_published',
            'is_approved', 'is_proceeded', 'is_send',
        ]
        widgets = {
            'comment': forms.Textarea()
        }

    class Media:
        js = (
            '/media/js/tiny_mce/tiny_mce_src.js',
            '/media/js/textareas.js',
        )


# helpers
def generate_vote_form(instance, Obj):
    atoms = VoteAtom.objects.filter(klass__service=instance.service).distinct()
    fields = ['atom_%s' % atom.pk for atom in atoms]

    # cleanse old atoms links
    for (key, item) in Obj.base_fields.items():
        if not key in fields and 'atom' in key:
            del Obj.base_fields[key]
    if hasattr(Obj, 'fields'):
        for (key, item) in Obj.fields.items():
            if not key in fields and 'atom' in key:
                del Obj.fields[key]

    for atom in atoms:
        Obj.base_fields['atom_%s' % atom.pk] = forms.ChoiceField(
            label=_(atom.title), required=True,
            choices=map(lambda x:(x, ""), xrange(atom.min, atom.max+1)),
            widget=forms.widgets.RadioSelect(
                attrs={'class': 'rating'}
            )
        )
    return Obj

class CoordinatesForm(forms.Form):
    lat = forms.FloatField(required=True)
    lng = forms.FloatField(required=True)


class ImportCSVForm(forms.Form):
    required_class = 'required'
    data = forms.FileField(label=_('import file'))
    pictures =  forms.FileField(
        label=_("pictures file"),
        help_text=_("only zip allowed"),
        required=False
    )

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs['request']
            del kwargs['request']
            self.stats = {'created': 0,  'updated': 0, 'category_created': 0}
        super(ImportCSVForm, self).__init__(*args, **kwargs)

    def clean_data(self):
        import csv
        data = self.files['data']
        try:
            reader = csv.reader(data)
            row = reader.next()
        except (csv.Error):
            raise forms.ValidationError(_("You downloaded non-csv file, please use proper format"))
        return data

    def clean_pictures(self):
        import zipfile
        pictures = self.files.get('pictures', None)
        if not pictures:
            return pictures
        try:
            handler = zipfile.ZipFile(pictures)
        except zipfile.BadZipfile:
            raise forms.ValidationError(
                _(
                    "Sorry, but file you want to download"
                    "is not zip file, please user proper format"
                )
            )
        return pictures

    def save(self):
        import csv
        from csvhelper import save_item_image

        reader = csv.reader(self.files['data'], delimiter=',', quotechar='"')
        r = re.compile('^\ |"')
        trim = partial(re.sub, r, '')
        broken_csv = 0
        pictures = self.files.get('pictures', None)

        stats = self.stats
        for row in reader:
            # 1 == category
            # 2 == container (parent)
            # 3 == container (source) (could be None)
            # 4 == item title
            # 5 == item weight, could be None
            # 6 == item description, could be None
            # 7 == cost
            # 8 == item category
            # 9 == image path

            if len(row) < 9:
                broken_csv += 1
                continue
            if broken_csv > 10:
                # not csv file
                break

            category = get_object_or_None(
                Category, title__iexact=trim(row[0]).decode('utf-8')
            )
            if not category:
                continue # skip if category title passed flaw

            _parent = trim(row[1])
            _source = trim(row[2])
            source = _source if _source != 'None' else _parent #_source == 'None'
            parent = _parent if _source != _parent else None

            parent_container = Container.objects.filter(
                title__iexact=parent,
                owner=self.request.user,
                container=None
            )
            parent_container = parent_container[0] if parent_container else None

            if not parent_container and parent:
                parent_container = Container.objects.create(
                    title=parent, category=category,
                    owner=self.request.user,
                    service=self.request.user.service,
                )
                stats['category_created'] += 1
            #
            source_container = Container.objects.filter(
                title__iexact=source,
                owner=self.request.user,
                container__container=None
            )

            source_container = source_container[0] if source_container else None
            if not source_container:
                source_container = Container.objects.create(
                    container=parent_container,
                    title=source,
                    category=category,
                    owner=self.request.user,
                    service=self.request.user.service
                )
                stats['category_created'] += 1
            #
            item_title = trim(row[3]).decode('utf-8')
            item_cost = Decimal(trim(row[6]))
            item_description = trim(row[5]).decode('utf-8') if 'None' not in row[5] else ''
            item_weight = int(trim(row[4])) if trim(row[4]).isdigit() else 0
            item_category = int(trim(row[7])) if trim(row[7]).isdigit() else 1
            picture_path = trim(row[8])
            item_category = get_object_or_None(ItemCategory, pk=item_category)
            item = get_object_or_None(
                Item,
                title__iexact=item_title,
                container=source_container
            )
            if not item:
                # create new instance
                item = Item.objects.create(
                    title=item_title,
                    container=source_container,
                    cost=item_cost,
                    weight=item_weight,
                    description=item_description,
                )
                stats['created'] += 1
                if item_category:
                    item.category = item_category
                item.image = save_item_image(pictures, item, picture_path)
                item.save()
            else:
                # updating instance
                item.cost = item_cost
                item.weight = item_weight
                item.description = item_description
                stats['updated'] += 1
                if item_category:
                    item.category = item_category
                item.image = save_item_image(pictures, item, picture_path)
                item.save()
