from django.conf.urls import patterns, include, url
from apps.core.shortcuts import direct_to_template

urlpatterns = patterns('apps.accounts.views',
    url(r'login/$', 'login', name='login'),
    url(r'logout/$', 'logout', name='logout'),
    url(r'profile/$', 'profile', name='profile'),
    url(r'profile/bonuses/', 'profile_bonuses', name='profile-bonuses'),
    url(r'profile/edit/$', 'profile_edit', name='profile-edit'),
    url(r'profile/edit/organization', 'profile_edit_org',
        name='profile-edit-org'),
    url(r'profile/delivercost/(?P<pk>\d+)/delete/$',
        'deliver_cost_delete', name='deliver-cost-delete'),
    url(r'profile/set/coordinates/$',
        'set_coordinates', name='set-coordinates'),
    url(r'profile/purge/coordinates/$',
        'purge_coordinates', name='purge-coordinates'),
    url(r'profile/contact/phone/(?P<pk>\d+)/delete/$',
        'profile_contact_phone_delete',
        name='profile-contact-phone-delete'),
    url(r'profile/contact/email/(?P<pk>\d+)/delete/$',
        'profile_contact_email_delete',
        name='profile-contact-email-delete'),    
    url(r'user/register/$', 'register_user', name='register-user'),
    url(r'partner/register/$', 'register_partner', name='register-partner'),
    url(r'partner/alter/schedule/$', 'alter_schedule', name='alter-schedule'),
    url(r'register/success/', direct_to_template,
        {'template': 'accounts/register_success.html'},
        name='register-success'),
    #invites
    url(r'^invite/$', 'invite', name='invite'),
    url(r'^invite/register/success/$', direct_to_template,
        {'template': 'accounts/invite_register_success.html'},
        name='invite-register-success'),
    url(r'^invite/success/$', direct_to_template,
        {'template': 'accounts/invite_success.html'},
        name='invite-success'),
    url(r'^invite/register/(?P<sid>[\w\d]+)/$',
        'invite_register', name='invite-register'),
    url(r'^account/(?P<sid>[\w\d\_-]+)/verify/$',
        'account_verify', name='account-verify'),
    url(r'account/password/(?P<sid>[\w\d]+)/restore/$',
        'password_restore',
        name='password-restore'),
    url(r'account/password/restore/initiate/$',
        'password_restore_initiate',
        name='password-restore-initiate'),

    #end of invites
)
