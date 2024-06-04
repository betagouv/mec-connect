from __future__ import annotations

from functools import partial

from django.core.serializers.json import DjangoJSONEncoder

PrettyJSONEncoder = partial(DjangoJSONEncoder, indent=2, sort_keys=True)
