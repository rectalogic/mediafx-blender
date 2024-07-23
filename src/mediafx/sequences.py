import abc
import typing as ta
import bpy
from .exceptions import InvalidSequenceError
if ta.TYPE_CHECKING:
    from .sequencer import Sequencer

# XXX lightweight wrapper with index (grab len(sequences))
# XXX for sound, just attempt to new_sound and it returns None if no audio
  #XXX new_movie on sound returns 1 frame clip with no size
  # SequenceElement has size, m.elements[0].orig_width

#XXX need a registry metaclass to map index to our class, so when we lookup bpy class we can return our proxy

#XXX hmm, should be using scene.sequence_editor.sequences_all ? yeah, it's all strips sequences is just toplevel
# deleting a clip will change indexes
# need a name for new_movie() etc. anyway, so generate one? (or let bpy generate) and save it



T = ta.TypeVar("T", bound=bpy.types.Sequence)


class Sequence(abc.ABC, ta.Generic[T]):
    name: str | None
    sequencer: Sequencer

    def __init__(self, seq: T, sequencer: Sequencer):
        self.name = seq.name
        self.sequencer = sequencer

    @property
    def sequence(self) -> T:
        if self.name is None or self.sequencer != self.sequencer.instance:
            raise InvalidSequenceError()
        try:
            return bpy.context.scene.sequence_editor.sequences_all[self.name]
        except KeyError:
            self.name = None
            raise InvalidSequenceError()

    @property
    def channel(self) -> int:
        return self.sequence.channel
    
    @property
    def duration(self) -> int:
        return self.sequence.frame_duration


class MovieSequence(Sequence[bpy.types.MovieSequence]):
    pass


class SoundSequence(Sequence[bpy.types.SoundSequence]):
    pass