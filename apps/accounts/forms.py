# -*- coding: utf-8 -*-
import re
from django import forms
from django.forms.util import ErrorList
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.forms.models import modelformset_factory
from django.forms.models import BaseModelFormSet
from django.conf import settings

from django.contrib import auth

from apps.core.helpers import get_object_or_None
from apps.core.forms import (
    TextareaForm, RequestModelForm, BruteForceCheck
)
from apps.core.models import UserSID
from apps.accounts.models import (
    TimeNDay, ContactPhoneType, Invite, ContactPhone, ContactEmail,
    DeliverCost, Schedule, TimeNDay
)
from apps.catalog.models import Service
from apps.geo.models import City, Subway, GPos

from uuid import uuid1


class LoginForm(forms.Form):
    username = forms.CharField(label=_("E-mail"))
    password = forms.CharField(
        label=_("Password"), widget=forms.PasswordInput())

    def clean(self):
        cd = self.cleaned_data
        username = cd.get('username')
        password = cd.get('password')

        user = auth.authenticate(username=username, password=password)
        if not user:
            # fail to authenticate, probabbly incorrect auth data
            msg = _("Sorry your username or/and password are invalid")
            self._errors['password1'] = ErrorList([msg])
            if 'password1' in cd:
                del cd['password1']
        if user:
			if not user.is_verified:
				msg = _("Only verified users allowed to login")
				self._errors['username'] = ErrorList([msg])

        cd['user'] = user
        return cd


class AbstractRegisterUserForm(forms.ModelForm):
    username = forms.RegexField(
        label=_('Username'),
        regex=re.compile(r'^[A-z][\w\d\._-]+\w+$'),
        max_length=32,
        min_length=3,
        #sorry but this is really need to skip pep8 notifications
        error_message=_(
            'Try to pass only latin symbols, numbers and\
underscores with your nickname'),
        help_text=_('Only latin symbols and numbers and underscore\
are allowed'),
    )
    password = forms.CharField(
        label=_("Password"), required=True,
        widget=forms.PasswordInput(), min_length=5)
    password2 = forms.CharField(
        label=_("Repeat password"), required=True,
        widget=forms.PasswordInput(), min_length=5)

    def clean_username(self):
        username = self.cleaned_data['username']
        user = get_object_or_None(User, username__iexact=username)
        if user:
            raise forms.ValidationError(_("Such username is already exists"))
        return username

    def clean(self):
        cd = self.cleaned_data
        password1 = cd.get('password')
        password2 = cd.get('password2')
        if password1 != password2:
            msg = _("Sorry passwords you entered does not match each other")
            self._errors['password'] = ErrorList([msg])
            if 'password' in cd:
                del cd['password']
        return cd

    def generic_clean_phone(self, field):
        value = self.cleaned_data[field]
        eight_match = re.match(r'^(8)\d+', value)
        if eight_match:
            value = re.sub(r'^8', '7', value)
        value = re.sub(re.compile(r'[\+\-\s]+'), '', value)
        if value:
            if not value.isdigit():
                msg = _("You can enter only numerals here")
                self._errors[field] = ErrorList([msg])
                if self.cleaned_data[field]:
                    del self.cleaned_data[field]
            user = User.objects.filter(phone=value)
            if settings.DISALLOW_NON_UNIQUE_PHONES:
	        if user:
		    msg = _("User with given phone exists, please login")
		    self._errors[field] = ErrorList([msg])
		    if self.cleaned_data[field]:
		        del self.cleaned_data[field]
        return value

    def clean_phone(self):
        return self.generic_clean_phone('phone')

    def clean_email(self):
        email = self.cleaned_data['email']
        user = get_object_or_None(User, email__iexact=email)
        if user:
            raise forms.ValidationError(
                _("User with given email exists, please login"))
        return email

    class Meta:
        model = User
        exclude = [
            'date_joined', 'is_active', 'is_superuser',
            'last_login', 'groups',
        ]


class UserRegisterForm(AbstractRegisterUserForm):
    required_css_class = 'required'
    email = forms.EmailField(label=_("E-mail"), required=True)
    phone = forms.CharField(
        label=_("phone"), required=True,
        widget=forms.HiddenInput(attrs={
            'data-order': '3',
            'data-before': 'id_city',
            'data-after': 'id_first_name',
        })
    )
    agreement = forms.BooleanField(
        label=_("User agreement"),
        initial=True, required=True,
        widget=forms.CheckboxInput(attrs={
            'data-text': _("User agreement"),
            'data-link': "/agreement/"
        })
    )
    birthday = forms.DateField(
        required=False,
        widget=forms.HiddenInput(attrs={
            'placeholder': '1970-08-27',
            'onfocus': 'this.placeholder=""',
            'data-after': 'id_agreement',
        }),
        help_text=u"Заполните это поле для получения дополнительных"
        u" бонусов в Ваш день рождения"
    )

    #def clean_username(self):
    #    username = self.cleaned_data['username']
    #    user = get_object_or_None(User, username__iexact=username)
    #    if user:
    #        raise forms.ValidationError(_("You can not choose this username"))
    #    return username

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs['request']
            del kwargs['request']

        super(UserRegisterForm, self).__init__(*args, **kwargs)
        if 'username' in self.base_fields:
            del self.base_fields['username']
            del self.fields['username']

        if hasattr(self, 'request'):
            from django.contrib.gis.utils import GeoIP
            geoip = GeoIP()
            iso_city = (
                geoip.city(
                    self.request.META.get('REMOTE_ADDR', '127.0.0.1')
                ) or {}
            ).get('city')

            city = get_object_or_None(City, iso__iexact=iso_city or '')
            if city:
                self.fields['city'].initial = city.pk

    def save(self, commit=True):
        self.instance.username = self.cleaned_data['email']
        if commit:
            self.instance.save()
        return self.instance

    class Meta:
        model = User
        fields = (
            'email',
            'first_name',
            'phone',
            'password',
            'password2',
            'city',
            'agreement',
            'birthday',
            #'middle_name', 'last_name',
            #'email', 'birthday',
            #'password', 'password2', 'phone', 'address', 'building',
            #'apartment', 'building', 'city', 'agreement',
        )
        exclude = ['is_partner', 'service', 'service_name', 'username']


class UserContactPhoneEmailSaver(object):
    def save(self, commit=True):
        types = self.data.getlist('contact_phone_type')
        phones = self.data.getlist('contact_phone')
        for (tp, phone) in zip(types, phones):
            instance = ContactPhone.objects.filter(
                phone=phone, user=self.instance
            )
            typ = get_object_or_None(ContactPhoneType, pk=tp)
            if not typ:
                continue # ignore phone with invalid type
            if not phone.isdigit():
                continue # skip phones with alphas

            if instance:
                instance[0].type = typ
                instance[0].save()
            else:
                phone = phone[0:10] if len(phone) > 11 else phone
                instance = ContactPhone.objects.create(
                    user=self.instance, phone=phone, type=typ
                )
        emails = self.data.getlist('contact_email')
        for email in emails:
            instance = ContactEmail.objects.filter(
                email=email, user=self.instance
            )
            if instance:
                instance[0].save()
            else:
                instance = ContactEmail.objects.create(
                    user=self.instance, email=email
                )        
        if commit:
            self.instance.save()
        return self.instance
          

class UserProfileEditForm(UserContactPhoneEmailSaver, forms.ModelForm):
    password = forms.CharField(widget=forms.HiddenInput(), required=False)
    building = forms.CharField(label=_("building"), required=False)
    address = forms.CharField(label=_("address"), required=False)

    def save(self, commit=True):
        password = self.cleaned_data.get('password', None)
        if password:
            self.instance.set_password(password)
        super(UserProfileEditForm, self).save(commit=commit)
        return self.instance

    class Meta:
        model = User
        fields = (
            'first_name',
            'phone',
            #'middle_name', 'last_name',
            'city',
            'address',
            'building', 'apartment', 'birthday',
        )
        widgets = {
            'birthday': forms.HiddenInput(),
        }


class PartnerProfileEditForm(UserContactPhoneEmailSaver, forms.ModelForm):
    password = forms.CharField(widget=forms.HiddenInput(), required=False)
    phone = forms.CharField(label=_("Phone"), required=True)

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs['request']
            del kwargs['request']
        super(PartnerProfileEditForm, self).__init__(*args, **kwargs)

    def generic_clean_phone(self, field):
        value = self.cleaned_data[field]
        eight_match = re.match(r'^(8)\d+', value)
        if eight_match:
            value = re.sub(r'^8', '7', value)
        value = re.sub(re.compile(r'[\+\-\s]+'), '', value)
        if value:
            if not value.isdigit():
                msg = _("You can enter only numerals here")
                self._errors[field] = ErrorList([msg])
                if self.cleaned_data[field]:
                    del self.cleaned_data[field]
            user = User.objects.filter(phone=value)
            if user and not self.request.user in user:
                msg = _("User with given phone exists, please login")
                self._errors[field] = ErrorList([msg])
                if self.cleaned_data[field]:
                    del self.cleaned_data[field]
        return value

    def clean_phone(self):
        return self.generic_clean_phone('phone')

    def clean_username(self):
        username = self.cleaned_data['username']
        user = get_object_or_None(User, username__iexact=username)
        if user:
            if user != self.request.user:
                raise forms.ValidationError(_("You can not choose this username"))
        return username

    def save(self, commit=True):
        password = self.cleaned_data.get('password', None)
        if password:
            self.instance.set_password(password)

        super(PartnerProfileEditForm, self).save(commit=commit)
        return self.instance

    class Meta:
        model = User
        fields = (
            'first_name', 'middle_name', 'last_name', 'phone',
            'email', 'username',
        )


class PartnerEditOrgForm(forms.ModelForm):
    address = forms.CharField(label=_("address"), required=False)
    def save(self, commit=True):
        super(PartnerEditOrgForm, self).save(commit)
        deliver_min, deliver_max, deliver_cost = map(
            self.data.getlist, ['deliver_min', 'deliver_max', 'deliver_cost']
        )
        for (mn, mx, cost) in zip(deliver_min, deliver_max, deliver_cost):
            dc = DeliverCost.objects.filter(min=mn, max=mx, cost=cost, user=self.instance)
            if not dc:
                DeliverCost.objects.create(
                    min=mn, max=mx, cost=cost, user=self.instance
                )
        # proceeding time
        user = self.instance
        schedule = self.instance.schedule
        if not schedule:
            schedule = Schedule.objects.create(user=user)
        for day in xrange(1, 8):
            day_enabled = self.data.get('day-%s' % day)
            since = self.data.get('day-%s-since' % day)
            until = self.data.get('day-%s-until' % day)
            # disabling day if not found it
            if day_enabled is None:
                timeday = get_object_or_None(schedule.days, weekday=day)
                if timeday:
                    timeday.is_active = False
                    timeday.save()
            if all((day, since, until)):
                timeday = get_object_or_None(schedule.days, weekday=day)
                if not timeday:
                    if day_enabled:
                        timeday = TimeNDay.objects.create(
                            weekday=day,
                            since=since, until=until,
                            schedule=schedule, is_active=True
                        )
                else:
                    timeday.since = since
                    timeday.until = until
                    if day_enabled:
                        timeday.is_active = True
                    timeday.save()
        return self.instance

    class Meta:
        model = User
        fields = (
            'service_name',
            'address',
            #'building', 'apartment',
            'avarage_deliver_time', 'avarage_deliver_cost',
            'avarage_cost', 'minimal_cost', 'logo',
            'description',
            'additional',
        )
        widgets = {
            'description': forms.Textarea()
        }

    class Media:
        js = (
            '/media/js/tiny_mce/tiny_mce_src.js',
            '/media/js/textareas_partner.js'
        )




class RegisterPartnerForm1(forms.ModelForm):
    required_css_class = 'required'
    service_name = forms.CharField(
        required=True, label=_("Service name"),
        help_text=_("Your service name"))
    #site = forms.CharField(
    #    required=True, label=_("Site address"),
    #    help_text=_("Your web site address")
    #)
    address = forms.CharField(
        required=True, label=_("Address"),
        help_text=_("Address where are you located"))
    avarage_cost = forms.CharField(
        required=True, label=_("Avarage cost"),
        help_text=_("Avarage cost for purchase"))
    avarage_deliver_cost = forms.CharField(
        required=True, label=_("Avarage deliver cost"),
        help_text=_("Avarage deliver cost for customers"))
    avarage_deliver_time = forms.CharField(
        required=True, label=_("Avarage deliver time"),
        help_text=_("Avarage deliver time for customers"))
    service = forms.ModelChoiceField(queryset=Service.objects)
    city = forms.ModelChoiceField(queryset=City.objects)
    subway = forms.ModelChoiceField(queryset=Subway.objects)
    apartment = forms.CharField(label=_("Office"), required=False)

    class Meta:
        model = User
        fields = (
            'service_name', 'service', 'city', 'subway', 'address',
            #'building',
            'apartment',
            'avarage_cost', 'avarage_deliver_cost', 'avarage_deliver_time',
        )


class RegisterPartnerForm2(AbstractRegisterUserForm, TextareaForm):
    real_name = forms.CharField(
        required=True, label=_("Real name"),
        help_text=_("Your surname, forname and middle name:\
            <i>Ivanov Ivan Ivanich</i>")
    )
    contact_phone = forms.CharField(
        required=True, label=_("Contact phone"),
        help_text=_("Your contact phone")
        )
    contact_phone_type = forms.ModelChoiceField(
        queryset=ContactPhoneType.objects, required=True,
        help_text=_("May be the same as phone"))
    contact_email = forms.EmailField(
        required=True, label=_("Contact email"),
        help_text=_("May be the same as common email")
    )

    phone = forms.CharField(label=_("Phone"), required=True)

    def clean_contact_phone(self):
        return self.generic_clean_phone('contact_phone')

    def clean_real_name(self):
        real_name = self.cleaned_data['real_name']
        # clean whitespaces, replace more than one spaces
        real_name = re.sub(re.compile('\s+'), ' ', real_name)
        # trim whitespace at the end if exists
        real_name = re.sub(re.compile('\s$'), '', real_name)
        # its equivalent to
        # real_name = real_name[:-1] if real_name[-1] == ' ' else real_name
        # use whatever you like
        if len(real_name.split(' ')) < 3:
            raise forms.ValidationError(
                _("Please input your surname,\
                    in the follow direction: surname, forename middle name\
                    dividing by space"
                )
            )
        return real_name

    def save(self, *args, **kwargs):  # commit=True as default args
        last_name, first_name, middle_name = \
            self.cleaned_data['real_name'].split(' ')
        self.instance.first_name = first_name
        self.instance.last_name = last_name
        self.instance.middle_name = middle_name
        super(RegisterPartnerForm2, self).save(*args, **kwargs)

    class Meta:
        model = User
        # contact_phone, contact_email saves in separate model insatnce
        # phone with user instance uses might be used as notification
        # phone
        fields = (
            'real_name', 'contact_phone_type', 'contact_phone', 'phone',
            'contact_email', 'email', 'username', 'password', 'password2',
            'description'
        )
        widgets = {
            'description': forms.Textarea()
        }


class BaseTimeNDayFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super(BaseTimeNDayFormSet, self).__init__(*args, **kwargs)

TimeNDayFormset = modelformset_factory(
    TimeNDay, formset=BaseTimeNDayFormSet,
    fields=('weekday', 'since', 'until'), extra=7
)

class InviteRegisterForm(UserRegisterForm):
    password = forms.CharField(
        label=_("Password"), required=True,
        widget=forms.PasswordInput())

    def save(self, commit):
        self.instance.email = self.invite.email
        self.instance.username = self.invite.email
        if commit:
            self.instance.save()
        return self.instance

    def clean(self):
        cd = self.cleaned_data
        email = self.invite.email
        exists = User.objects.filter(email__iexact=email)
        if exists:
            msg = _(
                "This email account was registered already, please login"
            )
            self._errors['first_name'] = ErrorList([msg])
        return cd

    def __init__(self, *args, **kwargs):
        if 'invite' in kwargs:
            self.invite = kwargs['invite']
            del kwargs['invite']
        super(InviteRegisterForm, self).__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = (
            #'email',
            'first_name',
            'phone',
            'password',
            'password2',
            'city',
            'agreement',
            'birthday',

            #'username', 'first_name', 'middle_name', 'last_name',
            #'password', 'password2', 'phone', 'address', 'building',
            #'apartment', 'building', 'city'
        )

class SendInviteForm(RequestModelForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        if email:
            invite = Invite.objects.filter(email__iexact=email)
            user = User.objects.filter(email__iexact=email)
            if invite or user:
                raise forms.ValidationError(_("This user had been already invited, sorry"))
        return email

    def clean(self):
        cd = self.cleaned_data
        user = self.request.user
        if settings.INVITES_LIMIT_ENABLE:
            if user.invites >= settings.MAX_INVITES_COUNT:
                msg = _("Your are out of invite limit, sorry for that :)")
                self._errors['email'] = ErrorList([msg])
                if 'email' in cd:
                    del cd['email']
        return cd

    def save(self, commit=True):
        super(SendInviteForm, self).save(commit=commit)
        self.instance.sid = uuid1().get_hex()
        self.instance.sender = self.request.user

    class Meta:
        model = Invite
        fields = ('email', )


class AccountSetGCoordinates(forms.ModelForm):
    lat = forms.FloatField(widget=forms.HiddenInput(), required=False)
    lng = forms.FloatField(widget=forms.HiddenInput(), required=False)
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    description = forms.CharField(widget=forms.HiddenInput(), required=False)

    def save(self, commit=True):
        lats = self.data.getlist('lat')
        lngs = self.data.getlist('lng')
        ids = self.data.getlist('id')
        descriptions = self.data.getlist('description')

        from itertools import chain
        if not all(chain(*(lats, lngs))):
            return self.instance

        #saving instances
        for (pk, lat, lng, description) in zip(ids, lats, lngs, descriptions):
            position = get_object_or_None(GPos, pk=pk)
            position.lat = lat
            position.lng = lng
            position.description = description
            position.user = self.instance
            position.save()

        #new coords

        for (lat, lng, description) in zip(
            lats[len(ids):], lngs[len(ids):], descriptions[len(ids):]
        ):
            user = self.instance
            if any((lat, lng)):
                position = GPos.objects.create(
                    lat=lat, lng=lng, description=description, user=user
                )

        if commit:
            self.instance.save()
        return self.instance

    class Meta:
        model = User
        fields = []
        widgets = {
            'glng': forms.HiddenInput,
            'glat': forms.HiddenInput,
        }

class PasswordRestoreInitiateForm(forms.Form):
    email = forms.CharField(
        label=_("Email"), help_text=_("Your email")
    )

    def clean_email(self):
        email = self.cleaned_data['email'] or None
        users = User.objects.filter(email__iexact=email)
        if not users:
            raise forms.ValidationError(
                _("Users with given email does not exists")
            )
        self.cleaned_data['users'] = users
        return email


class PasswordRestoreForm(RequestModelForm, BruteForceCheck):
    password = forms.CharField(
        label=_("Password"), widget=forms.PasswordInput()
    )
    password2 = forms.CharField(
        label=_("Password repeat"), widget=forms.PasswordInput()
    )

    def clean(self):
        cd = self.cleaned_data
        password = cd['password']
        password2 = cd['password2']
        if all((password, password2) or (None, )):
            if password != password2:
                msg = _("Passwords don't match")
        return cd

    def save(self, commit=True):
        user = self.instance.user
        user.set_password(self.cleaned_data['password'])
        user.save()
        if commit:
            self.instance.expired = True
            self.instance.save()
            instance = self.instance
        else:
            instance.expired = True
            instance = super(Password, self).save(commit=commit)

        return instance

    class Meta:
        model = UserSID
        exclude = ('expired_date', 'expired', 'sid', 'user')
