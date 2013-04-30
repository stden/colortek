from django.contrib.auth.models import User
from apps.catalog.models import Order
from datetime import datetime, timedelta
from random import randint

def orders_count(i, count=0):
    n = datetime.now()
    zero = datetime(n.year, n.month, n.day)

    if i == 0:
        return count
    Pi = i * 15
    offset = zero + timedelta(minutes=15*Pi)
    E = Order.objects.filter(created_on__gte=zero, created_on__lte=offset,).count() + 15
    count += E
    return accounts(i-1, count)

def orders_step(Pi):
    n = datetime.now()
    # zero point of current day
    zero = datetime(n.year, n.month, n.day)
    offset = zero + timedelta(minutes=15*Pi)
    E = Order.objects.filter(created_on__gte=zero, created_on__lte=offset).count() + 15
    return E

def accounts_step(Pi):
    n = datetime.now()
    # zero point of current day
    zero = datetime(n.year, n.month, n.day)
    offset = zero + timedelta(minutes=15*Pi)
    U = User.objects.filter(date_joined__gte=zero, date_joined__lte=offset).count() + 7
    return U

def accounts(Pi, count=0):
    if Pi == 0:
        return count
    n = datetime.now()
    # zero point of current day
    zero = datetime(n.year, n.month, n.day)
    offset = zero + timedelta(minutes=15*Pi)
    U = User.objects.filter(date_joined__gte=zero, date_joined__lte=offset).count() + 7
    count += U
    return accounts(Pi-1, count)


def stats(request):
    # YOU BETTER do not know what is going on here
    # I don't know either, not my idea
    participant_user_count = User.objects.filter(is_partner=False).count()
    total_user_count = User.objects.count()
    partners_count = User.objects.filter(is_partner=False).count()
    online_users = randint(total_user_count / 3, 200)
    if (total_user_count / 3 > 199):
        online_users = 200 - randint(0, 10)     
    n = datetime.now()
    Pi = (n.hour * 60 + n.minute) / 15
    # zero point of current day
    zero = datetime(n.year, n.month, n.day)
    day_off = zero + timedelta(hours=23, minutes=59, seconds=59)
    offset = zero + timedelta(minutes=15*Pi)
    if Pi -1 > 0:
        orders_count = (orders_step(Pi-1) + orders_step(Pi))*Pi
        user_count = accounts_step(Pi-1) * Pi
    else:
        orders_count = orders_step(Pi) * Pi
        user_count = accounts_step(Pi) * Pi
    user_count = accounts(Pi)

    user_count = User.objects.filter(is_partner=False).count()
    orders_count = Order.objects.filter(created_on__gte=zero, created_on__lte=day_off).count() #created_on__gte=zero, created_on__lte=offset,).count() + 15
    orders_count = orders_count * 10 if orders_count > 0 else 100  # 10*10


    return {
        'participant_user_count': participant_user_count,
        'partners_count': partners_count,
        'online_users': online_users,
        'present_orders_count': orders_count,
        'present_user_count': user_count,
        'total_user_count': total_user_count,
    }
