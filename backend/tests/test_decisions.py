import pytest
from datetime import datetime
from app.models.core_models import Decision, DecisionType, DecisionStatus

def test_decision_date_validation():
    print("\nStarting test_decision_date_validation with model_validate")
    
    # Test ISO format
    data1 = {
        "tenant_id": 1,
        "decision_type": DecisionType.RISK_ACCEPTANCE,
        "decision_text": "ISO test",
        "valid_until": "2026-11-19"
    }
    d1 = Decision.model_validate(data1)
    print(f"D1 valid_until: {d1.valid_until} (type: {type(d1.valid_until)})")
    assert isinstance(d1.valid_until, datetime)
    assert d1.valid_until.year == 2026

    # Test European slash format
    data2 = {
        "tenant_id": 1,
        "decision_type": DecisionType.RISK_ACCEPTANCE,
        "decision_text": "European slash test",
        "valid_until": "19/11/2026"
    }
    d2 = Decision.model_validate(data2)
    print(f"D2 valid_until: {d2.valid_until} (type: {type(d2.valid_until)})")
    assert isinstance(d2.valid_until, datetime)
    assert d2.valid_until.day == 19

    # Test European dash format
    data3 = {
        "tenant_id": 1,
        "decision_type": DecisionType.RISK_ACCEPTANCE,
        "decision_text": "European dash test",
        "valid_until": "19-11-2026"
    }
    d3 = Decision.model_validate(data3)
    print(f"D3 valid_until: {d3.valid_until} (type: {type(d3.valid_until)})")
    assert isinstance(d3.valid_until, datetime)
    assert d3.valid_until.day == 19
