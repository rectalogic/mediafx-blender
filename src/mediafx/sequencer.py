from __future__ import annotations
from contextlib import contextmanager
import os
import pathlib
import bpy
from .exceptions import SequencerError, OpsError
from .encoder import EncoderSettings
from . import sequences


def switch_to_sequencer_workspace() -> bool:
    idname = "Video Editing"
    result: set | None = None
    for template in bpy.utils.app_template_paths():
        result = bpy.ops.workspace.append_activate(
            idname=idname, filepath=os.path.join(template, "Video_Editing/startup.blend")
        )
        if result == {"FINISHED"}:
            break
    if result != {"FINISHED"}:
        for template_path in bpy.utils.app_template_paths():
            for p in pathlib.Path(template_path).rglob("startup.blend"):
                result = bpy.ops.workspace.append_activate(idname=idname, filepath=str(p))
                if result == {"FINISHED"}:
                    break
            if result == {"FINISHED"}:
                break
    return result == {"FINISHED"}


def configure_encoder(encoder_settings: EncoderSettings | None):
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


@contextmanager
def area_override(area_type: str):
    area = next((area for area in bpy.context.screen.areas if area.type == area_type), None)
    if area is None:
        area = bpy.context.screen.areas[0]
        area.type = area_type
    with bpy.context.temp_override(area=area):
        yield


class Sequencer:
    instance: Sequencer | None = None

    def __init__(self, encoder_settings: EncoderSettings | None = None):
        if Sequencer.instance is not None:
            raise SequencerError(
                "Only one Sequencer can be active at a time, dispose of current Sequencer first"
            )
        Sequencer.instance = self
        bpy.ops.wm.read_factory_settings(use_empty=True)

        switch_to_sequencer_workspace()
        configure_encoder(encoder_settings)

    def encode(self, filepath: pathlib.Path):
        """Encode video to specified file using current encoder settings."""
        render = bpy.context.scene.render
        render.filepath = str(filepath)
        with area_override("SEQUENCE_EDITOR"):
            OpsError.check(bpy.ops.sequencer.set_range_to_strips(), "Failed to set sequencer range")
            OpsError.check(bpy.ops.render.render(animation=True), "Failed to render")

    def save_blend(self, filepath: pathlib.Path):
        """Save as a Blender project 'blend' file (for debugging)."""
        if template := next(bpy.utils.app_template_paths(), None):
            bpy.ops.workspace.append_activate(
                idname="Video Editing", filepath=os.path.join(template, "Video_Editing/startup.blend")
            )
        OpsError.check(bpy.ops.wm.save_as_mainfile(filepath=str(filepath)), "Failed to save blend")

    def new_movie(
        self, filepath: pathlib.Path, channel: int, frame_start: int = 0, fit_method: str = "FIT"
    ) -> sequences.MovieSequence:
        # bpy.context.scene.sequence_editor.sequences.new_movie() does not support adjust_playback_rate,
        # and sets SeqLoadData.allow_invalid_file=true - so we use ops
        with area_override("SEQUENCE_EDITOR"):
            index = len(bpy.context.scene.sequence_editor.sequences_all)
            OpsError.check(
                bpy.ops.sequencer.movie_strip_add(
                    filepath=str(filepath),
                    relative_path=False,
                    show_multiview=False,
                    frame_start=frame_start,
                    channel=channel,
                    fit_method=fit_method,
                    set_view_transform=False,
                    adjust_playback_rate=True,
                    use_framerate=False,
                    overlap=True,
                    sound=False,
                ),
                "Failed to load movie",
            )
            return sequences.MovieSequence(
                bpy.context.scene.sequence_editor.sequences_all[index],
                self,
            )

    def new_sound(self, filepath: pathlib.Path, channel: int, frame_start: int = 0, mono: bool = False) -> sequences.SoundSequence:
        with area_override("SEQUENCE_EDITOR"):
            index = len(bpy.context.scene.sequence_editor.sequences_all)
            OpsError.check(
                bpy.ops.sequencer.sound_strip_add(
                    filepath=str(filepath),
                    relative_path=False,
                    frame_start=frame_start,
                    channel=channel,
                    overlap=True,
                    mono=mono,
                ),
                "Failed to load sound",
            )
            return sequences.SoundSequence(
                bpy.context.scene.sequence_editor.sequences_all[index],
                self,
            )

    def dispose(self):
        if Sequencer.instance != self:
            raise SequencerError("Sequencer already disposed")
        Sequencer.instance = None
