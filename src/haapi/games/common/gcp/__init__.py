"""Google Cloud Common."""
from google.cloud import secretmanager  # type: ignore


class SecretManager:
    """Common SecretManager class."""

    def __init__(self) -> None:
        """Initialize SecretManager with SecretManagerServiceClient."""
        self.SECRET_CLIENT = secretmanager.SecretManagerServiceClient()

    def _get_secret(self, version: str) -> str:
        """Gets secret from version and returns decoded secret.

        Args:
            version: full version path for secret

        Returns:
            str of secret decoded for you
        """
        response: str = self.SECRET_CLIENT.access_secret_version(
            name=version
        ).payload.data.decode("UTF-8")
        return response
