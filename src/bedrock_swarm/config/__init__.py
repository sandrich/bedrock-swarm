"""Configuration module for bedrock-swarm."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class AWSConfig:
    """AWS configuration for Bedrock clients.

    Attributes:
        region (str): AWS region
        profile (Optional[str]): AWS profile name
        endpoint_url (Optional[str]): Custom endpoint URL
    """

    region: str
    profile: Optional[str] = None
    endpoint_url: Optional[str] = None

    def __init__(
        self,
        region: str,
        profile: Optional[str] = None,
        endpoint_url: Optional[str] = None,
    ) -> None:
        """Initialize AWS configuration.

        Args:
            region (str): AWS region
            profile (Optional[str]): AWS profile name
            endpoint_url (Optional[str]): Custom endpoint URL
        """
        self.region = region
        self.profile = profile
        self.endpoint_url = endpoint_url
