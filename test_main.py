import pytest
from os import environ
from sentence_tokenizer import preprocess



def test_1():
    assert True


def test_preprocessing_removes_header():
    test_text = ''
    full_text = environ.get('env_source_text')
    for line in preprocess(full_text, 'ja').split('\n'):
        test_text = line
        if test_text != '':
            break
    assert test_text == '発明の名称取付装置および電子機器'


