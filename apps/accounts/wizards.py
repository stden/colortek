# coding: utf-8
from datetime import datetime

from django.contrib.formtools.wizard.views import SessionWizardView
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from apps.core.handlers import handle_uploaded_file
from apps.core.helpers import get_object_or_None
from apps.accounts.models import (
    ContactPhone, ContactEmail, Schedule,
    TimeNDay, ContactPhoneType
)
from apps.accounts.forms import RegisterPartnerForm1, RegisterPartnerForm2


#wizards
class RegisterPartnerWizard(SessionWizardView):
    file_storage = FileSystemStorage()
    #template_name = 'accounts/register_partner.html'

    def get_template_names(self):
        if self.steps.current == '0':
            return 'accounts/register_partner_step1.html'
        if self.steps.current == '1':
            return 'accounts/register_partner_step2.html'
        return 'accounts/register_partner.html'

    def process_step(self, form):
        return self.get_form_step_data(form)

    def done(self, form_list, **kwargs):
        user_data = form_list[0].cleaned_data
        # MANUAL ATTRS SAVE WAY:
        # be careful fields for user attribute saving is not set automatical
        # so set it here
        #fields = (
        #    'subway', 'service_name', 'site',
        #    'city', 'address', 'building', 'apartment',
        #    'avarage_deliver_cost', 'avarage_cost', 'avarage_deliver_time', 'service'
        #)
        # AUTOMATICAL SAVE ONE:
        fields = RegisterPartnerForm1.Meta.fields

        user_form = form_list[1]

        #contact_phone = user_form.cleaned_data['contact_phone']
        #contact_phone_type = user_form.cleaned_data['contact_phone_type']
        #contact_email = user_form.cleaned_data['contact_email']

        user_form.save(commit=False)
        user = user_form.instance
        user.is_partner = True
        user.service = user_data['service']
        for field in fields:
            setattr(user, field, user_data[field])

        user.set_password(user_form.cleaned_data['password'])
        user.save()

        # generating contact phones
        _types = user_form.data.getlist('1-contact_phone_type')
        _contact_phones = user_form.data.getlist('1-contact_phone')
        safe_type = 1

        for (idx, contact_phone) in enumerate(_contact_phones):
            _type = _types[idx] if len(_types) == len(_contact_phones) else safe_type
            contact_phone_type = get_object_or_None(ContactPhoneType, pk=_type)
            if contact_phone_type:
                contact_phone = ContactPhone.objects.create(
                type=contact_phone_type,
                phone=contact_phone, user=user)

        # generating contact emails
        for contact_email in user_form.data.getlist('1-contact_email'):
            cemail = ContactEmail.objects.create(
                email=contact_email,
                user=user

            )
        schedule = Schedule.objects.create(user=user)

        step = 0
        time_form = form_list[step]

        for day in xrange(1, 8):
            day_enabled = time_form.data.get('%s-day-%s' % (step, day))
            if day_enabled:
                since = time_form.data.get(
                    '%s-day-%s_since' % (step, day), '10:00'
                )
                until = time_form.data.get(
                    '%s-day-%s_until' % (step, day), '21:00'
                )
                try:
                    since = datetime.strptime(since, '%H:%M').time()
                    until = datetime.strptime(until, '%H:%M').time()
                    instance = TimeNDay.objects.create(
                        since=since,
                        until=until,
                        weekday=day, schedule=schedule
                    )
                except ValueError:
                    pass #no use
        #contact_email = ContactEmail.objects.create(
        #    email=contact_email,
        #    user=user)
        #timeformset = form_list[0]
        #
        #for form in timeformset.forms:
        #    if form.is_valid():
        #        instance = form.save(commit=False)
        #        #saving only first day element, other ignore
        #        if not schedule.days.filter(weekday=instance.weekday):
        #            instance.schedule = schedule
        #            instance.save()

        return redirect('accounts:register-success')
