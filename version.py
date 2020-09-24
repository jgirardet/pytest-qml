from pytestqml import __version__
from subprocess import run, PIPE


def tag():
    run(["git", "tag", __version__], stdout=PIPE, stderr=PIPE)
