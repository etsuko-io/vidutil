import gc
import logging
import os
import os.path
from os.path import join, isdir, isfile, abspath
from pathlib import Path
from threading import Lock
from typing import List, Union, Tuple, Optional

import ffmpeg
import numpy as np
from cv2 import cv2
from numpy import ndarray

from vidutil.memory import get_current_memory

# logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s[%(lineno)d]: %(message)s"
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)


class VideoEncoder:
    """
    This class exposes methods for opening, processing and saving a video.
    """

    lock = Lock()

    @staticmethod
    def load_video(path) -> List[ndarray]:
        """
        Load a video into memory as single frames.
        :param path: path to video file
        :return: list of frames
        """
        # todo:
        #  - support multiple files
        #  - support multiple processes
        #  - support multiple threads
        #  - support logging time
        #  - add check if path exists

        logger.debug(f"Loading file://{os.path.abspath(path)}")
        frames = []
        cap = cv2.VideoCapture(path)
        ret = True
        while ret:
            # read one frame from the 'capture' object;
            # img is (H, W, C) [height width channels?]
            ret, img = cap.read()
            if ret:
                frames.append(img)
        logger.debug(f"Memory usage: {get_current_memory()} MB")
        gc.collect()
        logger.debug("Garbage collected")
        logger.debug(f"New memory usage: {get_current_memory()} MB")
        return frames

    @staticmethod
    def list_images(path: Union[str, Path], extensions=None) -> List[Path]:
        if not extensions:
            extensions = [".png", ".jpg", ".jpeg", ".tif", ".tiff"]
        if not isdir(path):
            raise ValueError(f"{path} is not a directory")
        paths = sorted(
            [
                abspath(join(path, f))
                for f in os.listdir(path)
                if not f.startswith(".")
                and isfile(join(path, f))
                and Path(f).suffix in extensions
            ],
            key=str.lower,
        )
        return [Path(p) for p in paths]

    @staticmethod
    def load_images(paths: List[Union[str, Path]]) -> List[ndarray]:
        frames = []
        for p in paths:
            if isinstance(p, Path):
                frames.append(cv2.imread(p.as_posix()))
            else:
                frames.append(cv2.imread(p))

        return frames

    @staticmethod
    def get_fps(path: Union[str, Path]) -> float:
        # todo: verify it's not loaded into memory
        """
        Return the FPS of a video file without loading it in to memory
        :param path: path to video
        :return:
        """
        return cv2.VideoCapture(path).get(cv2.CAP_PROP_FPS)

    @staticmethod
    def get_total_frames(path: Union[str, Path]) -> int:
        return int(cv2.VideoCapture(path).get(cv2.CAP_PROP_FRAME_COUNT))

    @staticmethod
    def save(
        path: str,
        frames: List[np.array],
        fps: float,
        size: Optional[Tuple[int, int]] = None,
        codec: Union[str, int] = "mp4v",
    ) -> None:
        """
        Save video to disk
        :param path: path to save image to
        :param frames: list of numpy arrays, each representing a single video frame
        :param size: a tuple (width, height); calculated based on first frame if
         not provided
        :param fps: float
        :param codec: string codec with a supported opencv value. Defaults to mp4v
        :return:
        """
        # Some options:
        # - mp4v (MPEG-4/.mp4)
        # - avc1 (h264)
        # - hvc1 (HVEC, .avi) works in VLC, quality seems fine
        # https://gist.github.com/takuma7/44f9ecb028ff00e2132e
        if isinstance(codec, str):
            fourcc = cv2.VideoWriter_fourcc(*codec)
        else:
            # allow ints as opencv uses them for certain special codec behaviour:
            #  -1 (showing available codecs),
            #  0  (exporting images)
            fourcc = codec

        if not size:
            size = frames[0].shape[1::-1]
        video = cv2.VideoWriter(path, fourcc, fps, size)
        # todo: how to optimize? maybe by using separate
        #  file+thread per 10 seconds of video?
        length = len(frames)

        # todo: verify width/height of each frame with provided w/h.
        #  If it's swapped for example,
        #  it will result in a <1KB file that can't be opened.
        for i, frame in enumerate(frames):
            # todo: make percentage available to invoker of method
            percentage = round((i + 1) / length * 100, 2)
            logger.debug(percentage)
            video.write(frame)

        video.release()

        logger.info(get_current_memory())
        del video
        gc.collect()
        logger.info("VideoEncoder.save - garbage collected")
        logger.info(f"saved to file://{os.path.abspath(path)}")
        logger.info(get_current_memory())

    @staticmethod
    def merge_av(audio_path, video_path, output_path):
        if not audio_path:
            logger.info("no audio provided")
        if not video_path:
            logger.info("no video provided")
            return
        logger.debug(f"Merging audio and video: \n a: {audio_path} \n v: {video_path}")
        audio = ffmpeg.input(audio_path).audio
        video = ffmpeg.input(video_path).video
        out = ffmpeg.output(
            audio,
            video,
            output_path,
            vcodec="copy",
            acodec="aac",
            strict="experimental",
        )
        out.run()
        logger.info(f"saved to file://{os.path.abspath(output_path)}")

        logger.info(get_current_memory())

    @staticmethod
    def ffmpeg_export_frames(
        input_path: str, output_path: str, pattern_type: str = "glob", fps: float = 25
    ):
        (
            ffmpeg.input(input_path, pattern_type=pattern_type, framerate=fps)
            .output(output_path)
            .run(overwrite_output=True)
        )
