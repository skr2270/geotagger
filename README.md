# geotagger
The objective of this project is to embed EXIF data into extracted frames. Where the video file should have a .srt file

Open your Terminal or Command Prompt: Navigate to your project's directory.

Ensure you have Python installed: You can check this by running python --version or python3 --version. If Python is not installed, you'll need to install it first.

Create the Virtual Environment:

If you are using Python 3, you can create a virtual environment by running:
Copy code
python -m venv .venv
Alternatively, if your system differentiates between Python 2 and Python 3 with python and python3 commands, use:
Copy code
python3 -m venv .venv
Activate the Virtual Environment:

On Windows, run:
Copy code
.\.venv\Scripts\activate
On macOS and Linux, run:
bash
Copy code
source .venv/bin/activate
Install Required Packages:

Once the virtual environment is activated, you can install packages using pip. For your project, you might need opencv-python, pysrt, piexif, Pillow, and tqdm. Install them by running:
Copy code
pip install opencv-python pysrt piexif Pillow tqdm
Deactivate the Virtual Environment:

When you're done working in the virtual environment, you can deactivate it by simply running:
Copy code
deactivate
