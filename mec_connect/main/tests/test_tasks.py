from __future__ import annotations

from unittest import TestCase
from unittest.mock import patch

import pytest
from main.choices import ObjectType, WebhookEventStatus
from main.tasks import populate_grist_table, process_webhook_event, refresh_grist_table
from unittest_parametrize import ParametrizedTestCase, param, parametrize

from .factories import GristConfigFactory, WebhookEventFactory


class ProcessWebhookEventTests(ParametrizedTestCase):
    @parametrize(
        "object_type, task_project_called, task_survey_called",
        [
            param(ObjectType.PROJECT, True, False, id="project"),
            param(ObjectType.PROJECT, True, False, id="taggeditem"),
            param(ObjectType.SURVEY_ANSWER, False, True, id="survey_answer"),
        ],
    )
    @pytest.mark.django_db
    def test_task_triggered_and_event_saved(
        self, object_type, task_project_called, task_survey_called
    ):
        event = WebhookEventFactory(object_type=object_type)

        with (
            patch("main.tasks.process_project_event") as process_project_mock,
            patch("main.tasks.process_survey_answer_event") as process_survey_mock,
        ):
            process_webhook_event(event_id=event.id)

        if task_project_called:
            process_project_mock.assert_called_once_with(event=event)
        else:
            process_project_mock.assert_not_called()

        if task_survey_called:
            process_survey_mock.assert_called_once_with(event=event)
        else:
            process_survey_mock.assert_not_called()

        event.refresh_from_db()
        assert event.status == WebhookEventStatus.PROCESSED

    @pytest.mark.django_db
    def test_event_does_not_exist(self):
        with patch("main.tasks.logger.error") as logger_mock:
            process_webhook_event(event_id=1)
        logger_mock.assert_called_once_with("WebhookEvent with id=1 does not exist")


class PopulateGristTableTests(TestCase):
    @pytest.mark.django_db
    def test_config_does_not_exist(self):
        with patch("main.tasks.logger.error") as logger_mock:
            populate_grist_table(config_id="40d26f87-8b91-4670-a196-bfdcbc39eabb")
        logger_mock.assert_called_once_with(
            "GristConfig with id=40d26f87-8b91-4670-a196-bfdcbc39eabb does not exist"
        )


class RefreshGristTableTests(TestCase):
    @pytest.mark.django_db
    def test_config_does_not_exist(self):
        with patch("main.tasks.logger.error") as logger_mock:
            refresh_grist_table(config_id="40d26f87-8b91-4670-a196-bfdcbc39eabb")
        logger_mock.assert_called_once_with(
            "GristConfig with id=40d26f87-8b91-4670-a196-bfdcbc39eabb does not exist"
        )

    @pytest.mark.django_db
    @patch("main.tasks.update_or_create_project_record")
    @patch("main.tasks.fetch_projects_data")
    def test_update_or_create_project_record_call(
        self,
        mock_fetch_projects_data,
        mock_update_or_create_project_record,
    ):
        mock_fetch_projects_data.return_value = [("project_id", {"project_data": "data"})]

        config = GristConfigFactory()
        refresh_grist_table(config_id=config.id)

        mock_fetch_projects_data.assert_called_once_with(config=config)

        mock_update_or_create_project_record.assert_called_once_with(
            config=config,
            project_id="project_id",
            project_data={"project_data": "data"},
        )
