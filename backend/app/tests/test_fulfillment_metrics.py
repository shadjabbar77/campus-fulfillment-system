from app.services.fulfillment_metrics import get_fulfillment_metrics


def test_fulfillment_metrics_returns_expected_structure():
    metrics = get_fulfillment_metrics(order_count=100, seed=42)

    assert metrics["orders_simulated"] == 100
    assert "naive_strategy" in metrics
    assert "optimized_strategy" in metrics
    assert "improvements" in metrics


def test_optimized_strategy_reduces_average_distance():
    metrics = get_fulfillment_metrics(order_count=100, seed=42)

    naive_distance = metrics["naive_strategy"]["average_distance_m"]
    optimized_distance = metrics["optimized_strategy"]["average_distance_m"]

    assert optimized_distance <= naive_distance


def test_metrics_include_sla_rates():
    metrics = get_fulfillment_metrics(order_count=100, seed=42)

    assert "sla_success_rate" in metrics["naive_strategy"]
    assert "sla_success_rate" in metrics["optimized_strategy"]
    assert "express_sla_success_rate" in metrics["naive_strategy"]
    assert "express_sla_success_rate" in metrics["optimized_strategy"]
