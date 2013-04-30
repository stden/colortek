# -*- coding: UTF-8 -*-
from django import forms
from django.db.utils import IntegrityError

class ServiceAdminForm(forms.ModelForm):
    class Meta:
        widgets = {
            'description': forms.Textarea()
        }


class ContainerAdminForm(forms.ModelForm):
    class Meta:
        widgets = {
            'description': forms.Textarea()
        }


class OrderAdminForm(forms.ModelForm):
    class Meta:
        widgets = {
            'comment': forms.Textarea()
        }

class VoteAdminForm(forms.ModelForm):
    class Meta:
        exclude = ('is_published', )
