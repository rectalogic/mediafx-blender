from __future__ import annotations
import typing as ta
import typing_extensions as tx
import abc
import bpy


# XXX lightweight wrapper with index (grab len(sequences))
# XXX for sound, just attempt to new_sound and it returns None if no audio
  #XXX new_movie on sound returns 1 frame clip with no size
  # SequenceElement has size, m.elements[0].orig_width

#XXX need a registry metaclass to map index to our class, so when we lookup bpy class we can return our proxy

#XXX hmm, should be using scene.sequence_editor.sequences_all ? yeah, it's all strips sequences is just toplevel
# deleting a clip will change indexes
# need a name for new_movie() etc. anyway, so generate one? (or let bpy generate) and save it

#XXX should we store reference to the underlying Sequence, and expose it? and then expose extra helpers as needed?
#XXX Sequencer can maintain dict of "known" sequences it created - mapping between the 2 (wrapper and native)

#XXX what is purpose of Transform effect strip? we can keyframe transform of the video strip itself
# > version 2.9.2 put Scale and Position properties directly into the strip properties such that creating a Transform strip was no longer necessary for these simple transformations
# https://www.reddit.com/r/blenderhelp/comments/mxvpr7/vse_smooth_scaling_animation_with_keyframes/
# Transform allows percentages for offsets

# Sequence should be generic so subclasses return the correct bpy.types.Sequence subtype
# But this crashes bpy https://projects.blender.org/blender/blender/issues/125376


class Sequence(abc.ABC):
    _registry: dict[ta.Class[bpy.types.Sequence], ta.Class[Sequence]] = {}

    def __init_subclass__(cls, /, bpy_type: ta.Class[bpy.types.Sequence], **kwargs):
        super().__init_subclass__(**kwargs)
        cls._registry[bpy_type] = cls

    def __init__(self, sequence: bpy.types.Sequence):
        self._sequence = sequence

    @classmethod
    def new(cls, sequence: bpy.types.Sequence) -> Sequence:
        return cls._registry[type(sequence)](sequence)

    @property
    def sequence(self) -> bpy.types.Sequence:
        return self._sequence


class MovieSequence(Sequence, bpy_type=bpy.types.MovieSequence):
    @tx.override
    @classmethod
    def new(cls, sequence: bpy.types.MovieSequence) -> MovieSequence:
        ...

    @tx.override
    @property
    def sequence(self) -> bpy.types.MovieSequence:
        ...


class SoundSequence(Sequence, bpy_type=bpy.types.SoundSequence):
    @tx.override
    @classmethod
    def new(cls, sequence: bpy.types.SoundSequence) -> SoundSequence:
        ...

    @tx.override
    @property
    def sequence(self) -> bpy.types.SoundSequence:
        ...