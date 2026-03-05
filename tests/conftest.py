import pathlib
import pytest


FIXTURES_DIR = pathlib.Path(__file__).parent / "fixtures"


@pytest.fixture
def fixture_path():
    def _get(name):
        return str(FIXTURES_DIR / name)
    return _get
