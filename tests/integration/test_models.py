"""Integration tests for all Bedrock models."""

import os
import warnings

import boto3
import pytest

from bedrock_swarm.models.factory import BEDROCK_MODEL_REGISTRY, ModelFactory

# Filter out botocore's datetime deprecation warning
warnings.filterwarnings(
    "ignore",
    message="datetime.datetime.utcnow\\(\\) is deprecated",
    category=DeprecationWarning,
    module="botocore.*",
)


def get_all_model_ids():
    """Get all model IDs from the registry."""
    model_ids = []
    for family, versions in BEDROCK_MODEL_REGISTRY.items():
        for version in versions.keys():
            model_id = f"{family}-{version}"
            model_ids.append(model_id)
    return model_ids


@pytest.mark.parametrize("model_id", get_all_model_ids())
def test_model(model_id):
    """Test basic functionality of Bedrock models.

    Args:
        model_id: The Bedrock model ID to test
    """
    print(f"\nTesting model: {model_id}")

    # Initialize AWS session and client
    session = boto3.Session(
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        profile_name=os.getenv("AWS_PROFILE"),
    )
    client = session.client(
        "bedrock-runtime",
        endpoint_url=f"https://bedrock-runtime.{os.getenv('AWS_REGION', 'us-east-1')}.amazonaws.com",
    )

    # Create model instance using factory
    model = ModelFactory.create_model(model_id)

    # Test simple query
    response = model.invoke(client=client, message="Hi, who are you?")
    print("\nResponse:", response)

    # Basic validation - just check response structure
    assert isinstance(response, dict), "Response should be a dictionary"
    assert "type" in response, "Response should have a type field"
    assert "content" in response, "Response should have a content field"
    assert len(response["content"]) > 0, "Response content should not be empty"
