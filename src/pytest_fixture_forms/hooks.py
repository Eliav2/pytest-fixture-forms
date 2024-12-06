"""
hooks in this file are used to:
    - dynamically register fixtures based on classes that inherent from FixtureForms (see register() call in pytest_collection)
    - dynamically generate test nodes per each combination of parameters for tests that uses fixtures generated from FixtureForms inheritance (see pytest_pycollect_makeitem)
      - each test node is synthetically created with correct required arguments(which are fixtures) that suit the combination of parameters(see create_dynamic_function)
"""

import inspect
from itertools import product

from _pytest.python import Class, Package, Module
import pytest
from _pytest.main import Session

from pytest_fixture_forms.FixtureForms import FixtureForms
from pytest_fixture_forms.CustomModule import CustomModule
from pytest_fixture_forms.utils import (
    _get_direct_requested_fixtures,
    _get_dependent_fixtures,
    get_original_params_from_callspecs,
    create_dynamic_function, )


# special_params_fixtures = {}

# def pytest_collection(session):
#     """Called during collection before test items are created"""
#     pytest_internals["fixturemanager"] = session._fixturemanager
#     if not hasattr(session, "_notfound"):
#         session._notfound = []
#     test_items = _get_test_functions(session)
#     # pytest_internals["_original_test_items"] = (
#     #     test_items  # the test items that originally collected (they would be replaced by the dynamic tests)
#     # )
#     for cls in FixtureForms.__subclasses__():
#         if hasattr(cls, "_pending_fixture_registrations"):
#             for register in cls._pending_fixture_registrations:
#                 register(session, **{})
#     pytest_internals["session"] = session
#     fixturedefs = session._fixturemanager._arg2fixturedefs
#
#     for name, defs in fixturedefs.items():
#         if defs:  # Take the last fixturedef as it overrides previous ones
#             fixdef = defs[-1]
#             fixture_registry[name] = {"ids": fixdef.ids, "scope": fixdef.scope, "params": fixdef.params}
#
#     # direct_requested_fixtures = _get_direct_requested_fixtures([test_item._obj for test_item in test_items])
#     # requested_fixtures = _get_dependent_fixtures(direct_requested_fixtures, fixturedefs)
#     pytest_internals["test_items"] = test_items
#     # pytest_internals["requested_fixtures"] = requested_fixtures
#     pytest_internals["fixturedefs"] = fixturedefs
#
#
#     for cls in FixtureForms.__subclasses__():
#         special_params_fixtures[cls.get_instance_fixture_name()] = cls
#     # pytest_internals["special_params_fixtures"] = special_params_fixtures


# def pytest_configure(config):
#     """Pytest hook to discover and register fixtures before collection."""
#     registry = FixtureFormsRegistry.get_instance()
#     registry.discover_subclasses()

# @pytest.hookimpl(wrapper=True)
# def pytest_collection(session:Session):
#     # for cls in FixtureForms.__subclasses__():
#     #     special_params_fixtures[cls.get_instance_fixture_name()] = cls
#     #     if hasattr(cls, "_pending_fixture_registrations"):
#     #         for register in cls._pending_fixture_registrations:
#     #             register(session, **{})
#
#     # registry = FixtureFormsRegistry.get_instance()
#     # registry.discover_subclasses_from_session(session)
#     # registry.execute_registrations(session)
#
#     FixtureForms._register_pending_fixtures(session)
#
#     # return (yield)
#     # before=FixtureForms.__subclasses__()
#     test_items = yield
#     FixtureForms._register_pending_fixtures(session)
#
#     return test_items
#     # pytest_internals["test_items"] = _get_test_functions(session)
#     # pytest_internals["fixturemanager"] = session._fixturemanager
#     # if not hasattr(session, "_notfound"):
#     #     session._notfound = []
#     # test_items = _get_test_functions(session)
#     # pytest_internals["_original_test_items"] = (
#     #     test_items  # the test items that originally collected (they would be replaced by the dynamic tests)
#     # )
#
#     # pytest_internals["session"] = session
#     # fixturedefs = session._fixturemanager._arg2fixturedefs
#     #
#     # for name, defs in fixturedefs.items():
#     #     if defs:  # Take the last fixturedef as it overrides previous ones
#     #         fixdef = defs[-1]
#     #         fixture_registry[name] = {"ids": fixdef.ids, "scope": fixdef.scope, "params": fixdef.params}
#
#     # direct_requested_fixtures = _get_direct_requested_fixtures([test_item._obj for test_item in test_items])
#     # requested_fixtures = _get_dependent_fixtures(direct_requested_fixtures, fixturedefs)
#     # if not hasattr(session, "_notfound"):
#     #     session._notfound = []
#     # pytest_internals["test_items"] = _get_test_functions(session)
#     # pytest_internals["requested_fixtures"] = requested_fixtures
#     # pytest_internals["fixturedefs"] = fixturedefs
#
#     # for cls in FixtureForms.__subclasses__():
#     #     special_params_fixtures[cls.get_instance_fixture_name()] = cls
#     # pytest_internals["special_params_fixtures"] = special_params_fixtures
#
#     # return test_items

# @pytest.hookimpl(tryfirst=True)
# def pytest_import_module(path, mod):
#     pass
# @pytest.hookimpl(tryfirst=True)
# def pytest_plugin_registered(plugin):
#     pass

@pytest.hookimpl(wrapper=True)
def pytest_pycollect_makeitem(collector, name, obj):
    # print(
    #     f"Called with: collector={collector.__class__.__name__}, name={name}, obj={obj.__class__.__name__ if hasattr(obj, '__class__') else type(obj)}"
    # )

    # if isinstance(collector, Class) and issubclass(collector.cls, TestBaseCaseV2):

    # ignore items being collected before pytest_collection hook is completed
    res = yield

    # it's important to check if the function because our plugin is interested only in the last leaf test function,
    # while a pytest istestfunction would also accept a class method
    if (collector.istestfunction(obj, name) and inspect.isfunction(obj)):

        session = collector.session
        fixturedefs = session._fixturemanager._arg2fixturedefs
        if not fixturedefs:
            return res
        _original_test = obj
        if hasattr(_original_test, "__fixture_form_dynamically_generated"):
            # don't recurse into dynamically generated tests
            return res
        _original_test_items = res
        # test_items = _get_test_functions(session)
        # if "fixturedefs" not in pytest_internals:
        #     return None
        # store the original test for later use
        # _original_test = getattr(collector.cls, name)
        # _original_test_items = [
        #     test_item for test_item in test_items if test_item.originalname == name
        # ]
        if not _original_test_items:
            return res
        first_test_item = _original_test_items[0]
        test_marks = first_test_item.own_markers
        # recreation of parameters that were originally passed to the test (closely)
        original_parameterized_params_vals = get_original_params_from_callspecs(
            [test_item.callspec for test_item in _original_test_items if hasattr(test_item, "callspec")]
        )
        # fixturedefs = collector.session._fixturemanager._arg2fixturedefs
        # fixturedefs = pytest_internals["fixturedefs"]
        # special_params_instances_fixtures = pytest_internals["special_params_fixtures"]
        special_params_instances_fixtures = FixtureForms.special_params_fixtures
        # special_params_instances_fixtures = special_params_fixtures
        direct_requested_fixtures = _get_direct_requested_fixtures([obj])
        requested_fixtures = _get_dependent_fixtures(direct_requested_fixtures, fixturedefs)
        params2formsMap = {}
        for fixture_name in requested_fixtures:
            if fixture_name in special_params_instances_fixtures:
                cls = special_params_instances_fixtures[fixture_name]
                form_fixture_name = cls.get_form_fixture_name()
                default_params = fixturedefs[form_fixture_name][-1].params
                final_wanted_forms = original_parameterized_params_vals.get(form_fixture_name, default_params)
                params2formsMap[cls] = final_wanted_forms
        if not params2formsMap:
            # no special params fixtures were requested
            return res
        class_names = list(params2formsMap.keys())
        combinations = product(*params2formsMap.values())
        labeled_combinations = [tuple(zip(class_names, combo)) for combo in combinations]

        methods = {}
        original_args = list(inspect.signature(_original_test).parameters.keys())

        for params in labeled_combinations:
            required_fixtures = set()
            parameterized_vals = original_parameterized_params_vals.copy()
            # add args from original test
            for cls, form in params:
                # the forms fixture is required for each node
                required_fixtures.add(cls.get_form_fixture_name())
                # require the correct form fixture for each node
                required_fixtures.add(cls.get_form_value_fixture_name(form))

            test_name = "_".join([f"{cls.__name__}_{form}" for cls, form in params])

            args_to_remove = set()

            for cls, form in params:
                # override original_parameterized_params_vals with the values relevant to this node (no need to request all forms)
                form_fixture_name = cls.get_form_fixture_name()
                parameterized_vals[form_fixture_name] = [form]
                # only relevant owners should be requested
                owners_fixtures = [cls.get_form_owner_fixture_name(form) for form in cls.forms()]
                current_owner_fixture = cls.get_form_owner_fixture_name(form)
                for p in parameterized_vals.copy():
                    if p in owners_fixtures and p != current_owner_fixture:
                        del parameterized_vals[p]
                for p in requested_fixtures:
                    if p in owners_fixtures and p != current_owner_fixture:
                        args_to_remove.add(p)

            def create_test_function(args_to_remove):
                def impl(args: dict, required_params):
                    # fill irrelevant args with None
                    for arg in args_to_remove:
                        args[arg] = None
                    if isinstance(collector, Module):
                        # self does not exist in the original test function(but was injected by pytest, we remove it before calling the original test)
                        del args["self"]
                    _original_test(**args)

                final_args = [arg for arg in original_args if arg not in args_to_remove]
                if isinstance(collector, Module):
                    # in case it's a function defined in a module, we need to add the self argument, because previously it was normal function, now it's a method under a class so pytest is going to inject the self argument as the first argument
                    final_args = ["self"] + final_args
                _required_fixtures = [fixture for fixture in required_fixtures if fixture not in args_to_remove]
                return create_dynamic_function(
                    final_args,
                    impl,
                    required_params=list(required_fixtures),
                )

            test_func = create_test_function(args_to_remove)

            for _name, param_config in parameterized_vals.items():
                mark = next((mark for mark in test_marks if mark.args and mark.args[0] == _name), None)
                kwargs = mark.kwargs if mark else {}
                # parameterize each node with the relevant values
                test_func = pytest.mark.parametrize(_name, parameterized_vals[_name], **kwargs)(test_func)

            setattr(test_func, "__fixture_form_dynamically_generated", test_name)
            methods[f"test_{test_name}"] = test_func

        # Create new class named after the original test
        class_name = name
        DynamicTestClass = type(
            class_name,
            (),
            methods,
        )
        # for modules, we replace the original test func with the new class,
        # for test classes we replace the method with the new class
        collector_node = (
            collector.cls
            if isinstance(collector, Class)
            else (
                collector.module
                if isinstance(collector, Module)
                # should not happen(if it does, its a bug)
                else NotImplementedError("Unsupported collector type")
            )
        )
        # Add the class to the module/class
        setattr(collector_node, name, DynamicTestClass)

        # Create a Class collector for our new class
        new_class_collector = Class.from_parent(
            parent=collector,
            name=DynamicTestClass.__name__,
            obj=DynamicTestClass,
        )

        # return list(new_class_collector.collect())
        return new_class_collector

    return res


def pytest_pycollect_makemodule(module_path, parent):
    if module_path.name == "__init__.py":
        pkg: Package = Package.from_parent(parent, path=module_path)
        return pkg
    mod: CustomModule = CustomModule.from_parent(parent, path=module_path)
    return mod


def pytest_make_parametrize_id(config, val, argname):
    """Hook for generating test IDs for parametrized tests"""
    return f"{argname}:{val}"
