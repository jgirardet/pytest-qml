import sys

from src.pytestqml import __version__
from subprocess import run, PIPE


def tag():
    res = run(["git", "tag", __version__], stdout=PIPE, stderr=PIPE)
    print(res)


def install_qt():
    res = run("aqt install 5.15.1 linux desktop".split(" "), stdout=PIPE, stderr=PIPE)
    print(res)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("usage: tag, install_qt")
    elif sys.argv[1] == "tag":
        tag()
    elif sys.argv[1] == "install_qt":
        install_qt()
