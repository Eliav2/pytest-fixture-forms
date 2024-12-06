from typing import Type

import pytest

from pytest_fixture_forms import FixtureForms


@pytest.hookspec()
def pytest_fixtureforms_update_test_node_parameterization(
    session: pytest.Session,
    cls: Type[FixtureForms],
    form: str,
    parameterized_vals: dict,
    node_args: list[str],
    args_to_remove: list[str],
) -> None:
    """
    Called when a test node is being parameterized with the final parameterized values.
    Called for each generated test node.
    @param session: the pytest session object
    @param cls: the current fixture form class
    @param form: the current form name
    @param parameterized_vals: the final parameterized values for the test node
    @param node_args: the arguments that would be passed to the test node
    @param args_to_remove: the arguments that should be removed before calling the original test function
    """
