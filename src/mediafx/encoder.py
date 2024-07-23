import os
import dataclasses
import pathlib
import bpy


@dataclasses.dataclass
class EncoderSettings:
    resolution_x: int = 640
    resolution_y: int = 360
    fps: int = 25
    fps_base: int = 1
    ffmpeg_format: str = "MPEG4"
    ffmpeg_codec: str = "H264"
    ffmpeg_audio_codec: str = "AAC"


