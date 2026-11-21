#!/usr/bin/env python3
"""Entrypoint: copy the built front page to the grader's output dir.

The image is drawn at build time by draw_news.py and committed as
entry.png; this program only copies those exact bytes, so two runs
always write identical output. Standard library only, no network.
"""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    src = os.path.join(HERE, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(src, os.path.join(out_dir, "entry.png"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
