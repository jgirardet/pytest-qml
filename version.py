from src.pytestqml import __version__
from subprocess import run, PIPE


def tag():
    res = run(["git", "tag", __version__], stdout=PIPE, stderr=PIPE)
    print(res)


if __name__ == "__main__":
    tag()
