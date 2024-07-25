import pathlib
import pytest
from mediafx.sequencer import Sequencer
from mediafx import sequences


@pytest.fixture
def sequencer():
    sequencer = Sequencer()
    yield sequencer
    sequencer.dispose()


def fixture(name):
    return pathlib.Path(__file__).parent / "fixtures/assets" / name


def test_movie_sequence(sequencer):
    seq = sequencer.new_movie(fixture("bbbjumprope-320x180-15fps-5.5s-44100.nut"), 1, 1)
    assert type(seq) is sequences.MovieSequence
    assert seq.sequence.channel == 1


def test_sound_sequence(sequencer):
    seq = sequencer.new_sound(fixture("bbbjumprope-320x180-15fps-5.5s-44100.nut"), 1, 1)
    assert type(seq) is sequences.SoundSequence
    assert seq.sequence.channel == 1
