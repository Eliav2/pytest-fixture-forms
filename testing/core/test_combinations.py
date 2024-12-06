import pytest

from pytest_fixture_forms import FixtureForms


class Param1(FixtureForms):
    @pytest.fixture
    def form1(self):
        return "1"

    @pytest.fixture
    def form2(self):
        return "2"

    @pytest.fixture
    def form3(self):
        return "3"


class Param2(FixtureForms):
    @pytest.fixture
    def form1(self):
        return "1"

    @pytest.fixture
    def form2(self):
        return "2"

    @pytest.fixture
    def form3(self):
        return "3"


class Param3(FixtureForms):
    @pytest.fixture
    def form1(self):
        return "1"

    @pytest.fixture
    def form2(self):
        return "2"

    @pytest.fixture
    def form3(self):
        return "3"


def test_combinations(param1: Param1, param2: Param2, param3: Param3):
    assert param1.value in ["1", "2", "3"]
    assert param2.value in ["1", "2", "3"]
    assert param3.value in ["1", "2", "3"]
    print(param1, param2, param3)
