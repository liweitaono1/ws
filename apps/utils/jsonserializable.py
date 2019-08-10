import uuid
from datetime import datetime
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.fields.files import ImageFieldFile


class DateEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o,datetime):
            return "{}-{}-{} {}:{}:{}".format(o.year, o.month, o.day, o.hour, o.minute, o.second)
        elif isinstance(o,  uuid.UUID):
            return str(o)
        elif isinstance(o, ImageFieldFile):
            return str(o)
        return json.JSONEncoder.default(self, o)
