# pytest-fixture-forms

A powerful pytest plugin that simplifies testing different forms of parameters through dynamic fixture generation. This
plugin is particularly useful for API testing, integration testing, or any scenario where you need to verify behavior
across multiple parameter variations.

## Key Features

- Automatically generates fixtures based on class methods
- Supports dynamic test generation for parameter combinations
- Integrates seamlessly with pytest's parametrization
- Handles nested fixture dependencies elegantly
- Reduces boilerplate in test code

## Installation

Install from PyPI:

```bash
pip install pytest-fixture-forms
```

## Quick Start

Here's a simple example showing how to use pytest-fixture-forms:

```python
from pytest_fixture_forms import FixtureForms
import pytest


class UserCredentials(FixtureForms):
    @pytest.fixture
    def valid_user(self):
        return {"username": "john_doe", "password": "secure123"}

    @pytest.fixture
    def invalid_password(self):
        return {"username": "john_doe", "password": "wrong"}

    @pytest.fixture
    def missing_username(self):
        return {"username": "", "password": "secure123"}


def test_login(user_credentials):
    # This test will run for each form defined in UserCredentials
    response = login_service.authenticate(**user_credentials.value)

    if user_credentials.form == "valid_user":
        assert response.status_code == 200
    else:
        assert response.status_code == 401
```

## Understanding FixtureForms

When you create a class that inherits from `FixtureForms`, the plugin automatically generates several fixtures:

1. `<class_name_snake_case>` - Returns an instance containing the current form and value
2. `<class_name_snake_case>_form` - The name of the current form being tested
3. `<class_name_snake_case>_<form_name>` - The value for a specific form

For example, given a class named `ApiEndpoint`:

```python
class ApiEndpoint(FixtureForms):
    @pytest.fixture
    def get_users(self):
        return "/api/v1/users"

    @pytest.fixture
    def create_user(self):
        return "/api/v1/users/create"


def test_endpoint(api_endpoint):
    # api_endpoint.form will be either "get_users" or "create_user"
    # api_endpoint.value will be the corresponding URL
    response = client.request("GET", api_endpoint.value)
```

## Advanced Usage

### Combining Multiple Forms

You can use multiple `FixtureForms` classes in a single test to test combinations:

```python
class RequestMethod(FixtureForms):
    @pytest.fixture
    def get(self):
        return "GET"

    @pytest.fixture
    def post(self):
        return "POST"


class ApiPath(FixtureForms):
    @pytest.fixture
    def users(self):
        return "/users"

    @pytest.fixture
    def products(self):
        return "/products"


def test_api_combinations(request_method, api_path):
    # This will generate tests for all combinations:
    # GET /users
    # GET /products
    # POST /users
    # POST /products
    response = client.request(request_method.value, api_path.value)
```

### Using with Parametrization

You can control which forms to test using pytest's parametrize:

```python
@pytest.mark.parametrize("request_method_form", ["get"])  # Only test GET requests
@pytest.mark.parametrize("api_path_form", ["users", "products"])
def test_specific_combinations(request_method, api_path):
    response = client.request(request_method.value, api_path.value)
```

### Accessing Fixture Values

Each `FixtureForms` instance provides:

- `form` - The current form name
- `value` - The value returned by the current form's fixture
- `request` - The pytest fixture request object

### Working with Dependencies

Forms can depend on other fixtures:

```python
class AuthenticatedEndpoint(FixtureForms):
    @pytest.fixture
    def user_profile(self, auth_token):  # Depends on auth_token fixture
        return f"/api/v1/profile", {"Authorization": auth_token}


@pytest.fixture
def auth_token():
    return "Bearer xyz123"
```

## How It Works

The plugin uses pytest's collection hooks to:

1. Dynamically register fixtures based on `FixtureForms` class methods
2. Generate test nodes for each combination of parameters
3. Handle fixture dependencies and parametrization

## Best Practices

1. Keep form methods focused on a single variation
2. Use clear, descriptive names for forms
3. Group related forms in a single class
4. Consider using parametrization to control test combinations
5. Document expected behavior for each form

## Common Patterns

### API Testing

```python
class Endpoint(FixtureForms):
    @pytest.fixture
    def valid_path(self):
        return "/api/v1/resource"

    @pytest.fixture
    def invalid_path(self):
        return "/api/v1/nonexistent"


class Payload(FixtureForms):
    @pytest.fixture
    def valid_data(self):
        return {"key": "value"}

    @pytest.fixture
    def invalid_data(self):
        return {"invalid": "data"}


def test_api(endpoint, payload):
    response = client.post(endpoint.value, json=payload.value)
```

## Contributing

Contributions are welcome! This is a new project and there might be bugs or missing features. If you have any
suggestions, bug reports, or feature requests, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.