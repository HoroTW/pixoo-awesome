Pixoo-Awesome is a tool to get more out of your Pixoo Devices.
===============================================================

It uses the [Pixoo-Client](https://github.com/virtualabs/pixoo-client) to connect to your Pixoo devices and send data to them.

I target the Pixoo-Max because it's the device I have 😀 but it should also work with other Pixoo devices but you might need to adjust some sizes ^^.

To use this project you should clone the repository and copy the `example.env` file as `local.env` file.
You need to find the mac address of your Pixoo device and put it in the `local.env` file.

I would suggest creating a `.venv` so the project dependencies can't conflict with other projects.

## Requirements
- Python 3.6+
- The packages in the requirements.txt file
- The `local.env` file with the mac address of your Pixoo device

## Quick start
```bash
# copy the example.env file to local.env
cp example.env local.env
# insert the mac address of your Pixoo device and other credentials as needed
nano local.env
# Create a virtual environment
python3 -m venv .venv
# Activate the virtual environment
source .venv/bin/activate
# Install the project dependencies
pip install -r requirements.txt
# Run the project
python pixoo.py
```

You might wan't to change what is shown on your Pixoo device by editing the `pixoo.py` file.


## Development
For development you should also install the `requirements-dev.txt` file.
This project uses `black` as a formatter and `prospector` as a linter.

Pull requests are welcome! 🙌 🙌 🙌

## Feature Ideas:
 - more Indicators (Single Pixels to represent some value like existing github "did <some user> made a commit today?")
 - different graphs to show values like cpu usage, memory usage, etc.
 - a scheduler to display different modes time based (like e.g. the weather forecast)
 - display GIFs
 - display pictures with panning and zooming
 - display an folder with pictures as a slideshow
 - a night mode to turn the screen off at night
 - a dynamic Text display (would be cool if it could choose a text size so that it fits on the screen even on multiline text)
 - the integration to home assistant
