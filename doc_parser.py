# -*- coding:utf-8 -*-

import argparse
import re
import xml.etree.ElementTree as ET
import zipfile
import os
import sys
from sentence_tokenizer import sentence_tokenize
from sentence_tokenizer import jp_zh_sent_tokenizer



nsmap = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}


def process_args():
    parser = argparse.ArgumentParser(description='A pure python-based utility '
                                                 'to extract text and images '
                                                 'from docx files.')
    parser.add_argument("-docx", default=os.path.join('.', 'KE18-00133.docx'), help="path of the docx file")
    parser.add_argument('-i', '--img_dir', help='path of directory '
                                                'to extract images')

    args = parser.parse_args()

    if not os.path.exists(args.docx):
        print('File {} does not exist.'.format(args.docx))
        sys.exit(1)

    if args.img_dir is not None:
        if not os.path.exists(args.img_dir):
            try:
                os.makedirs(args.img_dir)
            except OSError:
                print("Unable to create img_dir {}".format(args.img_dir))
                sys.exit(1)
    return args


def qn(tag):
    """
    Stands for 'qualified name', a utility function to turn a namespace
    prefixed tag name into a Clark-notation qualified tag name for lxml. For
    example, ``qn('p:cSld')`` returns ``'{http://schemas.../main}cSld'``.
    Source: https://github.com/python-openxml/python-docx/
    """
    prefix, tagroot = tag.split(':')
    uri = nsmap[prefix]
    return '{{{}}}{}'.format(uri, tagroot)


def xml2text(xml):  # word를 읽었을 때 xml을 txt로. tree형태에서 필요한 정보만 fetch
    """
    A string representing the textual content of this run, with content
    child elements like ``<w:tab/>`` translated to their Python
    equivalent.
    Adapted from: https://github.com/python-openxml/python-docx/
    """
    text = u''
    root = ET.fromstring(xml)
    text_list = []
    font_size = 12
    started = False
    for child in root.iter():
        if child.tag == qn('w:t'):
            started = True
            t_text = child.text
            text += t_text if t_text is not None else ''
        elif child.tag == qn('w:tab'):
            text += '\t'
        elif child.tag in (qn('w:br'), qn('w:cr')):
            text += '\n'
        elif child.tag == qn("w:p"):
            if started:
                text_list.append({'font_size': font_size, 'text': text.strip()})
            text = ''
        elif child.tag == qn("w:sz"):
            if len(child.attrib) > 0:
                font_size = child.attrib.popitem()[1]
                # print('font_size ', font_size)

    if text != '':
        text_list.append({'font_size': font_size, 'text': text})
    return text_list


def process(docx, img_dir=None):
    text = []

    # unzip the docx in memory
    zipf = zipfile.ZipFile(docx)
    filelist = zipf.namelist()

    # get header text
    # there can be 3 header files in the zip

    # Don't actually want headers
    # header_xmls = 'word/header[0-9]*.xml'  # header/footer 필요 x
    # for fname in filelist:
    #     if re.match(header_xmls, fname):
    #         text.extend(xml2text(zipf.read(fname)))

    # get main text
    doc_xml = 'word/document.xml'
    text.extend(xml2text(zipf.read(doc_xml)))

    # get footer text
    # there can be 3 footer files in the zip
    # footer_xmls = 'word/footer[0-9]*.xml'
    # for fname in filelist:
    #     if re.match(footer_xmls, fname):
    #         text.extend(xml2text(zipf.read(fname)))

    if img_dir is not None:
        # extract images
        for fname in filelist:
            _, extension = os.path.splitext(fname)
            if extension in [".jpg", ".jpeg", ".png", ".bmp"]:
                dst_fname = os.path.join(img_dir, os.path.basename(fname))
                with open(dst_fname, "wb") as dst_f:
                    dst_f.write(zipf.read(fname))

    zipf.close()
    return text


if __name__ == '__main__':
    args = process_args()
    text = process(args.docx, args.img_dir)
    sys.stdout.write(text.encode('utf-8'))
