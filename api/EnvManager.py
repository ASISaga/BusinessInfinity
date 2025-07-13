import os

class EnvManager:
    """Centralized environment variable access for configuration."""
    def get(self, key, default=None):
        """Get an environment variable, with optional default."""
        return os.getenv(key, default)

    def get_required(self, key):
        """Get a required environment variable, raise if missing."""
        value = os.getenv(key)
        if value is None:
            raise EnvironmentError(f"Missing required environment variable: {key}")
        return value

    def get_int(self, key, default=None):
        """Get an environment variable as int, with optional default."""
        value = os.getenv(key, default)
        if value is not None:
            try:
                return int(value)
            except ValueError:
                raise ValueError(f"Environment variable {key} is not a valid integer.")
        return default

    def get_bool(self, key, default=False):
        """Get an environment variable as bool."""
        value = os.getenv(key)
        if value is None:
            return default
        return value.lower() in ("1", "true", "yes", "on")
