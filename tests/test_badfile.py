import tempfile
import pathlib
import pytest
from mediafx.sequencer import Sequencer


@pytest.fixture
def sequencer():
    sequencer = Sequencer()
    yield sequencer
    sequencer.dispose()


@pytest.fixture
def bad_filepath():
    with tempfile.NamedTemporaryFile(suffix=".mp4") as f:
        f.write(b"\000\000\000\000")
        yield pathlib.Path(f.name)


def test_bad_movie_sequence(sequencer, bad_filepath):
    with pytest.raises(RuntimeError) as exc_info:
        seq = sequencer.new_movie(bad_filepath, 1, 1)
        assert exc_info.match(r"could not be loaded")


def test_bad_sound_sequence(sequencer, bad_filepath):
    with pytest.raises(RuntimeError) as exc_info:
        seq = sequencer.new_sound(bad_filepath, 1, 1)
        assert exc_info.match(r"could not be loaded")