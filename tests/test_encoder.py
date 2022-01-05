from numpy import ndarray

from vidutil.encoder import VideoEncoder


def test_encoder():
    encoder = VideoEncoder()
    path = "assets/vsco.mp4"
    vid = encoder.load(path)
    assert len(vid) == 57
    for frame in vid:
        assert isinstance(frame, ndarray)
    assert encoder.get_fps(path) == 7.728813559322034
