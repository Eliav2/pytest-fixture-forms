import pytest
from packaging import version

PYTEST_VERSION = version.parse(pytest.__version__)
IS_PYTEST7 = PYTEST_VERSION.major == 7
IS_PYTEST8 = PYTEST_VERSION.major == 8
def skip_if_not_pytest7(reason="Test only applicable for pytest 7"):
    return pytest.mark.skipif(not IS_PYTEST7, reason=reason)

def skip_if_not_pytest8(reason="Test only applicable for pytest 8"):
    return pytest.mark.skipif(not IS_PYTEST8, reason=reason)

# Helper functions for version-specific behavior
def get_collection_items(session):
    """Get collection items in a version-compatible way"""
    if IS_PYTEST7:
        return session.perform_collect()
    else:
        return session.collect()  # pytest 8+ way