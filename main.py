import sys

from resources.lib import color


def _do_action():
    if len(sys.argv) > 1:
        _params = sys.argv[1:]
        params = {i[0]: i[1] for i in [j.split("=") for j in _params]}
        action = params.get("action", None)

        if action == "color_picker":
            color.color_picker()


if __name__ == "__main__":
    _do_action()
