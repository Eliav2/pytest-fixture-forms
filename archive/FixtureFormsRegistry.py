from typing import Type, Dict, List, Callable
import pytest
from pytest import Session, Config, Item, Package, Module

from pytest_fixture_forms import FixtureForms


class FixtureFormsRegistry:
    """
    Registry that handles automatic discovery and registration of FixtureForms subclasses
    by leveraging pytest's test collection.
    """
    _instance = None
    _registered_classes: Dict[str, Type['FixtureForms']] = {}
    _pending_registrations: List[Callable] = []

    def __init__(self):
        if FixtureFormsRegistry._instance is not None:
            raise RuntimeError("Use FixtureFormsRegistry.get_instance()")
        self._discovery_completed = False

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register_class(self, cls: Type['FixtureForms']):
        """Register a FixtureForms subclass."""
        self._registered_classes[cls.__name__] = cls

    def add_pending_registration(self, callback: Callable):
        """Add a pending fixture registration callback."""
        self._pending_registrations.append(callback)

    def discover_subclasses_from_session(self, session: Session):
        """
        Discover FixtureForms subclasses by importing all test modules collected by pytest.
        """
        if self._discovery_completed:
            return

        def _import_from_collector(collector):
            """Recursively import modules from pytest collectors."""
            if isinstance(collector, Module):
                # Module is already imported by pytest
                return
            elif isinstance(collector, Package):
                # For packages, we need to import the module
                try:
                    __import__(collector.name)
                except ImportError:
                    return

            # Recurse into children
            if hasattr(collector, 'collect'):
                for item in collector.collect():
                    _import_from_collector(item)

        # Start with the session's collected items
        items = session.perform_collect()
        for item in items:
            if hasattr(item, 'parent'):
                _import_from_collector(item.parent)

        self._discovery_completed = True

    def execute_registrations(self, session: Session):
        """Execute all pending fixture registrations."""
        for callback in self._pending_registrations:
            callback(session)

    def get_registered_classes(self) -> Dict[str, Type['FixtureForms']]:
        """Get all registered FixtureForms subclasses."""
        return self._registered_classes.copy()


@pytest.hookimpl(tryfirst=True)
def pytest_collection(session):
    """Modified collection hook that ensures all fixtures are registered."""
    registry = FixtureFormsRegistry.get_instance()
    registry.execute_registrations(session)
    return None  # Let pytest continue with normal collection