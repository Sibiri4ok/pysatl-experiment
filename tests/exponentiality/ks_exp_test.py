import pytest as pytest

from stattest.test.exponent import KSTestExp
from tests.exponentiality.abstract_exponentiality_test_case import AbstractExponentialityTestCase


@pytest.mark.parametrize(  # TODO: actual test (7; 10)
    ("data", "result"),
    [
        ([1, 2, 3, 4, 5, 6, 7], 0.17377394345044517),
        ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 0.16232061118184815),
    ],
)
class TestCaseKSExponentialityTest(AbstractExponentialityTestCase):

    @pytest.fixture
    def statistic_test(self):
        return KSTestExp()
