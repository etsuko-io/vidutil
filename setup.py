from setuptools import find_packages, setup

setup(
    name="vidutil",
    version="0.0.5",
    packages=find_packages(include=["vidutil", "vidutil.*"]),
    install_requires=[
        "numpy",
        "opencv-contrib-python==4.5.5.64",
        "pygobject==3.38.0",
        "ffmpeg-python",
        "psutil",
    ],
)
