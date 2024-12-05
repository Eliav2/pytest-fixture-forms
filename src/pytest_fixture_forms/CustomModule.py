import fnmatch

from _pytest import fixtures
from _pytest.compat import safe_getattr
from _pytest.python import Module


class CustomModule(Module):
    """
    Custom module to override the default behavior of pytest to collect tests. (allow test class names to start with lowercase 'test')
    this is essential because we replace at collection time certain function tests with class tests with the same name (and test functions regularly start with 'test_')
    """

    def _matches_prefix_or_glob_option(self, option_name: str, name: str) -> bool:
        """Check if the given name matches the prefix or glob-pattern defined
        in ini configuration."""
        for option in self.config.getini(option_name):
            # allow test class names to start with lowercase 'test'
            if name.startswith(option) or name.lower().startswith(option.lower()):
                return True
            # Check that name looks like a glob-string before calling fnmatch
            # because this is called for every name in each collected module,
            # and fnmatch is somewhat expensive to call.
            elif ("*" in option or "?" in option or "[" in option) and fnmatch.fnmatch(name, option):
                return True
        return False

    # def istestfunction(self, obj: object, name: str) -> bool:
    #     """Override to change class name convention"""
    #     if self.funcnamefilter(name) or self.isnosetest(obj):
    #         if isinstance(obj, (staticmethod, classmethod)):
    #             # staticmethods and classmethods need to be unwrapped.
    #             obj = safe_getattr(obj, "__func__", False)
    #         return callable(obj) and fixtures.getfixturemarker(obj) is None
    #     else:
    #         return False
    #
    # def istestclass(self, obj: object, name: str) -> bool:
    #     """Override to change function name convention"""
    #     return self.classnamefilter(name) or self.isnosetest(obj)
