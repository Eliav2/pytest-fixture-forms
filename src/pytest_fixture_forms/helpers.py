import pytest
from packaging import version

PYTEST_VERSION = version.parse(pytest.__version__)
IS_PYTEST7 = PYTEST_VERSION.major == 7
IS_PYTEST8 = PYTEST_VERSION.major == 8