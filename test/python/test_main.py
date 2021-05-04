import main

def test_import():
    import os
    assert True

def test_lambda():
    main.lambda_handler()
    assert True