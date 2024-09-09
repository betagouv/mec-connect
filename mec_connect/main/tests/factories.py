from __future__ import annotations

import uuid

import factory
import factory.fuzzy
from main.choices import ObjectType
from main.models import GristConfig, WebhookEvent


class BaseFactory(factory.django.DjangoModelFactory):
    class Meta:
        abstract = True

    id = factory.LazyFunction(uuid.uuid4)


class WebhookEventFactory(BaseFactory):
    class Meta:
        model = WebhookEvent

    webhook_uuid = factory.LazyFunction(uuid.uuid4)
    topic = "projects.Project/update"
    object_id = 1
    object_type = ObjectType.PROJECT

    remote_ip = factory.Faker("ipv4")
    headers = {}
    payload = {}


class GristConfigFactory(BaseFactory):
    class Meta:
        model = GristConfig

    name = factory.Faker("word")
    doc_id = factory.fuzzy.FuzzyText(length=10)
    table_id = factory.fuzzy.FuzzyText(length=10)
