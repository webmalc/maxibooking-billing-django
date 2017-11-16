{% load i18n %}1. {% trans 'services'|capfirst %}
=============
{% for service in order.client_services.all %}
* #{{ service.id }} {{ service.service }} - {{ service.price }} - {{ service.quantity }} ({{ service.begin|date }} - {{ service.end|date }})
{% endfor %}
