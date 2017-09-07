1. Services
=============
{% for service in order.client_services.all %}
* #{{ service.id }} {{ service.service }} {{ service.price }} - {{ service.quantity }} ({{ service.modified|date }})
{% endfor %}
