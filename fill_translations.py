import json
import os
import re

from typing import List

STANDARD_KEYS = [
   'id', 'type', 'author',
]


def get_translation_files() -> List[str]:
    """
    Returns a list of translation files in the current directory.

    Translation file is considered to start with translation and end with .json
    in the file name.
    """
    return [
        file for file in os.listdir(".")
        if (
            os.path.isfile(file)
            and file.endswith(".json")
            and file.startswith("translation")
        )
    ]


def remove_comments(string: str) -> str:
    """Removes single line comments from the specified string."""
    return re.sub(r'(\/\/.+)', '', string)


def read_json_to_dict(file_path: str) -> List[dict]:
    """Attempts to read a JSON file at the specified path to a list of dictionaries."""
    cleaned_lines = []
    with open(file_path, mode="r", encoding="utf-8") as f:
        for line in f.readlines():
            cleaned_lines.append(
               remove_comments(line)
            )
    return json.loads(''.join(cleaned_lines), object_pairs_hook=dict)


def get_filtered_keys(dictionary: dict) -> List[str]:
    """Returns a filtered list of dictionary keys.
    
    It filters out keys defined in STANDARD_KEYS constant."""
    return [
        key for key in dictionary.keys()
        if key not in STANDARD_KEYS
    ]


if __name__ == "__main__":
    files = get_translation_files()

    # Find default translation file
    print("Searching for default translation file")
    default_file = None
    default_obj = None
    filtered_files = []
    for file in files:
        obj = read_json_to_dict(file)[0] # Generally, it should be first and the only JSON object per file

        if obj['type'] != "translation":
           print(f"{file}: First object is not a translation, skipping")
           continue

        other_keys = get_filtered_keys(obj)
        count = len(other_keys)
        if count == 0:
           print(f"{file}: Has no keys after filtering, skipping")
           continue

        if count > 1:
           print(f"{file}: More than 1 keys remain ({other_keys}) after filtering, manual intervention required, skipping")
           continue

        if other_keys[0] == "*":
            if default_file is None:
                print(f"Found default translation at {file}")
                default_file = file
                default_obj = obj
            else:
               print("More than one default file detected, exiting")
               exit()
        else:
           filtered_files.append(file)


    # If we failed, let the user know
    if default_file is None:
        print("Failed to find the default file")
        exit()
    assert default_obj

    default_keys = default_obj["*"].keys()

    # Should be safe since we checked it all beforehand
    for file in filtered_files:
        obj = read_json_to_dict(file)[0]
        language = get_filtered_keys(obj)[0]
        current_keys = obj[language].keys()
        print(f"Updating {file} (language: {language})")

        for string_key in default_keys:
            if string_key not in current_keys:
               obj[language][string_key] = default_obj["*"][string_key]
               print(f"Adding missing {string_key!r} translation string")
             
        with open(file, "r+", encoding="utf-8") as f:
            f.seek(0)
            json.dump([obj], f, indent=2, ensure_ascii=False)
            f.truncate()
