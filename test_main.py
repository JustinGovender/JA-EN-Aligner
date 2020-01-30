import pytest
from os import environ
from sentence_tokenizer import preprocess



def test_1():
    assert True


def test_preprocessing_removes_header():
    test_text = '''整理番号:46G094257A 特願2014-266299
    (Proof)
    提出日:平成26年12月26日
    1
    【書類名】明細書
    【発明の名称】取付装置および電子機器
    【技術分野】
    【０００１】
    本発明の実施形態は、取付装置および電子機器に関する。
    【背景技術】
    【０００２】
    従来、ユーザの体表に取り付けた状態で動作させる電子機器が知られている。'''.split('\n')
    full_text = preprocess(test_text, 'ja').split('\n')
    for i in range(len(full_text)):
        if full_text[i] != '':
            test_text = full_text[i]
            break
    assert test_text == '発明の名称取付装置および電子機器'


