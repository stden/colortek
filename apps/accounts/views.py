# Create your views here.
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from apps.core.helpers import render_to
from apps.accounts.models import (
    Invite, ContactPhone, ContactEmail, DeliverCost, Verification
)
from apps.accounts.forms import (
    LoginForm, UserRegisterForm, RegisterPartnerForm1, RegisterPartnerForm2,
    TimeNDayFormset, SendInviteForm, InviteRegisterForm, UserProfileEditForm,
    PartnerProfileEditForm, PartnerEditOrgForm,
    AccountSetGCoordinates, PasswordRestoreInitiateForm, PasswordRestoreForm
)
from apps.accounts.wizards import RegisterPartnerWizard
from apps.accounts.decorators import (
    partner_required, check_invite, phone_owner, email_owner, prevent_bruteforce
)
from apps.core.helpers import get_object_or_None
from django.shortcuts import get_object_or_404

from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.mail import send_mail, EmailMultiAlternatives as EmailMulti
from django.utils.translation import ugettext_lazy as _
from django.contrib import auth
from django.conf import settings
from django.db import transaction
from django.http import Http404

from apps.core.models import UserSID
from apps.sms.models import SMSLogger


@render_to('accounts/login.html')
def login(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.cleaned_data['user']
            auth.login(request, user)
            _next = request.GET.get('next', None)
            if _next:
                return {'redirect': _next}
            if request.user.is_operator:
                return {'redirect': 'catalog:service-orders'}
            return {'redirect': 'core:index'}
    return {
        'form': form
    }


@render_to('index.html')
def logout(request):
    auth.logout(request)
    return {'redirect': 'catalog:index'}


@transaction.commit_on_success
@render_to('accounts/register_user.html')
def register_user(request):
    form = UserRegisterForm(request.POST or None, request=request)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save(commit=False)
            sms = SMSLogger(provider='disms',
                    text=settings.USER_REGISTER_SMS % {
                    'login': form.cleaned_data['email'],
                    'password': form.cleaned_data['password']
                }, phone=form.cleaned_data['phone']
            )
            sms.send_message()
            user.set_password(form.cleaned_data['password'])
            user.is_active = True
            user.is_verified = True
            user.save()
            auth.login(request, user)
        #    auth_user = auth.authenticate(email=user.email, password = form.cleaned_data['password'])
        #    auth.login(request, auth_user)

            # process invite
            expired = datetime.now() + \
                timedelta(hours=settings.INVITE_EXPIRES_HOURS)
            invite = get_object_or_None(
                Invite, email=form.cleaned_data['email'],
                expire_date__lte=expired
            )
            if invite:
                invite.is_verified = True
                invite.receiver = user
                invite.save()
            return {'redirect': 'accounts:register-success', 'user': user}
    days = xrange(1, 32)
    months = xrange(1, 13)
    years = xrange(1930, 2012)
    return {'form': form, 'days': days, 'months': months, 'years': years}


@transaction.commit_on_success
def register_partner(request):
    # schedule initial
    schedule_initial = [{'weekday': i} for i in xrange(1, 8)]
    view = RegisterPartnerWizard.as_view(
        [
            RegisterPartnerForm1,
            RegisterPartnerForm2,
    #        TimeNDayFormset
        ], initial_dict={
            '2': schedule_initial,
        }
    )
    return view(request)


# checks, should be deleted as soon as it possible
@partner_required
@render_to('accounts/alter_schedule.html')
@login_required
def alter_schedule(request):
    formset = TimeNDayFormset(
        request.POST or None,
        initial=[
            {'weekday': '1'},
            {'weekday': '2'},
            {'weekday': '3'},
            {'weekday': '4'},
            {'weekday': '5'},
            {'weekday': '6'},
            {'weekday': '7'},
        ]
    )
    if request.method == 'POST':
        if formset.is_valid():
            formset.save()
            return {'redirect': 'core:index'}
    return {'formset': formset}


@login_required
@render_to('accounts/invite.html', allow_xhr=True)
def invite(request):
    form = SendInviteForm(request.POST or None, request=request)
    if request.method == 'POST':
        if form.is_valid():
            form.save(commit=False)
            invite = form.instance
            email = form.cleaned_data['email']
            subject = u"%(username)s приглашает Вас присоединиться к сервису\
 \"Уже везу\"" % {
                'username': invite.sender.get_real_name().upper()
            }
            information = render_to_string('mail/user_invite.html', {
                'site_url': settings.SITE_SHORT_URL,
                'register_link': settings.SITE_URL + reverse(
                    'accounts:invite-register', args=(invite.sid,)
                ),
                'username': invite.sender.get_real_name()

            })
#            msg = settings.INVITE_MESSAGE % {
#                'user': request.user.username,
#                'link': settings.SITE_URL + reverse(
#                    'accounts:invite-register', args=(invite.sid,)),
#                'resource': settings.SITE_URL,
#                'resource_name': settings.RESOURCE_NAME
#            }

            # no mail send, no money :)
            # send_mail(
            #    subject=unicode(
            #        _('You have been invited to %s service') % \
            #                                             settings.SERVICE_NAME
            #    ),
            #    message=information,  # unicode(msg),
            #    from_email=settings.EMAIL_FROM,
            #    recipient_list=[email]
            # )

            mail_message = EmailMulti(subject, information,
                                      settings.EMAIL_FROM, [email])
            mail_message.content_subtype = 'html'
            mail_message.send()

            invite.save()
            return {'redirect': 'accounts:invite-success'}
    return {
        'form': form
    }


@transaction.commit_on_success
@check_invite(sid='sid')
@render_to('accounts/invite_register.html')
def invite_register(request, sid):
    invite = get_object_or_None(Invite, sid=sid)
    offset = datetime.now() + timedelta(hours=settings.INVITE_EXPIRES_HOURS)
    if invite.expire_date > offset:
        invite.is_expired = True
        invite.save()
        return {'redirect': 'core:ufo'}

    if not invite:
        return {'redirect': 'core:ufo'}
    form = InviteRegisterForm(request.POST or None,
        invite=invite
    )
    if request.method == 'POST':
        if form.is_valid():
            invite.is_verified = True
            user = form.save(commit=False)
            # user.email = invite.email
            user.set_password(form.cleaned_data['password'])
            user.save()
            invite.reciever = user
            invite.save()
            return {'redirect': 'accounts:invite-register-success'}
    days = xrange(1, 32)
    months = xrange(1, 13)
    years = xrange(1930, 2012)

    return {'form': form, 'sid': sid, 'days': days, 'months': months,
            'years': years}


@login_required
@render_to('accounts/profile.html')
def profile(request):
    usr = request.user
    return {'usr': usr}


# @login_required
@render_to('accounts/profile_bonuses.html')
def profile_bonuses(request):
    if request.user.is_authenticated():
        request.user.reload_bonus_score()
    return {}


@login_required
@render_to('accounts/profile_edit.html')
def profile_edit(request):
    if request.user.is_partner:
        form = PartnerProfileEditForm(
            request.POST or None, instance=request.user, request=request)
    else:
        form = UserProfileEditForm(
            request.POST or None, instance=request.user)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return {'redirect': 'accounts:profile-edit', 'success': True}
    days = xrange(1, 32)
    months = xrange(1, 13)
    years = xrange(1930, 2012)

    return {'form': form, 'days': days, 'months': months, 'years': years}


@login_required
@partner_required
@render_to('accounts/profile_edit_org.html')
def profile_edit_org(request):
    form = PartnerEditOrgForm(
        request.POST or None, request.FILES or None, instance=request.user
    )
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return {'redirect': 'accounts:profile-edit-org'}
    return {'form': form}


@phone_owner(field='pk')
@login_required
@render_to('index.html')
def profile_contact_phone_delete(request, pk):
    phone = get_object_or_404(ContactPhone, pk=pk)
    phone.delete()
    return {'redirect': 'accounts:profile-edit'}
    
@email_owner(field='pk')
@login_required
@render_to('index.html')
def profile_contact_email_delete(request, pk):
    email = get_object_or_404(ContactEmail, pk=pk)
    email.delete()
    return {'redirect': 'accounts:profile-edit'}    


# from future
@login_required
@render_to('accounts/set_position.html')
def set_coordinates(request):
    form = AccountSetGCoordinates(
        request.POST or None,
        instance=request.user)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
    return {'form': form}


@partner_required
@login_required
@render_to('accounts/profile_edit.html')
def deliver_cost_delete(request, pk):
    deliver_cost = get_object_or_404(DeliverCost, pk=pk)
    deliver_cost.delete()
    return {'redirect': 'accounts:profile-edit-org'}


@login_required
@render_to('accounts/set_position.html')
def purge_coordinates(request):
    request.user.glat = None
    request.user.glng = None
    request.user.save()

    form = AccountSetGCoordinates(
        request.POST or None,
        instance=request.user)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
    return {'form': form}


@render_to('accounts/account_verify.html')
def account_verify(request, sid):
    verification = get_object_or_404(Verification, sid=sid)
    verification.is_verified = True
    verification.save()
    verification.user.save()
    return {'user': verification.user}


@render_to('accounts/password_restore_initiate.html')
def password_restore_initiate(request):
    form = PasswordRestoreInitiateForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            users = form.cleaned_data['users']
            sids = UserSID.objects.filter(user__in=users, expired=True)

            sids = []
            if not sids:
                for user in users:
                    sid = UserSID.objects.create(user)
                    sids.append(sid)
            else:
                for user in users:
                    sid = UserSID.objects.filter(
                        user=request.user).order_by('-id')[0]
                    sids.append(sid)

            for sid in sids:
                msg = settings.PASSWORD_RESTORE_REQUEST_MESSAGE % {
                    'link': settings.SITE_URL + reverse(
                    'accounts:password-restore', args=(sid.sid,))
                }
                send_mail(
                    subject=unicode(_('Your password requested to change')),
                    message=unicode(msg),
                    from_email=settings.EMAIL_FROM,
                    recipient_list=[sid.user.email],
                    fail_silently=True
                )
            return {'redirect': 'core:password-restore-initiated'}
    return {'form': form}


@prevent_bruteforce
@render_to('accounts/password_restore.html')
def password_restore(request, sid):
    instance = get_object_or_None(UserSID, sid=sid, expired=False)
    if not instance:
        request.session['brute_force_iter'] \
 = request.session.get('brute_force_iter', 0) + 1
        raise Http404("not found")

    form = PasswordRestoreForm(
        request.POST or None, instance=instance, request=request
    )
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return {'redirect': 'core:password-restored'}
    return {'form': form}
