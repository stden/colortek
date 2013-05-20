# coding: utf-8
from datetime import datetime, timedelta

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User

from apps.accounts.managers import VerificationManager

import caching.base



WEEKDAY_CHOICES = (
    (1, _("Mon")),
    (2, _("Tue")),
    (3, _("Wed")),
    (4, _("Thu")),
    (5, _("Fri")),
    (6, _("Sat")),
    (7, _("Sun")),
)


class ContactPhoneType(models.Model):
    title = models.CharField(_("title"), max_length=32, unique=True)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _("Contact phone type")
        verbose_name_plural = _("Contact phone types")


class ContactPhone(models.Model):
    phone = models.CharField(_("phone"), max_length=21)
    type = models.ForeignKey(
        ContactPhoneType, related_name='phone_type_set', default=1,
        verbose_name=_('phone type'))
    user = models.ForeignKey(
        User, related_name='phone_user_set',
        verbose_name=_("phone user"))

    def __unicode__(self):
        return "%(type)s: %(phone)s [%(user)s]" % {
            'type': self.type.title,
            'phone': self.phone,
            'user': self.user.username
        }

    class Meta:
        verbose_name = _("Contact phone")
        verbose_name_plural = _("Contact phones")


class ContactEmail(models.Model):
    email = models.EmailField(_("email"))
    user = models.ForeignKey(User, related_name='email_user_set')

    def __unicode__(self):
        return '%s [%s]' % (self.email, self.user.username)

    class Meta:
        verbose_name = _("Contact email")
        verbose_name_plural = _("Contact emails")


class Schedule(caching.base.CachingMixin, models.Model):
    """ partner working schedule,
    contains working days with its time ranges
    """
    user = models.ForeignKey('auth.User', related_name='schedule_user_set')

    objects = caching.base.CachingManager()

    @property
    def days(self):
        return self.timenday_schedule_set

    def __unicode__(self):
        return unicode(_("%s schedule") % self.user.username)

    class Meta:
        verbose_name = _("Schedule")
        verbose_name_plural = _("Schedules")


class TimeNDay(caching.base.CachingMixin, models.Model):
    """ describes working time for given day """
    weekday = models.IntegerField(
        _("week day"),
        validators=[
            MinValueValidator(1),  # 1 means monday
            MaxValueValidator(7)  # 2 means sunday
        ],
        choices=WEEKDAY_CHOICES
    )
    since = models.TimeField(_("since"))
    until = models.TimeField(_("until"))
    schedule = models.ForeignKey(
        'accounts.Schedule', related_name='timenday_schedule_set',
        verbose_name=_("schedule"))
    is_active = models.BooleanField(
        _('is active?'),
        help_text=_("marks if this schedule point is active"),
        default=True
    )

    objects = caching.base.CachingMixin()

    def __unicode__(self):
        return ("[{user}] {weekday}, {since} - {until}").format(
            user=self.schedule.user.username, weekday=self.weekday,
            since=self.since, until=self.until
        )

    class Meta:
        verbose_name = _("Time and day")
        verbose_name_plural = _("Time and days")


class DeliverCost(models.Model):
    user = models.ForeignKey(
       User, related_name='deliver_cost_user_set'
    )
    min = models.PositiveIntegerField(
        _("min"), default=0,
        help_text=_("min border value in killometers")
    )
    max = models.PositiveIntegerField(
        _("max"), default=5,
        help_text=_("max border value in killometers")
    )
    cost = models.DecimalField(
        _("cost"), help_text=_("Deliver cost for this distance range"),
        max_digits=10, decimal_places=2,
    )

    def __unicode__(self):
        return "%s [%s km to %s km]" % (self.cost, self.min, self.max)

    class Meta:
        verbose_name = _("Deliver cost")
        verbose_name_plural = _("Deliver costs")


class Invite(models.Model):
    is_expired = models.BooleanField(
        _("is expired?"), default=False)
    expire_date = models.DateTimeField(
        _("expire date"), help_text=_("date and time when invite is expired"),
        default=datetime.now() + timedelta(days=7)
    )
    created_on = models.DateTimeField(
        _("created on"), help_text=_("created date of invitation"),
        default=datetime.now, auto_now_add=True
    )
    updated_on = models.DateTimeField(
        _("updated on"), help_text=_("date when this was updated last time"),
        default=datetime.now, auto_now=True
    )
    sender = models.ForeignKey(
        User,
        related_name='invite_sender_user_set', null=True,
        verbose_name=_("sender")
    )
    reciever = models.ForeignKey(
        User,
        related_name='invite_reciever_user_set', null=True,
        blank=True,
        verbose_name=_("reciever")
    )
    email = models.EmailField(
        _("Email"), help_text=_("Friend email"), null=True,
        unique=True
    )
    sid = models.CharField(
        _("SID"), help_text=_("SpecialID for registration"),
        max_length=128
    )
    is_verified = models.BooleanField(
        _("is verified?"), help_text=_("shows if user is verified"),
        default=False)

    def __unicode__(self):
        return "%s [%s]" % (self.sender.username, self.email)

    class Meta:
        verbose_name = _("Invite")
        verbose_name_plural = _("Invites")
        ordering = ['-created_on', '-updated_on']


class Verification(models.Model):
    is_processed = models.BooleanField(
        _("is processed?"), default=False,
    )
    sid = models.CharField(max_length=512, unique=True)
    user = models.ForeignKey(
        User, related_name='verification_user_set',
        null=True, blank=True
    )
    is_verified = models.BooleanField(
        _('is verified?'), default=False
    )

    objects = VerificationManager()

    def __unicode__(self):
        return self.user.username

    class Meta:
        verbose_name = _("Verification")
        verbose_name_plural = _("Verification")


from apps.accounts.signals import setup_signals
setup_signals()
