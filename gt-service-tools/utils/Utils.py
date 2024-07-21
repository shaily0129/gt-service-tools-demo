import os
def load_env_file(file_path):
    """
    Load environment variables from a file and set them in the local environment.
    :param file_path: Path to the .env file
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith('#'):  # Ignore empty lines and comments
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()