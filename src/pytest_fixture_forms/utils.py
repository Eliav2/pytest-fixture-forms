import inspect
import re
from inspect import Parameter, Signature
from typing import Iterable, Callable

from _pytest.fixtures import FixtureDef
from _pytest.python import Function

from pytest_fixture_forms.runtime import pytest_internals


def create_dynamic_function(original_params: list[str | Parameter], func_impl, *, required_params: list[str] = None):
    """
    Create a function with dynamic parameter names.

    Args:
        original_params: List of parameter names
        func_impl: Function that receives a dict of {param_name: param_value} and implements the logic

    Returns:
        A function with the specified parameter names that delegates to func_impl

    >>># Usage examples:
    >>>def example1():
    >>>    # Example 1: Simple function that sums its arguments
    >>>    def impl(args: dict):
    >>>        return sum(args.values())
    >>>
    >>>    # Create function with dynamic param names
    >>>    func = create_dynamic_function(['a', 'b', 'c'], impl)
    >>>    result = func(1, 2, 3)  # calls impl with {'a': 1, 'b': 2, 'c': 3}
    >>>    print(result)  # 6
    """
    # Create parameters
    if required_params is None:
        required_params = []
    parameters = [
        Parameter(param, Parameter.POSITIONAL_OR_KEYWORD) if isinstance(param, str) else param
        for param in original_params
    ]
    original_param_names = [p.name for p in parameters]
    for param in required_params:
        if param not in original_param_names:
            parameters.append(
                Parameter(
                    param,
                    Parameter.POSITIONAL_OR_KEYWORD,
                )
            )

    # Create the function with proper signature
    def dynamic_func(*args, **kwargs):
        # Bind the arguments to parameter names
        bound_args = Signature(parameters).bind(*args, **kwargs)
        bound_args.apply_defaults()
        # if required params requested, pass them as second argument to impl func
        if required_params:
            required_bound_args = {}
            for arg in bound_args.arguments.copy():
                if arg in required_params:
                    required_bound_args[arg] = bound_args.arguments[arg]
                    if arg not in original_param_names:
                        del bound_args.arguments[arg]
            return func_impl(bound_args.arguments, required_bound_args)
        # Call the implementation with args dict
        return func_impl(bound_args.arguments)

    # Set the signature on the function
    dynamic_func.__signature__ = Signature(parameters)
    return dynamic_func


def _get_parametrized_values_for_fixture(test_items, fixture_name) -> list:
    """
    this function is used to get the parameters for a specific fixture that was parametrized`
    """
    # callspecs = [getattr(test_item, "callspec") in test_items for test_item in test_items if hasattr(test_item, "callspec")]
    # return  get_original_params_from_callspecs(callspecs).get(fixture_name, [])
    values = []
    for test_item in test_items:
        test_item_callspec = getattr(test_item, "callspec", None)
        if not test_item_callspec:
            continue
        for param_name, param_value in test_item_callspec.params.items():
            if param_name == fixture_name:
                values.append(param_value)
    return values


def _get_parametrized_params_for_test(callspecs) -> dict:
    params_final = {}
    params = callspecs[0].params
    for param_name, param_value in params.items():
        values = [callspec.params[param_name] for callspec in callspecs]
        params_final[param_name] = values
    return params_final


def get_original_params_from_callspecs(callspecs):
    result = {}
    if len(callspecs) == 0:
        return result
    first_spec = callspecs[0]

    for param in first_spec.params:
        # Get all values for this param looking at the _idlist
        param_ids = set()
        values = []

        for spec in callspecs:
            # Find the id for this param in _idlist
            param_id = next(id for id in spec._idlist if id.startswith(f"{param}:"))
            if param_id not in param_ids:
                param_ids.add(param_id)
                values.append(spec.params[param])

        result[param] = values

    return result


def _get_final_parametrized_values_for_fixture(fixturedefs, test_items, fixture_name) -> list:
    """first check for runtime values(passed as parametrized values to the test node, and if not provided get the values from the fixture definition"""
    # values that were defined in the fixture
    default_params = fixturedefs[fixture_name][-1].params
    # values that were parametrized in the test
    runtime_params = list(set(_get_parametrized_values_for_fixture(test_items, fixture_name)))
    return runtime_params or default_params


def _get_test_functions(session) -> list[Function]:
    """
    hack to get the expected items from the session, before the collection is done. this is done by calling internal pytest functions such resolve_collection_argument to get the expected items
    """
    from _pytest.main import resolve_collection_argument

    initialpaths = []
    if not hasattr(session, "_initial_parts"):
        session._initial_parts = []
    for arg in session.config.args:
        fspath, parts = resolve_collection_argument(
            session.config.invocation_params.dir,
            arg,
            as_pypath=session.config.option.pyargs,
        )
        session._initial_parts.append((fspath, parts))
        initialpaths.append(fspath)
    session._initialpaths = frozenset(initialpaths)
    expected_items = session.collect()
    functions = []
    for item in expected_items:
        if isinstance(item, Function):
            functions.append(item)
        else:
            # recursevly get all test functions
            functions.extend(_get_test_functions(item))

    return functions


def _get_direct_requested_fixtures(test_functions: Iterable[Callable]) -> set[str]:
    """
    get all requested fixtures from all test function in scope
    """
    requested_fixtures = set()
    for test_function in test_functions:
        for param in inspect.signature(test_function).parameters.keys():
            requested_fixtures.add(param)
    return requested_fixtures


def _get_dependent_fixtures(fixture_names: Iterable[str], fixturedefs):
    """
    recusevly get all fixtures that are dependent on the given fixture
    """
    if not fixture_names:
        return set()
    dependent_fixtures = set(fixture_names)

    for fixture in fixture_names:
        _fixture_def = fixturedefs.get(fixture)
        if not _fixture_def:
            continue
        fixture_def = _fixture_def[-1]
        fixture_args = fixture_def.argnames
        dependent_fixtures.update(_get_dependent_fixtures(fixture_args, fixturedefs))

    dependent_fixtures.discard("request")  # remove request fixture
    return dependent_fixtures


def pascal_to_kebab_case(s):
    # Convert PascalCase to kebab-case using regular expressions
    return re.sub(r"(?<!^)(?=[A-Z])", "-", s).lower()


def pascal_to_snake_case_simple(s):
    # Convert PascalCase to snake_case using regular expressions
    return re.sub(r"(?<!^)(?=[A-Z])", "_", s).lower()


def pascal_to_snake_case(s):
    """Version that properly handles acronyms by looking ahead
    to detect consecutive uppercase letters,
    for example, "XMLParser" -> "xml_parser"
    """
    return re.sub(
        r"(?<!^)(?<!_)(?=[A-Z][a-z])|(?<!^)(?<!_)(?=[A-Z][0-9])|(?<!^)(?=[A-Z])(?=[A-Z][a-z])", "_", s
    ).lower()


def snake_to_pascal_case(s):
    return "".join(word.capitalize() for word in s.split("_"))


def is_fixture(method):
    """Helper to check if a method is decorated as a pytest fixture"""
    return hasattr(method, "_pytestfixturefunction")


def get_fixture_args(method):
    """Extract pytest fixture parameters from a decorated method"""
    if not is_fixture(method):
        return {}

    fixture_info = getattr(method, "_pytestfixturefunction")
    return {
        "scope": fixture_info.scope,
        "params": fixture_info.params,
        "autouse": fixture_info.autouse,
        "ids": fixture_info.ids,
        "name": fixture_info.name,
    }


def define_fixture(fixture_name, func, scope="function", params=None, ids=None, autouse=False):
    fixture_def = FixtureDef(
        fixturemanager=pytest_internals["fixturemanager"],
        baseid="",
        argname=fixture_name,
        func=func,
        scope=scope,
        params=params,
        ids=ids,
    )
    pytest_internals["fixturemanager"]._arg2fixturedefs[fixture_name] = [fixture_def]
