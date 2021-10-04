import uuid
from django.db import models


class BaseModelMixin(models.Model):
    """
        Base model mixin to create 'created' and 'id' field for all models
    """
    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True,
                          editable=False)

    class Meta:
        abstract = True
