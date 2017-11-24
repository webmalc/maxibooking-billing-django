from rest_framework import serializers

from .models import Order, Price, Service, Transaction


class PaymentSystemSerializer(serializers.Serializer):
    """
    PaymentSystem serializer
    """
    id = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()
    countries = serializers.ListField()
    countries_excluded = serializers.ListField()
    html = serializers.CharField()


class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    """
    Transaction serializer
    """

    order = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    created_by = serializers.StringRelatedField(many=False, read_only=True)
    modified_by = serializers.StringRelatedField(many=False, read_only=True)

    class Meta:
        model = Transaction
        fields = ('id', 'order', 'data', 'created', 'modified', 'created_by',
                  'modified_by')


class OrderSerializer(serializers.HyperlinkedModelSerializer):
    """
    Order serializer
    """

    client_services = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name='clientservice-detail')
    client = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field='login')
    created_by = serializers.StringRelatedField(many=False, read_only=True)
    modified_by = serializers.StringRelatedField(many=False, read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'status', 'note', 'price', 'price_currency',
                  'expired_date', 'paid_date', 'payment_system', 'client',
                  'client_services', 'created', 'modified', 'created_by',
                  'modified_by')


class ServiceSerializer(serializers.HyperlinkedModelSerializer):
    """
    Service serializer
    """

    prices = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name='price-detail')
    created_by = serializers.StringRelatedField(many=False, read_only=True)
    modified_by = serializers.StringRelatedField(many=False, read_only=True)

    class Meta:
        model = Service
        fields = ('id', 'title', 'description', 'price', 'price_currency',
                  'prices', 'period', 'period_units', 'period_days',
                  'default_rooms', 'is_enabled', 'is_default', 'created',
                  'modified', 'created_by', 'modified_by')


class PriceSerializer(serializers.HyperlinkedModelSerializer):
    """
    Price serializer
    """

    service = serializers.HyperlinkedRelatedField(
        many=False, read_only=True, view_name='service-detail')
    country = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field='tld')
    created_by = serializers.StringRelatedField(many=False, read_only=True)
    modified_by = serializers.StringRelatedField(many=False, read_only=True)

    class Meta:
        model = Price
        fields = ('id', 'price', 'price_currency', 'country', 'service',
                  'is_enabled', 'created', 'modified', 'created_by',
                  'modified_by')
