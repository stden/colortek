# coding: utf-8
#
from django import forms
from django.utils.translation import ugettext_lazy as _

class TextareaForm(object):
    class Media:
        js = (
            '/media/js/tiny_mce/tiny_mce.js',
            '/media/js/textareas.js',
        )


class RequestModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs['request']
            del kwargs['request']
        super(RequestModelForm, self).__init__(*args, **kwargs)


class BruteForceCheck(object):
    """ depents on RequestModelForm """
    def __init__(self, *args, **kwargs):
        super(PasswordRestoreForm, self).__init__(*args, **kwargs)
        if all(self.data or (None, )):
            if not hasattr(self, 'request'):
                raise ImproperlyConfigured("You should add request")

    def save(self, commit=True):
        super(BruteForceCheck, self).save(commit)
        if 'brute_force_iter' in self.request.session:
            del self.request.session['brute_force_iter']
            self.request.session.save()

    def is_valid(self, *args, **kwargs):
        super(PasswordRestoreForm, self).is_valid(*args, **kwargs)
        if not self.is_valid():
            self.request['brute_force_iter'] = \
                self.request.get('brute_force_iter', 0) + 1
