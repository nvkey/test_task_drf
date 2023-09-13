from typing import Mapping, MutableMapping

from django.db.models import Model
from django.shortcuts import get_object_or_404


def set_field_obj(data: MutableMapping, field, model: Model) -> Mapping:
    """Заменяет id в указанном поле на объект по id"""
    obj_id = data.pop(field)
    obj_field = get_object_or_404(model, id=obj_id)
    return data | {field: obj_field}
