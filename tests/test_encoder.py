from numpy import ndarray

from vidutil.encoder import VideoEncoder


class TestEncoder:
    def test_load_video(self):
        encoder = VideoEncoder()
        path = "assets/vsco.mp4"
        vid = encoder.load_video(path)
        assert len(vid) == 57
        for frame in vid:
            assert isinstance(frame, ndarray)
        assert encoder.get_fps(path) == 7.728813559322034

    def test_list_images(self):
        path = "assets/image-sequence"
        sequence = VideoEncoder.list_images(path)
        assert len(sequence) == 9
        for i in range(len(sequence)):
            assert sequence[i].name == f"im{i}.png"

    def test_load_images(self):
        path = "assets/image-sequence"
        frames = VideoEncoder.load_images(VideoEncoder.list_images(path))
        assert len(frames) == 9
        for frame in frames:
            assert isinstance(frame, ndarray)

    def test_ffmpeg_export_frames(self):
        path = "assets/image-sequence-2"
        VideoEncoder.ffmpeg_export_frames(f"{path}/im*.jpeg", "movie.mp4")

    def test_ffmpeg_export_frames(self):
        path = "assets/image-sequence-2"
        VideoEncoder.ffmpeg_export_frames(f"{path}/im*.jpeg", "movie.mp4")
