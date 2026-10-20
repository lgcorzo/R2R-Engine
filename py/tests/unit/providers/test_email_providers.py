import logging
from unittest.mock import MagicMock, patch

import pytest

from core.base import EmailConfig
from core.providers.email.mailersend import MailerSendEmailProvider
from core.providers.email.sendgrid import SendGridEmailProvider


@pytest.fixture
def email_config():
    return EmailConfig(
        sendgrid_api_key="SG.test_key",
        mailersend_api_key="mlsn.test_key",
        from_email="noreply@example.com",
        frontend_url="https://example.com",
        sender_name="Test Sender",
    )


@pytest.mark.asyncio
async def test_sendgrid_logging_no_sensitive_data(email_config, caplog):
    provider = SendGridEmailProvider(email_config)
    sensitive_email = "sensitive_user@example.com"
    sensitive_body = "Secret Response Body"

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.body = sensitive_body

    with patch.object(provider.client, "send", return_value=mock_response):
        with caplog.at_level(logging.ERROR):
            with pytest.raises(RuntimeError) as exc_info:
                await provider.send_email(
                    to_email=sensitive_email,
                    subject="Test Subject",
                    body="Test Body",
                )

    for record in caplog.records:
        assert sensitive_email not in record.message
        assert sensitive_body not in record.message

    assert sensitive_email in str(exc_info.value)


@pytest.mark.asyncio
async def test_sendgrid_exception_logging_no_pii(email_config, caplog):
    provider = SendGridEmailProvider(email_config)
    sensitive_email = "user_pii@example.com"

    with patch.object(
        provider.client, "send", side_effect=Exception("Connection error")
    ):
        with caplog.at_level(logging.ERROR):
            with pytest.raises(RuntimeError):
                await provider.send_email(
                    to_email=sensitive_email,
                    subject="Test Subject",
                    body="Test Body",
                )

    for record in caplog.records:
        assert sensitive_email not in record.message


@pytest.mark.asyncio
async def test_mailersend_logging_no_sensitive_data(email_config, caplog):
    provider = MailerSendEmailProvider(email_config)
    sensitive_email = "sensitive_mailersend@example.com"

    with patch.object(
        provider.client, "send", return_value="500 Internal Error"
    ):
        with caplog.at_level(logging.ERROR):
            await provider.send_email(
                to_email=sensitive_email,
                subject="Test Subject",
                body="Test Body",
            )

    for record in caplog.records:
        assert sensitive_email not in record.message
