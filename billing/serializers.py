from django.apps import apps


class NestedUpdateSerializerMixin(object):
    """
    Base nested serializer update and create
    """

    def _update_instance(self, instance, data, exclude_attrs=None):
        for attr, value in data.items():
            if not exclude_attrs or attr not in exclude_attrs:
                setattr(instance, attr, value)
        instance.save()
        return instance

    def _update_reference(self, instance, data, ref_name, ref_new=None):
        ref_data = data.pop(ref_name, None)
        if ref_data:
            ref = getattr(instance, ref_name, ref_new)
            if ref:
                self._update_instance(ref, ref_data)
        return instance

    def create(self, validated_data):
        instance = self.Meta.model()
        self._update(instance, validated_data)
        return instance

    def update(self, instance, validated_data):
        self._update(instance, validated_data)
        return instance

    def _update(self, instance, validated_data):
        self._update_instance(instance, validated_data,
                              self.Meta.references.keys())
        for key, model_name in self.Meta.references.items():
            model = apps.get_model(model_name)
            self._update_reference(
                instance, validated_data, key, model(company=instance))
