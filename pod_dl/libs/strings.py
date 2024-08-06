import re


def sanitize_filename(input_string):
    # Convert the string to lowercase
    input_string = input_string.lower()

    # Replace characters incompatible with file names
    sanitized_string = re.sub(r'[\\/:"*?<>|]', '', input_string)

    # Replace any sequence of non-alphanumeric characters (except spaces) with a single dash
    sanitized_string = re.sub(r'[^a-z0-9]+', '-', sanitized_string)

    # Remove leading or trailing dashes
    sanitized_string = sanitized_string.strip('-')

    return sanitized_string
