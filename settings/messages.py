# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

INVITE_MESSAGE = _("""
    You have been sent an invitation to %(resource)s.

    If you don't know whats this site/service does please ignore it or wait
    for explanation from your friends.

    Please click follow the %(link)s and follow given instructions
    to proceed the registration.

    If you got this letter accidently, please ignore it,
    nothing bad would happen.

    Sincerely your, %(resource_name)s administration.
""")

# VOTE_MESSAGE = _("""
#    You have an order and we appreciate that, so you have an infulence
#    on resource quality increasing. Please vote for quality of service
#    by answering vote question link below:
#
#    %(link)s
# """)

VOTE_MESSAGE = u""" Вы сделали заказ у компании %(company)s. Надеемся вам понравилось,
вы можете оставить отзыв у нас на сайте, проследовав по ссылке:

%(link)s
"""

NEW_ORDER_MESSAGE_TEMPLATE_NAME = 'catalog/new_order_message.html'
NEW_ORDER_SMS = u"""Здравствуйте! в %(time)s поступил новый заказ на сумму %(amount)s"""

# USER_REGISTER_SMS = u"""Спасибо за регистрацию в системе УЖЕ ВЕЗУ"""
FIRST_USER_ORDER = u"""УЖЕ ВЕЗУ благодарит Вас за заказ. Администрация УЖЕ ВЕЗУ дарит вам %(amount)s баллов. Вам будет начислено %(bonus_amount)s баллов."""
USER_ORDER = u"""УЖЕ ВЕЗУ благодарит за заказ. Вам будет начислено %(amount)s баллов."""
REGISTER_VERIFICATION_MESSAGE = u"""
    Спасибо за регистрацию на нашем сервисе "УЖЕ ВЕЗУ",
    для подтверждения вашей регистрации, пожалуйста, пройдите
    по ссылке, представленной ниже. Если вы не регистрировалсь на этом
    сайте, пожалуйста проигнорируйте это письмо.

    %(link)s

    Если ссылка не открывается в вашем браузере или открывается не правильно, скопируйте следующий адрес
    и вставьте его в адресную строку браузера:

    %(link)s
"""
ORDER_REGISTER_MESSAGE = u"""
    Спасибо за заказ и вашу регистрацию в системе УЖЕ ВЕЗУ

    вам был присвоен логин: %(login)s
    вашей учетной записи был установлен пароль: %(password)s
    осуществить авторизацию на сайте вы можете по ссылке, которая находится ниже.
    Если вы не осуществляли заказов или регистраций, пожалуйста, проигнорируйте это письмо.

    %(link)s
"""

PASSWORD_RESTORE_REQUEST_MESSAGE = u"""
    Вы или кто-то другой запросили смену пароля для аккаунта, который зарегистрирован на этот почтовый адрес.

    Если это были не вы, пожалуйста, проигнорируйте данное письмо и/или дайте знать об этом
    администрации сервиса

    Ваша ссылка для сброса пароля: %(link)s

    Если ссылка по каким-либо причинам не открывается щелкчком мыщи, просто скопируйте
    ее и вставьте в адресную строку браузера.
"""
ANONYMOUS_ORDER_MESSAGE = u"""Уже Везу благодарит за заказ. Через некоторое время с вами свяжется оператор и уточнит детали заказа."""
USER_REGISTER_SMS = u"""Спасибо за регистрацию в системе УЖЕ ВЕЗУ.
Ваш логин: %(login)s
Ваш пароль: %(password)s"""
