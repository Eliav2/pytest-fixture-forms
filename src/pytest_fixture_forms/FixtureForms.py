import inspect
from typing import Any

import pytest

from pytest_fixture_forms.utils import (
    create_dynamic_function,
    pascal_to_snake_case,
    is_fixture,
    get_fixture_args,
    define_fixture,
)
from _pytest.main import Session


class FixtureForms:
    """
    This class is used to create fixtures inside a class.
    any method inside a class that inherits from this class will be considered a fixture, with the name of the method prefixed by the class name.
    so for example,
    >>>from pytest_fixture_forms import FixtureForms
    >>>class MyClass(FixtureForms):
    >>>     @pytest.fixture
    >>>     def arn(self):
    >>>         return 1
    defiines a fixtures named:
        "my_class" - returns instance of MyClass class
        "my_class_form" - returns the current form name, e.g, "arn"
    each fixture method in the class is considered a form, and the value of the form is the return value of the method. would generate the following fixtures:
        "my_class_<form>" - returns the value of the form, e.g, 1


    """

    # This is a class variable that holds the mapping between the fixture name and the subclass that defines it
    special_params_fixtures = {}

    @classmethod
    def forms(cls) -> list[str]:
        # Only get methods decorated with @pytest.fixture
        return [
            name
            for name, method in cls.__dict__.items()
            if callable(method) and not name.startswith("__") and is_fixture(method)
        ]

    @classmethod
    def get_instance_fixture_name(cls):
        return f"{pascal_to_snake_case(cls.__name__)}"

    @classmethod
    def get_initial_prototype_fixture_name(cls):
        """very initial prototype, with form only"""
        return f"{pascal_to_snake_case(cls.__name__)}_initial_prototype"

    @classmethod
    def get_prototype_fixture_name(cls):
        """the prototype instance is same as the instance, but without the value"""
        return f"{pascal_to_snake_case(cls.__name__)}_prototype"

    @classmethod
    def get_form_value_fixture_name(cls, method_name):
        """Get the name of the defined fixture for given method of the class"""
        return f"{pascal_to_snake_case(cls.__name__)}_{method_name}"

    @classmethod
    def get_form_fixture_name(cls):
        return f"{pascal_to_snake_case(cls.__name__)}_form"

    @classmethod
    def get_form_owners_fixture_name(cls):
        return f"{pascal_to_snake_case(cls.__name__)}_owner"

    @classmethod
    def get_form_owner_fixture_name(cls, form_name):
        return f"{pascal_to_snake_case(cls.__name__)}_{form_name}_owner"

    @classmethod
    def _schedule_fixture_registration(cls, callback):
        if not hasattr(FixtureForms, "_pending_fixture_registrations"):
            FixtureForms._pending_fixture_registrations = []
        FixtureForms._pending_fixture_registrations.append(callback)

    @classmethod
    def _register_pending_fixtures(cls, session):
        for subcls in FixtureForms.__subclasses__():
            cls.special_params_fixtures[subcls.get_instance_fixture_name()] = subcls
            if hasattr(subcls, "_pending_fixture_registrations"):
                for register in subcls._pending_fixture_registrations:
                    register(session, **{})

    @classmethod
    def __register_methods_as_fixtures(cls):
        """register all methods as fixtures, and also defines owner fixture for each form"""

        def register(session:Session, **kwargs):
            fixturemanager = session._fixturemanager
            fixturedefs = fixturemanager._arg2fixturedefs
            for form in cls.forms():
                method = getattr(cls, form)
                fixture_name = cls.get_form_value_fixture_name(form)
                if fixture_name not in fixturedefs:
                    # Unwrap staticmethod if needed (this messes up with tests defined at a class scope)
                    if isinstance(method, staticmethod):
                        func = method.__get__(None, cls)
                    else:
                        func = method
                    func.fixture_name = fixture_name
                    # Get fixture parameters if the method was decorated with @pytest.fixture
                    instance_fixture_name = cls.get_instance_fixture_name()
                    fixture_args = get_fixture_args(func)

                    # # if fixture given, unwrapped it because we are making the fixture def registration ourselves in pytest_collection hook
                    unwrapped_func = func if not is_fixture(func) else func.__wrapped__
                    # unwrapped_func_sig = inspect.signature(unwrapped_func)
                    form_owners_fixture_name = cls.get_form_owner_fixture_name(form)

                    def make_wrapper(method_name):
                        # prototype_fixture_name = cls.get_prototype_fixture_name()
                        initial_prototype_fixture_name = cls.get_initial_prototype_fixture_name()
                        # _form_owners_fixture_name = cls.get_form_owner_fixture_name(form)
                        _must_params = [
                            initial_prototype_fixture_name,
                            # cls.get_form_owners_fixture_name(),
                            # _form_owners_fixture_name,
                            # "request",
                            # "who",
                        ]

                        def impl(args: dict, required_params):
                            method = getattr(cls, method_name).__wrapped__
                            # who = required_params["who"]
                            initial_instance = required_params[initial_prototype_fixture_name]
                            initial_instance.form = method_name
                            # initial_instance.who = who
                            bound_method = method.__get__(None, cls)
                            # this is the actual call to the form method, we inject here the 'self' arg,
                            # and the rest of the args that user requested(which are provided by pytest fixture system)
                            return bound_method(initial_instance, *args.values())

                        # Create signature without self for pytest
                        sig = inspect.signature(unwrapped_func)
                        params = [p for n, p in sig.parameters.items() if n != "self"]

                        return create_dynamic_function(
                            [p.name for p in params],
                            impl,
                            # Filter out _must_params unless they're in the original function signature
                            required_params=_must_params,
                        )

                    final_value_func = make_wrapper(form)
                    # fixture for the method value
                    define_fixture(
                        fixturemanager,
                        fixture_name,
                        final_value_func,
                        fixture_args.get("scope", "function"),
                        params=fixture_args.get("params", None),
                    )

        cls._schedule_fixture_registration(register)

    @classmethod
    def __register_form_fixture(cls):
        """register special fixture for forms"""

        form_fixture_name = cls.get_form_fixture_name()

        def register_forms_fixture(session, **kwargs):
            fixturemanager = session._fixturemanager
            methods_names = [
                name for name, method in cls.__dict__.items() if callable(method) and not name.startswith("__")
            ]

            def forms_fixture(request):
                return request.param

            define_fixture(fixturemanager,form_fixture_name, forms_fixture, params=methods_names)

        cls._schedule_fixture_registration(register_forms_fixture)

    @classmethod
    def __register_instance_fixture(cls):
        """register special for returning the instance of the class"""

        def register_instance_fixture(session, **kwargs):
            fixturemanager = session._fixturemanager
            initial_prototype_fixture_name = cls.get_initial_prototype_fixture_name()

            # initial fixture to create the instance, does not depend on parameterized fixtures such forms fixture
            def impl_initial_proto(args: dict):
                request = args["request"]
                # form and value are later initialized
                return cls(request)

            initial_proto_fixture_func = create_dynamic_function(["request"], impl_initial_proto)
            define_fixture(fixturemanager,initial_prototype_fixture_name, initial_proto_fixture_func)

            prototype_fixture_name = cls.get_prototype_fixture_name()
            forms_fixture_name = cls.get_form_fixture_name()

            # intermediate fixture to create the instance, with parameterization on forms, while avoiding recursive dependency
            def impl_proto(args: dict):
                initial_proto = args[initial_prototype_fixture_name]
                form = args[forms_fixture_name]
                initial_proto.form = form
                # value is later initialized, owner should be set by the user
                return initial_proto

            proto_fixture_func = create_dynamic_function(
                [initial_prototype_fixture_name, forms_fixture_name], impl_proto
            )

            define_fixture(fixturemanager,prototype_fixture_name, proto_fixture_func)

            def impl(args: dict):
                request = args["request"]
                # form = args[forms_fixture_name]
                proto = args[prototype_fixture_name]
                form = proto.form
                proto_instance = args[prototype_fixture_name]
                # val = args[cls.get_form_fixture_name(form)]
                val = request.getfixturevalue(cls.get_form_value_fixture_name(form))
                proto_instance.value = val
                return proto_instance

            instance_fixture_name = cls.get_instance_fixture_name()
            # fixturedefs = session._fixturemanager._arg2fixturedefs
            # test_items = kwargs.get("test_items", [])
            # requested_forms = _get_final_parametrized_values_for_fixture(fixturedefs, test_items, forms_fixture_name)
            # requested_forms_fixtures = set()
            # for form in requested_forms:
            #     requested_forms_fixtures.add(cls.get_form_value_fixture_name(form))
            # values_param_name = cls.get_value_fixture_name()
            instance_fixture_func = create_dynamic_function(["request", prototype_fixture_name], impl)

            define_fixture(fixturemanager,instance_fixture_name, instance_fixture_func)

        cls._schedule_fixture_registration(register_instance_fixture)

    def __init_subclass__(cls, **kwargs):
        cls.__register_form_fixture()
        # cls.__register_forms_default_owner_fixture()
        cls.__register_methods_as_fixtures()
        cls.__register_instance_fixture()
        # cls.__register_value_fixture()
        super().__init_subclass__(**kwargs)

    def __repr__(self):
        return f"{self.__class__.__name__}.{self.form}={self.value}"

    def __init__(
        self,
        request: pytest.FixtureRequest,
        *,
        form: str = None,
    ):
        self.request: pytest.FixtureRequest = request
        self.form: str = form
        self.value: Any | None = None

    def getfixturevalue(self, name):
        return self.request.getfixturevalue(name)

    def request_form(self, form_name):
        return self.getfixturevalue(self.get_form_value_fixture_name(form_name))

    @classmethod
    def get_cases_fixture_name(cls):
        return f"{pascal_to_snake_case(cls.__name__)}_case"
