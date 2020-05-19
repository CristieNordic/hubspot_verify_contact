# Hubspot Contact Verification
This is simple python script that verify your email adresses on a contact and see if it valid anymore.

## Installation
### Pre requirement
You need to run a machine like a Linux client or Windows 10 WSL and you need Python 3 and Git installed.

### Clone this project
Run following command and download this project
`git clone https://github.com/CristieNordic/hubspot_verify_contact.git`

### Crate a virtual environment and start it
Open the project directory and run `virtualenv` to isolate this project.
`virtualenv . -p python3`

To start the virtual enviroment you run following command from the bash shell.
`source bin/active`

To logout you running following command.
`deactivate`

For more information can you (read here)[https://virtualenv.pypa.io/en/latest/#]

### Install Dependency
Run pip to install all dependencies that are required.
`pip install -r requirement.txt`

## Configuration
Modify the `config.py` file that only contains your APIKey, URL to lists and some few other values that are been used in the verify.py script.
You can use any editor such like notepad, vi or any other text editor.

## Run the script
Start a bash shell and run the script by running `python verify.py`
Enjoy and wait, this can take a loooooooooooooong time depending on number of contacts.
