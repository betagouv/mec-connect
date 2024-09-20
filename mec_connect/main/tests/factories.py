from __future__ import annotations

import uuid

import factory
import factory.fuzzy
from main.choices import GristColumnType, ObjectType
from main.models import GristColumn, GristColumnFilter, GristConfig, WebhookEvent
from main.services import update_or_create_columns_config


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

    @factory.post_generation
    def create_columns_config(obj, create, extracted, **kwargs):  # noqa: N805
        if not create:
            return
        if extracted:
            update_or_create_columns_config(config=obj)


class GristColumnFactory(BaseFactory):
    class Meta:
        model = GristColumn

    col_id = factory.Faker("word")
    label = factory.Faker("word")
    type = factory.fuzzy.FuzzyChoice(choices=GristColumnType.choices)


class GristColumnFilterFactory(BaseFactory):
    class Meta:
        model = GristColumnFilter

    grist_config = factory.SubFactory(GristConfigFactory)
    grist_column = factory.SubFactory(GristColumnFactory)
    filter_value = factory.Faker("word")
