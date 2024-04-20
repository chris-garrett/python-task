import os
import config  # noqa
import pytest

from __tasklib__ import load_dotenv


def test_load_default_dotenv():
    load_dotenv()

    assert os.getenv("COLOR") == "green"
    assert os.getenv("EVENT") == "storm"
    assert os.getenv("KEY1") == "value1"
    assert os.getenv("NAME") == "taylor       # include comment"


def test_load_expanded_dotenv():
    load_dotenv()
    load_dotenv(".env.expanded")

    assert os.getenv("EXPAND_COLOR") == "green"
    assert os.getenv("EXPAND_EVENT") == "storm"
    assert os.getenv("EXPAND_KEY1") == "value1"
    assert os.getenv("EXPAND_NAME") == "taylor       # include comment"


def test_load_no_overwrite_dotenv():
    load_dotenv()
    load_dotenv(".env.overwrite")

    assert os.getenv("COLOR") == "green"
    assert os.getenv("EVENT") == "storm"
    assert os.getenv("KEY1") == "value1"
    assert os.getenv("NAME") == "taylor       # include comment"


def test_load_overwrite_dotenv():
    load_dotenv()
    load_dotenv(".env.overwrite", override=True)

    assert os.getenv("COLOR") == "blue"
    assert os.getenv("EVENT") == "clear"
    assert os.getenv("KEY1") == "1eulav"
    assert os.getenv("NAME") == "swifty       # include comment"
