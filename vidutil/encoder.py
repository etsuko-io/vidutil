import gc
import logging
import os
import os.path
from threading import Lock
from typing import List

import ffmpeg
import numpy as np
from cv2 import cv2
from numpy import ndarray

from vidutil.memory import get_current_memory

# logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)


class VideoEncoder:
    """
    This class exposes methods for opening, processing and saving a video.
    """

    lock = Lock()

    @staticmethod
    def load(path) -> List[ndarray]:
        # todo:
        #  - support multiple files
        #  - support multiple processes
        #  - support multiple threads
        #  - support logging time
        logger.debug(f"Loading file://{os.path.abspath(path)}")
        frames = []
        cap = cv2.VideoCapture(path)
        ret = True
        while ret:
            # read one frame from the 'capture' object; img is (H, W, C) [height width channels?]
            ret, img = cap.read()
            if ret:
                frames.append(img)
        logger.debug(get_current_memory())
        gc.collect()
        logger.debug("VideoEncoder.load - garbage collected")
        return frames

    @staticmethod
    def get_fps(path) -> float:
        # todo: verify it's not loaded into memory
        """
        Return the FPS of a video file without loading it in to memory
        :param path:
        :return:
        """
        return cv2.VideoCapture(path).get(cv2.CAP_PROP_FPS)

    @staticmethod
    def get_total_frames(path) -> int:
        return int(cv2.VideoCapture(path).get(cv2.CAP_PROP_FRAME_COUNT))

    @staticmethod
    def save(path: str, frames: List[np.array], fps: float, size: tuple) -> None:
        """
        Save video to disk
        :param path: path to save image to
        :param frames: list of numpy arrays, each representing a single video frame
        :param size: a tuple (width, height)
        :param fps: int
        :return:
        """
        # Options: mp4v, avc1
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        video = cv2.VideoWriter(path, fourcc, fps, size)
        # todo: how to optimize? maybe by using separate file+thread per 10 seconds of video?
        length = len(frames)
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
