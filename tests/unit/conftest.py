"""Shared test fixtures."""

import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture(autouse=True)
def mock_aws_session():
    """Mock AWS session for all tests."""
    with patch("boto3.Session") as mock_session:
        session = MagicMock()
        mock_client = MagicMock()
        
        # Set up standard response for non-streaming calls
        mock_response = {
            "completion": "Test response",
            "stop_reason": "stop",
        }
        mock_body = MagicMock()
        mock_body.read = MagicMock(return_value=mock_response)
        mock_client.invoke_model = MagicMock(return_value={"body": mock_body})
        
        # Set up streaming response
        mock_stream = MagicMock()
        mock_stream.__iter__ = MagicMock(return_value=iter([
            {"chunk": {"bytes": b'{"type": "content_block_delta", "delta": {"text": "Test streaming response"}}'}}
        ]))
        mock_stream.close = MagicMock()
        mock_client.invoke_model_with_response_stream = MagicMock(
            return_value={"body": mock_stream}
        )
        
        session.client.return_value = mock_client
        mock_session.return_value = session
        yield mock_session 