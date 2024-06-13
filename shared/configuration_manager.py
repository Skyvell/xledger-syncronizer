import logging
from azure.appconfiguration import AzureAppConfigurationClient
from azure.appconfiguration import ConfigurationSetting
from azure.core.exceptions import ResourceNotFoundError, AzureError


class ConfigurationManager:
    def __init__(self, connection_string: str, prefix: str = ''):
        self.client = AzureAppConfigurationClient.from_connection_string(connection_string)
        self.settings = {}
        self.prefix = prefix

    def load(self):
        try:
            fetched_kv = self.client.list_configuration_settings()
            self.settings = {item.key[len(self.prefix):]: item.value
                             for item in fetched_kv if item.key.startswith(self.prefix)}
            logging.info("Configuration loaded successfully.")
        except Exception as e:
            logging.error(f"Failed to load configuration: {e}")

    def save(self):
        try:
            for key, value in self.settings.items():
                self.client.set_configuration_setting(ConfigurationSetting(key=self.prefix + key, value=value))
            logging.info("Configuration saved successfully.")
        except Exception as e:
            logging.error(f"Failed to save configuration: {e}")

    def __getattr__(self, name):
        if name in ['client', 'settings', 'prefix']:
            return super().__getattr__(name)
        return self.settings.get(name, None)

    def __setattr__(self, name, value):
        if name in ['client', 'settings', 'prefix']:
            super().__setattr__(name, value)
        else:
            self.settings[name] = value
            logging.info(f"Setting updated - {name}: {value}")


class SynchronizerStateManager:
    """
    Manages the synchronizer state using Azure App Configuration.

    This class handles state variables related to the synchronization process,
    including `deltas_cursor`, `initial_sync_complete`, and `initial_sync_cursor`.
    The state is stored and retrieved directly from Azure App Configuration.
    """

    def __init__(self, connection_string: str, prefix: str = ''):
        """
        Initialize the SynchronizerStateManager.

        :param connection_string: Connection string for Azure App Configuration.
        :param prefix: Optional prefix for filtering configuration keys.
        """
        self._client = AzureAppConfigurationClient.from_connection_string(connection_string)
        self._prefix = prefix

    def _get_state(self, key: str):
        """
        Fetch the current value for the specified key from Azure App Configuration.

        :param key: The key of the configuration setting.
        :return: The value of the configuration setting, or None if the key does not exist.
        """
        try:
            config_key = f"{self._prefix}{key}"
            setting = self._client.get_configuration_setting(key=config_key)
            logging.info(f"Fetched state: {key} = {setting.value}")
            return setting.value
        except ResourceNotFoundError:
            logging.warning(f"State key not found: {key}")
            return None
        except AzureError as e:
            logging.error(f"Error fetching state {key}: {e}")
            raise

    def _save_state(self, key: str, value: str):
        """
        Save the value for the specified key to Azure App Configuration.

        :param key: The key of the configuration setting.
        :param value: The value to be saved.
        """
        try:
            config_key = f"{self._prefix}{key}"
            config_setting = ConfigurationSetting(key=config_key, value=value)
            self._client.set_configuration_setting(config_setting)
            logging.info(f"Saved state: {key} = {value}")
        except AzureError as e:
            logging.error(f"Error saving state {key}: {e}")
            raise

    @property
    def deltas_cursor(self) -> str:
        """
        Get the deltas cursor state.

        :return: The current deltas cursor, or None if not set.
        """
        return self._get_state('deltas_cursor')

    @deltas_cursor.setter
    def deltas_cursor(self, cursor: str):
        """
        Set the deltas cursor state.

        :param cursor: The new value for the deltas cursor.
        """
        self._save_state('deltas_cursor', cursor)

    @property
    def initial_sync_complete(self) -> bool:
        """
        Get the initial synchronization completion state.

        :return: True if the initial synchronization is complete, otherwise False.
        """
        return self._get_state('initial_sync_complete') == 'true'

    @initial_sync_complete.setter
    def initial_sync_complete(self, completes: bool):
        """
        Set the initial synchronization completion state.

        :param completes: True to mark the initial synchronization as complete, False otherwise.
        """
        self._save_state('initial_sync_complete', 'true' if completes else 'false')

    @property
    def initial_sync_cursor(self) -> str:
        """
        Get the initial synchronization cursor state.

        :return: The current initial synchronization cursor, or None if not set.
        """
        return self._get_state('initial_sync_cursor')

    @initial_sync_cursor.setter
    def initial_sync_cursor(self, cursor: str):
        """
        Set the initial synchronization cursor state.

        :param cursor: The new value for the initial synchronization cursor.
        """
        self._save_state('initial_sync_cursor', cursor)
