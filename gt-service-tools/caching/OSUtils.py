import os


def get_os_param(param_name):
    param_value = os.getenv(param_name)

    if param_value is not None:
        response = param_value
    else:
        response = None

    return response
