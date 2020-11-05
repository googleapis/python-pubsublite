from google.oauth2 import service_account


class ConstructableFromServiceAccount:
    @classmethod
    def from_service_account_file(cls, filename, **kwargs):
        f"""Creates an instance of this client using the provided credentials file.
        Args:
            filename (str): The path to the service account private key json
                file.
            kwargs: Additional arguments to pass to the constructor.
        Returns:
            A {cls.__name__}.
        """
        credentials = service_account.Credentials.from_service_account_file(filename)
        return cls(credentials=credentials, **kwargs)

    from_service_account_json = from_service_account_file
