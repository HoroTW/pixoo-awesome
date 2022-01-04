Pixoo-Awesome is a tool to get more out of your Pixoo Devices.
===============================================================

It uses the [Pixoo-Client](https://github.com/virtualabs/pixoo-client) to connect to your Pixoo devices and send data to them.

I target the Pixoo-Max because it's the device I have 😀 but it should also work with other Pixoo devices but you might need to adjust some sizes ^^.

To use this project you should clone the repository and copy the `example.env` file as `local.env` file.
You need to find the mac address of your Pixoo device and put it in the `local.env` file.

I would suggest creating a `.venv` so the project dependencies can't conflict with other projects.

Install the dependencies with `pip install -r requirements.txt`.

You might wan't to change the displayed items by editing the `pixoo.py` file.


## Development
For development you should also install the `requirements-dev.txt` file.
This project uses `black` as a formatter and `prospector` as a linter.