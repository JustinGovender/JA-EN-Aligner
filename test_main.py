import pytest
from os import environ
from sentence_tokenizer import preprocess



def test_1():
    assert True


def test_preprocessing_removes_header():
    test_text = ''
    full_text = environ.get('env_source_text')
    full_text = preprocess(full_text, 'ja').split('\n')
    for i in range(len(full_text)):
        if full_text[i] != '':
            test_text = full_text[i]
            break
    assert test_text == '発明の名称取付装置および電子機器'


