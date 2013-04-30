# -*- coding: UTF-8 -*-
from django import forms
from django.db.utils import IntegrityError
from django.contrib.auth.models import User


class PostAdminForm(forms.ModelForm):
    class Meta:
        widgets = {
            'announce': forms.Textarea()
        }

    def __init__(self, *args, **kwargs):
        super(PostAdminForm, self).__init__(*args, **kwargs)
        self.fields['service'].queryset = User.objects.filter(is_partner=True)

