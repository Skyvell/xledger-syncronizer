import logging
from io import BytesIO
from azure.storage.filedatalake import DataLakeServiceClient, DataLakeFileClient
from azure.core.exceptions import ResourceExistsError, HttpResponseError


class DataLakeWriter:
    """
    Handles writing data to Azure Data Lake Storage.

    This class manages the creation of file systems, directories, and files,
    and supports writing string data or data from a BytesIO object directly to Azure Data Lake Storage.
    """

    def __init__(self, account_name: str, account_key: str):
        """
        Initialize the DataLakeWriter with the storage account credentials.

        :param account_name: Azure storage account name
        :param account_key: Azure storage account key
        """
        self.service_client = DataLakeServiceClient(
            account_url=f"https://{account_name}.dfs.core.windows.net",
            credential=account_key
        )

    def _get_file_system_client(self, file_system_name: str):
        """
        Get the file system client.

        :param file_system_name: Name of the file system (container)
        :return: File system client
        """
        return self.service_client.get_file_system_client(file_system_name)

    def _ensure_file_system_exists(self, file_system_name: str) -> None:
        """
        Ensure that the specified file system exists. Create it if it does not exist.

        :param file_system_name: Name of the file system (container)
        """
        file_system_client = self._get_file_system_client(file_system_name)
        try:
            file_system_client.create_file_system()
            logging.info(f"File system '{file_system_name}' created successfully.")
        except ResourceExistsError:
            logging.info(f"File system '{file_system_name}' already exists.")
        except HttpResponseError as e:
            logging.error(f"Failed to create or access file system '{file_system_name}': {e}")
            raise

    def _ensure_directory_exists(self, file_system_client, directory_name: str) -> None:
        """
        Ensure that the specified directory exists. Create it if it does not exist.

        :param file_system_client: Client for the file system
        :param directory_name: Name of the directory
        """
        try:
            parent_directories = directory_name.strip('/').split('/')
            current_path = ''
            for dir_name in parent_directories:
                current_path = f"{current_path}/{dir_name}" if current_path else dir_name
                try:
                    file_system_client.create_directory(current_path)
                    logging.info(f"Directory '{current_path}' created.")
                except HttpResponseError as e:
                    if e.status_code == 409:  # Directory already exists
                        logging.info(f"Directory '{current_path}' already exists.")
                    else:
                        logging.error(f"Failed to create directory '{current_path}': {e}")
                        raise
        except HttpResponseError as e:
            logging.error(f"Failed to ensure directory '{directory_name}' exists: {e}")
            raise

    def _get_file_client(self, file_system_client, directory_name: str, file_name: str) -> DataLakeFileClient:
        """
        Get or create the file client.

        :param file_system_client: Client for the file system
        :param directory_name: Name of the directory
        :param file_name: Name of the file
        :return: File client
        """
        directory_client = file_system_client.get_directory_client(directory_name)
        try:
            return directory_client.create_file(file_name)
        except HttpResponseError as e:
            if e.status_code == 409:  # File already exists
                logging.info(f"File '{file_name}' already exists in '{directory_name}'.")
                return directory_client.get_file_client(file_name)
            else:
                logging.error(f"Failed to create or get file '{file_name}': {e}")
                raise

    def _write_to_file(self, file_client: DataLakeFileClient, data: bytes) -> None:
        """
        Write data to the file.

        :param file_client: Client for the file
        :param data: Data to write to the file
        """
        try:
            file_client.append_data(data, offset=0, length=len(data))
            file_client.flush_data(len(data))
            logging.info("Data written successfully.")
        except HttpResponseError as e:
            logging.error(f"Failed to write data to file '{file_client.path_name}': {e}")
            raise

    def write_data(self, file_system_name: str, directory_name: str, file_name: str, data) -> None:
        """
        Write data to a file in Azure Data Lake Storage.

        :param file_system_name: Name of the file system (container)
        :param directory_name: Name of the directory
        :param file_name: Name of the file
        :param data: Data to write to the file, can be a string or BytesIO object
        """
        # Ensure the file system exists.
        self._ensure_file_system_exists(file_system_name)

        # Get the file system client.
        file_system_client = self._get_file_system_client(file_system_name)

        # Ensure the directory exists.
        self._ensure_directory_exists(file_system_client, directory_name)

        # Create or get the file client.
        file_client = self._get_file_client(file_system_client, directory_name, file_name)

        # Handle BytesIO data
        if isinstance(data, BytesIO):
            data.seek(0)  # Move to the start of the BytesIO buffer
            bytes_data = data.read()
        elif isinstance(data, str):
            bytes_data = data.encode('utf-8')  # Convert string data to bytes
        else:
            raise ValueError("Data must be a string or BytesIO object.")

        # Write data to the file.
        self._write_to_file(file_client, bytes_data)

        logging.info(f"Data written to '{file_system_name}/{directory_name}/{file_name}' successfully.")