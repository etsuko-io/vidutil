from setuptools import setup, find_packages

setup(
    name="vidutil",
    version="0.0.2",
    packages=find_packages(include=["vidutil", "vidutil.*"]),
    install_requires=[
        "numpy",
        "opencv-python-headless>=4.5.5.62,<5.0.0",
        "pygobject==3.38.0",
        "ffmpeg-python",
        "psutil",
    ],
)
