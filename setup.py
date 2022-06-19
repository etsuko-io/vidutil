from setuptools import find_packages, setup

setup(
    name="vidutil",
    version="0.0.3",
    packages=find_packages(include=["vidutil", "vidutil.*"]),
    install_requires=[
        "numpy",
        "opencv-python-headless>=4.5.5.62,<5.0.0",
        "pygobject==3.38.0",
        "ffmpeg-python",
        "psutil",
    ],
)
