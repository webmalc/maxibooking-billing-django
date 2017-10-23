from django.db import models
from django.db.models import Sum


class PropertyManager(models.Manager):
    """"
    Property manager
    """
    pass


class RoomManager(models.Manager):
    """"
    Room manager
    """

    def count_rooms(self, client):
        """
        Count client property rooms
        """
        rooms_max = self.filter(property__client=client).aggregate(
            Sum('rooms'))['rooms__sum']

        return rooms_max if rooms_max else 0
