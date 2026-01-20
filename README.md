# Procedural DRG Room Generation

A small Python script to generate Deep Rock Galactic rooms procedurally, using random walk. The configuration file can be found in settings/. Each key in the JSON file represents a category of rooms. If you tun the script with defaults:

`uv run main.py`

it will generate 20 rooms for each entry in the settings file. You can tell it to run only specific entries:

`uv run main.py -k "SMALL"`

or change the number of generated rooms:

`uv run main.py -n 40`

A custom settings file can be used with the -c flag:

`uv run main.py -c myCustomSettings.json`
