import pytest

from ..models.requests import TargetModel
from ..services.cost_estimator import CostEstimator


@pytest.fixture
def estimator():
    return CostEstimator()


def test_gpt4o_cost(estimator):
    result = estimator.estimate(1000, 600, TargetModel.GPT_4O)
    assert result.total_cost > 0
    assert result.input_cost > 0
    assert result.estimated_output_cost > 0
    assert result.model == "gpt-4o"


def test_savings_percent(estimator):
    pct = estimator.savings_percent(0.032, 0.011)
    assert 65 < pct < 70


def test_savings_percent_zero_original(estimator):
    assert estimator.savings_percent(0, 0.01) == 0.0


def test_all_models_have_pricing(estimator):
    for model in TargetModel:
        result = estimator.estimate(500, 200, model)
        assert result.total_cost >= 0


def test_cost_scales_linearly(estimator):
    small = estimator.estimate(100, 60, TargetModel.GPT_4O)
    large = estimator.estimate(1000, 600, TargetModel.GPT_4O)
    assert abs(large.total_cost / small.total_cost - 10.0) < 0.01
