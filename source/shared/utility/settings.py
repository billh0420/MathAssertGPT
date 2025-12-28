# settings
# from shared.utility

import json

def save_settings(settings):
    # Get current values as a dictionary
    current_settings = settings.param.values()
    # Exclude internal param parameters (like name, etc.) if needed
    settings_to_save = {k: v for k, v in current_settings.items() if k not in ['name', 'some_tags', 'some_d_mode']}
    # Save to a JSON file
    with open('../settings.json', 'w') as f:
        json.dump(settings_to_save, f, indent=4)

def load_settings(settings):
    # Load from the JSON file
    with open('../settings.json', 'r') as f:
        loaded_data = json.load(f)
    # Update the parameters with the loaded data
    settings.param.update(**loaded_data)
