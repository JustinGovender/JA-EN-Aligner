# from core.utils.scondmport sentence_tokenize
from sentence_tokenizer import sentence_tokenize
import pandas as pd
import argparse
import os
import sys
from doc_parser import process
import pdf_parser
from google_api import google_translate
from Bleualign.align import Aligner
from pdf_parser import PdfParser
import re
from refine import Refiner

GOOGLE_SPLIT_SIZE = 100


def make_full_text(dict_list):
    text = ''
    result = ''
    for i, element in enumerate(dict_list):
        text = text + ' ' + (element['text'])
    return text


def make_sentences(text, lang):
    source_text = []
    full_text = ' '.join([value['text'] for value in text if value['text']])
    for sent in sentence_tokenize(full_text, lang):
        source_text.append(sent)
    return source_text


def dict_to_list(dict, key):
    return [value[key] for value in dict if value[key]]


def write_cells(sources, targets, source_lang, target_lang):
    df = pd.DataFrame(columns=[source_lang, target_lang])

    for i, (src, tgt) in enumerate(zip(sources, targets)):
        if src != '' or tgt != '':
            df.loc[i + 1, source_lang] = src
            df.loc[i + 1, target_lang] = tgt

    df.to_excel('sentence_pairs_result.xlsx', engine='xlsxwriter')


def make_google_reference_list(source_list, source_lang, target_lang):
    reference_list = []
    src_text_size = len(source_list)
    src_text_slice_count = src_text_size // GOOGLE_SPLIT_SIZE + 1
    for i in range(src_text_slice_count):
        start_pos = i * GOOGLE_SPLIT_SIZE
        end_pos = start_pos + GOOGLE_SPLIT_SIZE
        if end_pos > src_text_size:
            sub_list = source_list[start_pos:]
        else:
            sub_list = source_list[start_pos:end_pos]

        df = pd.DataFrame(sub_list)
        df = df.drop_duplicates()
        translated = google_translate('\n'.join(df[0].tolist()), source_lang, target_lang)
        translated_list = [translated[sentence] for sentence in sub_list]
        reference_list.extend(translated_list)

    return reference_list

def fix_ja_english_words(ja_list, en_list):
    replacement_dict = {}
    matches = []
    # Find all the source sentences with english characters
    for i, sent in enumerate(ja_list):
        if re.search(r'[a-zA-Z][a-zA-Z\s_-]+', sent) is not None:
            # Get each English word
            matches = re.findall(r'[a-zA-Z][a-zA-Z\s_-]+', sent)
            # For each word
            for word in matches:
                # Check if we already know the replacement word
                replacement_word = replacement_dict.get(word)
                if replacement_word is not None:
                    ja_list[i] = re.sub(word, replacement_word, ja_list[i])
                else:
                    # Remove all whitespace
                    broken_word = re.sub(r'\s+', '', word)
                    # Construct a string that will match independent of whitespace
                    match_string = ''
                    for j, char in enumerate(broken_word):
                        if j:
                            match_string += '\s*' + char
                        else:
                            match_string += '\b' + char
                    # Try to find matching word in the English sentence
                    result = re.search(match_string, en_list[i], flags=re.IGNORECASE)
                    replacement_word = result.group(0) if result else None
                    if replacement_word is not None:
                        # Add to dictionary
                        replacement_dict[word] = replacement_word
                        #Replace word in original list
                        ja_list[i] = re.sub(word, replacement_word, ja_list[i])






def align_sentences(source_list, target_list, reference_list):
    aligner = Aligner(None)
    aligner.multialign = aligner.get_align(source_list, target_list, reference_list, [])
    return aligner.get_mainloop(source_list, target_list, reference_list, [])


def generate_pairs(source_lang, target_lang, source_file, target_file, srctotarget_file, is_reference_save):
    # process file format into dictionary
    if os.path.splitext(source_file)[1].lower() == '.pdf':
        parser = PdfParser()
        source_dict_list, _ = parser.pdf_parse(source_file, False, source_lang)
    else:
        # Default is docx
        source_dict_list = process(source_file)
        source_dict_list = make_sentences(source_dict_list, source_lang)
    source_list = dict_to_list(source_dict_list, 'text')
    if os.path.splitext(target_file)[1].lower() == '.pdf':
        parser = PdfParser()
        target_dict_list, _ = parser.pdf_parse(target_file, False, target_lang, True)
    else:
        # Default is docx
        target_dict_list = process(target_file)
        target_dict_list = make_sentences(target_dict_list, target_lang)
    target_list = dict_to_list(target_dict_list, 'text')

    #Make sure all characters are half-width
    refiner = Refiner(os.path.join('.', 'regex.txt'))
    source_list = refiner.convert_text(source_list)
    target_list = refiner.convert_text(target_list)
    test_text = ' '.join(target_list) # <--------------------------------------------------------------- Debug !Remove!

    if srctotarget_file:
        with open(srctotarget_file, 'r') as srctotarget:
            reference_list = srctotarget.readlines()
            refs = [reference_list]
    else:
        reference_list = make_google_reference_list(source_list, source_lang, target_lang)
        reference_list = [string + '\n' for string in reference_list]
        refs = [reference_list]

        if is_reference_save:
            with open('mt_text.txt', 'w+') as reference_file:
                for sentence in reference_list:
                    reference_file.write(sentence)
    sources, targets = align_sentences(source_list, target_list, refs)
    if source_lang is 'ja':
        fix_ja_english_words(sources, targets)
    test_text = ' '.join(targets) # <--------------------------------------------------------------- Debug !Remove!
    return sources, targets


def parse_args(argv):
    """Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    # set the argument formats
    parser.add_argument(
        '--source_lang', '-src_lang', default='ja',
        help='source language')
    parser.add_argument(
        '--target_lang', '-tgt_lang', default='en',
        help='target language')
    parser.add_argument(
        '--source_file', '-src_file', default=os.path.join('.', '김태동 고문님 번역 파일들', '2015', 'KE15-02730.pdf'),
        help='source file')
    parser.add_argument(
        '--target_file', '-tgt_file', default=os.path.join('.', '김태동 고문님 번역 파일들', '2015', 'ke15-02730-EN.docx'),
        help='target file')
    parser.add_argument(
        '--source_to_target_file', '-srctotgt_file', default=os.path.join('test_data', 'misc_test', 'ref.txt'),
        help='source to target file')
    parser.add_argument(
        '--is_reference_save', '-ref', default=True,
        help='whether you want to save the reference file or not')

    return parser.parse_args(argv[1:])


if __name__ == '__main__':
    args = parse_args(sys.argv)
    sources, targets = generate_pairs(args.source_lang, args.target_lang, args.source_file, args.target_file, None, args.is_reference_save)
    write_cells(sources, targets, args.source_lang, args.target_lang)
