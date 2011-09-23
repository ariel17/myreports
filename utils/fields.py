from django.db import models
import uuid


class UUIDField(models.CharField):

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 64)
        kwargs['null'] = True
        kwargs['blank'] = True
        models.CharField.__init__(self, *args, **kwargs)

    def pre_save(self, model_instance, add):
        if add:
            value = str(uuid.uuid4())
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super(models.CharField, self).pre_save(model_instance, add)

"""
class Example(models.Model) :
    uuid = UUIDField(primary_key=True, editable=False)
    name = models.CharField(max_length=32)
    value = models.CharField(max_length=255, blank=True)
"""
