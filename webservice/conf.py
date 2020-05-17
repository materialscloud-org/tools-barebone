import os


class ConfigurationError(Exception):
    pass


class FlaskRedirectException(Exception):
    """
    Class used to return immediately with a flash message and a redirect.
    """


directory = os.path.split(os.path.realpath(__file__))[0]
static_folder = os.path.join(directory, "static")
user_static_folder = os.path.join(directory, "user_static")
view_folder = os.path.join(directory, "view")
config_file_path = os.path.join(static_folder, "config.yaml")
