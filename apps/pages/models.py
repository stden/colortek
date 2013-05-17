from django.db import models
from django.utils.translation import ugettext_lazy, pgettext_lazy
from datetime import datetime

# Create your models here.
def _(x, y=None):
    if not y:
        return ugettext_lazy(x)
    return pgettext_lazy(x, y)

APP_TRANS = (
    _("Auth", 'app admin title'),
    _("Blog", 'app admin title'),
    _('Geo', 'app admin title'),
    _('Sites', 'app admin title'),
    _('Sms', 'app admin title'),
    _("Accounts", 'app admin title'),
    _("accounts", 'app admin title'),
    _("auth", 'app admin title'),
    _("sms"),
    _('blog'),
    _('geo'),
    _('sites'),
)


class Page(models.Model):
    title = models.CharField(_("Title"), max_length=256)
    text = models.TextField(_("Text"))
    url = models.CharField(_("URL"), max_length=256)
    is_published = models.BooleanField(_("is published?"), default=False)
    created_on = models.DateTimeField(_("Created on"), auto_now=True, default=datetime.now())
    updated_on = models.DateTimeField(_("Updated on"), auto_now_add=True, default=datetime.now())
    template = models.CharField(
        _('template'), help_text=_("template which is using for this content show"),
        max_length=1024, blank=True, null=True
    )
    # seo
    description = models.CharField(_('description'), max_length=4096, blank=True, null=True)
    keywords = models.CharField(_('keywords'), max_length=4096, blank=True, null=True)

    def __unicode__(self):
        #return self.safe_translation_getter('title', 'Page %s' % self.pk)
        try:
            return self.title
        except:
            return 'Page %s' % self.pk

    class Meta:
        verbose_name = _("Page")
        verbose_name_plural = _("Pages")


class TextBlock(models.Model):
    codename = models.CharField(_("Codename"), unique=True, max_length=256)
    title = models.CharField(_("Title"), max_length=256)
    content = models.TextField(_("Content"))
    created_on = models.DateTimeField(_("Created on"), auto_now=True, default=datetime.now())
    updated_on = models.DateTimeField(_("Updated on"), auto_now_add=True, default=datetime.now())

    def __unicode__(self):
        #return self.safe_translation_getter('title', 'TextBlock %s' % self.pk)
        try:
            return self.title
        except:
            return 'TextBlock %s' % self.pk

    class Meta:
        verbose_name = _("Text block")
        verbose_name_plural = _("Text blocks")
