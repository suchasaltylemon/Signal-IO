import os.path
import sys

LOADER = object()

include_path = os.path.abspath(os.path.dirname(__file__))

sys.path.append(include_path)
