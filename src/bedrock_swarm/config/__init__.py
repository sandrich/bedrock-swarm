from typing import Optional

class AWSConfig:
    """AWS configuration for Bedrock clients.
    
    Args:
        region (str): AWS region (e.g., us-west-2)
        profile (Optional[str]): AWS profile name
        endpoint_url (Optional[str]): Custom endpoint URL for Bedrock
    """
    
    def __init__(
        self,
        region: str,
        profile: Optional[str] = None,
        endpoint_url: Optional[str] = None
    ):
        self.region = region
        self.profile = profile
        self.endpoint_url = endpoint_url
