import pytest
from os import environ


def test_1():
    assert True


def test_2():
    value = environ.get('test_var')
    assert value == 'Hello World!'