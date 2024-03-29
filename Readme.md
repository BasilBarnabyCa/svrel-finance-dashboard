## Project Setup
### Python Installation
**Windows**
1. Visit the official Python downloads page at (https://www.python.org/downloads/windows/)
2. Click on the link for the Latest Python 3 Release - Python x.x.x (replace x.x.x with the current version number).
3. Scroll down and click on the link for Windows x86-64 executable installer if you have a 64-bit system, or Windows x86 executable installer if you have a 32-bit system.
4. Once the installer is downloaded, run the installer file.
5. On the first installer page, make sure you check the box "Add Python x.x to PATH" to set the system variable PATH.
6. Click "Install Now" - this will handle the installation for you.
7. Once the installation is complete, you can verify the installation by opening a new command prompt (make sure it's a new command prompt, and not one that was already open) and typing `python --version`. You should see the Python version that you installed.

**MacOS**
1. Visit the official Python downloads page at (https://www.python.org/downloads/mac-osx/)
2. Click on the link for the Latest Python 3 Release - Python x.x.x (replace x.x.x with the current version number).
3. Scroll down to the Files section and click on the link for macOS 64-bit installer.
4. Once the installer is downloaded, run the installer file and follow the instructions.
5. Once the installation is complete, you can verify the installation by opening a new terminal window (make sure it's a new terminal window, not one that was already open) and typing `python3 --version`. You should see the Python version that you installed.

Please note that MacOS comes with a pre-installed version of Python (Python 2.7.x), but this version is not updated and does not receive security patches. The Python 3.x.x version that you install following these instructions is the one you should use. To run Python 3.x.x, you should always use the `python3` command instead of `python`.

### Creating Environments with Python on Windows (Optional)
`python -m venv env`

`source env/Scripts/activate`

### Creating Environments with Python on MacOS (Optional)
`python3 -m venv env`

`source env/bin/activate`

### Installing required packages
`pip install -r requirements.txt`


## Run Project
`python main.py`

or

`python3 main.py`