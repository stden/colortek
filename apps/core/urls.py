from django.conf.urls.defaults import patterns, include, url
from apps.core.shortcuts import direct_to_template


urlpatterns = patterns('apps.core.views',
    url('^$', 'index', name='index'),
    # static urls with info
    url('^permission/denied/$', direct_to_template,
        {'template': 'core/blockage.html'},
        name='blockage'),
    url('^permission/fields/required/$', direct_to_template,
        {'template': 'core/fields_required.html'},
        name='fields-required'),
    url('^could/not/proceed/$', direct_to_template,
        {'template': 'core/ufo.html'},
        name='ufo'),
#    url('^about/$', direct_to_template,
#        {'template': 'about.html'},
#        name='about'),
    url(r'^password/restored/$', direct_to_template,
        {'template': 'static/password_restored.html'},
        name='password-restored'),
    url(r'^password/restore/initiated/$', direct_to_template,
        {'template': 'static/password_restore_initiated.html'},
        name='password-restore-initiated'),
    url(r'test/500/$',
        'test_500', name='test-500'),

)

