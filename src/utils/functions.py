import os

def mkdir_if_not_exists(default_save_path: str):
    """
    Make directory if not exists by a folder path
    :param default_save_path: str() -> path to create the folder
    :return: None
    """

    if not os.path.exists(default_save_path):
        os.mkdir(default_save_path)

