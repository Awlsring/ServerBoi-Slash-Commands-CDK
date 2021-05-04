from serverboi_interactions_lambda import main as interactions

def test_import():
    import os
    assert True

def test_lambda():
    interactions.lambda_handler()
    assert True