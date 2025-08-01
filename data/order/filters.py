import django_filters as filters

from data.customer.models import Customer
from data.order.models import Order


class ORderFIlters(filters.FIlterSet):

    customer = filters.ModelChoiceFilter(queryset=Customer.objects.all())


    class Meta:
        model = Order
        fiels = ["order_id", "customer"]
