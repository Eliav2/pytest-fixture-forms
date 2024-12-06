import fnmatch
from typing import Iterable

from _pytest import fixtures, nodes
from _pytest.compat import safe_getattr
from _pytest.python import Module

from pytest_fixture_forms import FixtureForms


class CustomModule(Module):
    """
    Custom module to override the default behavior of pytest to collect tests. (allow test class names to start with lowercase 'test')
    this is essential because we replace at collection time certain function tests with class tests with the same name (and test functions regularly start with 'test_')
    This module also registers fixtures from FixtureForms classes at the collection time.
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

    def collect(self) -> Iterable[nodes.Item | nodes.Collector]:
        """ we want the collection to discover fixtures from FixtureForms classes as well """
        self._register_fixture_forms_fixtures()
        return super().collect()

    def _register_fixture_forms_fixtures(self):
        for name in dir(self.obj):
            obj_ub = safe_getattr(self.obj, name, None)
            if isinstance(obj_ub, type) and issubclass(obj_ub, FixtureForms) and obj_ub != FixtureForms:
                fixture_form_cls = obj_ub
                fixture_form_cls.perform_fixture_registration(self.session)
                # for form in fixture_form_cls.forms():
                #     for fixture_name, fixture in fixture_form_cls.get_form_fixtures(form).items():
                #         self.session._fixturemanager.add_fixture(fixture_name, fixture, self.obj)
                # obj = obj_ub()
                # for form in obj.forms:
                #     for fixture_name, fixture in obj.get_form_fixtures(form).items():
                #         self.session._fixturemanager.add_fixture(fixture_name, fixture, self.obj)

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
