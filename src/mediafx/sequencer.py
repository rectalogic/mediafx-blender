from __future__ import annotations
import os
import pathlib
import bpy
from .exceptions import SequencerError, OpsError
from .encoder import EncoderSettings
from . import sequences


class Sequencer:
    instance: Sequencer | None = None

    def __init__(self, encoder_settings: EncoderSettings | None = None):
        if Sequencer.instance is not None:
            raise SequencerError("Only one Sequencer can be active at a time, dispose of current Sequencer first")
        Sequencer.instance = self
        bpy.ops.wm.read_factory_settings(use_empty=True)
        if encoder_settings is None:
            encoder_settings = EncoderSettings()
        scene = bpy.context.scene
        render = scene.render
        scene.view_settings.view_transform = "Standard"
        render.image_settings.file_format = "FFMPEG"
        render.ffmpeg.format = encoder_settings.ffmpeg_format
        render.ffmpeg.codec = encoder_settings.ffmpeg_codec
        render.ffmpeg.audio_codec = encoder_settings.ffmpeg_audio_codec
        render.resolution_x = encoder_settings.resolution_x
        render.resolution_y = encoder_settings.resolution_y
        render.fps = encoder_settings.fps
        render.fps_base = encoder_settings.fps_base

    def encode(self, filepath: pathlib.Path):
        """Encode video to specified file using current encoder settings."""
        render = bpy.context.scene.render
        render.filepath = str(filepath)
        bpy.context.area.type = "SEQUENCE_EDITOR"
        OpsError.check(bpy.ops.sequencer.set_range_to_strips(), "Failed to set sequencer range")
        OpsError.check(bpy.ops.render.render(animation=True), "Failed to render")

    def save_blend(self, filepath: pathlib.Path):
        """Save as a Blender project 'blend' file (for debugging)."""
        if template := next(bpy.utils.app_template_paths(), None):
            bpy.ops.workspace.append_activate(idname="Video Editing", filepath=os.path.join(template, "Video_Editing/startup.blend"))
        OpsError.check(bpy.ops.wm.save_as_mainfile(filepath=str(filepath)), "Failed to save blend")

    def new_movie(self, filepath: pathlib.Path, channel: int, frame_start: int, fit_method: str = "FIT") -> sequences.MovieSequence:
        return sequences.MovieSequence(bpy.context.scene.sequence_editor.sequences.new_movie(
            name=filepath.name,
            filepath=str(filepath),
            channel=channel,
            frame_start=frame_start,
            fit_method=fit_method,
            # XXX add adjust_playback_rate
        ), self)
    
    def new_sound(self, filepath: pathlib.Path, channel: int, frame_start: int) -> sequences.SoundSequence:
        #XXX returns None if no sound but valid? need to handle in superclass
        return sequences.SoundSequence(bpy.context.scene.sequence_editor.sequences.new_sound(
            name=filepath.name,
            filepath=str(filepath),
            channel=channel,
            frame_start=frame_start,
        ), self)
    
    def dispose(self):
        if Sequencer.instance != self:
            raise SequencerError("Sequencer already disposed")
        Sequencer.instance = None