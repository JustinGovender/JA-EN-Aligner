import pytest
from os import environ
from sentence_tokenizer import preprocess



def test_1():
    assert True


def test_2():
    test_text = ''
    full_text = environ.get('env_source_text')
    processed_text = preprocess(full_text, 'ja').split('\n')
    for line in processed_text:
        test_text = line
        if test_text != '':
            break
    print(test_text)
    assert test_text == '発明の名称取付装置および電子機器'