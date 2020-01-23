import nltk
import re
from nltk.tokenize import RegexpTokenizer
import spacy

# from core.utils.constant import CHINESE_OR_JAPANESE

#Try spacy
nlp = spacy.load('en_core_web_sm')
doc = ''


jp_zh_sent_tokenizer = RegexpTokenizer('[^！？?!。]*[！？!?。]')
reg = re.compile(r'^\s*[A-Za-z0-9①-㊿]+\.|^\s*[ㄱ-ㅎ\s가-힣]\.|^\s*[MDCLXVI]+\.|^\s*[ぁ-んァ-ン]\.')
punkt = nltk.data.load('tokenizers/punkt/english.pickle')
punkt._params.abbrev_types.update(['al', 'etc', 'approx', 'cf', 'p.a', 'no', 'mar', 'apr', 'may', 'jun', 'jul'])


def preprocess(full_text, lang):
    text = ''
    if lang == 'ja':
        # Remove text that is unique to the Japanese document
        # Regex pattern: remove spaces of > 1 length, remove bracketed headings, Re
        text = re.sub(
            r' {2,}|^\s*【\d+】|^【特許文献\d+】|^【書類名】明細書$|^【請求項\d+】$|^整理番号(.*)\d+$|整理番号([\s\S]*)\d+\/[A-Z]', '', full_text, flags=re.MULTILINE)
        # Remove lenticular brackets and ideographic spaces
        text = re.sub(r'\b\u3000\b', ' ', text)
        text = re.sub(r'[【】]|^\s*\n$|\u3000', '', text)
    elif lang == 'en':
        # Remove text that is unique to the English document
        text = re.sub(
            r' {2,} |This application is based upon(.*)herein by reference.|CROSS-REFERENCE(.*)APPLICATION|\[\d+\]|\s*\d+\.\s+', '',
            full_text, flags=re.MULTILINE | re.IGNORECASE)
        # Fix Fig. 1 being separatedz by removing the space
        text = re.sub(r'FIG.\s+', 'FIG.', text, flags=re.IGNORECASE)
        text = re.sub(r'FIGS.\s+', 'FIGS.', text, flags=re.IGNORECASE)
    text = replace_bracketed_punctuation(text)
    return text


# Replaces all punctuation inside brackets so it doesn't get incorrectly tokenized
def replace_bracketed_punctuation(text):

    # Search line for brackets
    match_list = []
    match_matrix = re.findall(r'\((.*?)\)|（(.*?)）|「(.*?)」', text)
    for i in match_matrix:
        for j in i:
            if j is not '':
                match_list.append(j)
    for match in match_list:
        if re.search(r'[。\!\?]', match):
            # Construct replacement string
            replacement = match.replace('。', '<gcon_ja_period>')
            replacement = replacement.replace('!', '<gcon_exclamation_mark>')
            replacement = replacement.replace('?', '<gcon_question_mark>')
            # Replace it in the actual list
            text = text.replace(match, replacement)
    return text





def tokenize(tokenize_fn, full_text):
    text_infos = []
    sents = []
    full_text = full_text.replace('\n', '')
    for sentence in tokenize_fn(full_text):
        if sentence.strip():  # Checks that it is not just whitespace/ doesn't actually do anything?
            sents.append(sentence)
            # Replace special characters with original text
            if '<gcon_' in sentence:
                sentence = sentence.replace('<gcon_ja_period>', '。')
                sentence = sentence.replace('<gcon_exclamation_mark>', '!')
                sentence = sentence.replace('<gcon_question_mark>', '?')
            text_infos.append({'text': sentence.strip()})


        # sents = [sent.strip() for sent in tokenize_fn(full_text) if sent.strip()]
        # if len(sents) > 1:
        #     for index, sent in enumerate(sents):
        #         if reg.match(sent) and index < len(sents) - 1:
        #             sents[index] = sents[index] + ' ' + sents[index + 1]
        #             del sents[index + 1]
        #         text_infos.append({'text': sents[index].strip()})
        # else:
        #     text_infos.append({'text': sent.strip()})
    return text_infos


def sentence_tokenize(full_text, source_lang):
    # if source_lang in CHINESE_OR_JAPANESE:
    full_text = preprocess(full_text, source_lang)
    if source_lang == 'ja' or source_lang == 'zh':
        return tokenize(jp_zh_sent_tokenizer.tokenize, full_text)
    else:
        return tokenize(nltk.sent_tokenize, full_text)


if __name__ == "__main__":
    # text = """
    #     a. 안녕하세요.
    #     1. 좋은 아침입니다.
    #     ㄱ. 초 록
    #     가. 바이.
    #     II. 그게 뭐예요?
    #     ぁ. 잘 부탁드립니다.
    #     ㊿. 과연 될 것인가?
    #     ⓐ. 수고하셨습니다.
    #     ⓰. 까만 동그라미도 되나요?
    #     ㉻. 이젠 에어컨이 잘 나오네요.
    #     (가). 괄호는 안되겠죠.
    # """

    # text = """
    # 1.マイケルユージーンアーチャー[1]（1974年2月11日生まれ）は、彼のステージ名D'Angelo（ディアンジェロと発音）でよく知られ、アメリカのシンガー、ソングライター、マルチ楽器奏者、レコードプロデューサーです。 ダンジェロは、エリカバドゥ、ローリンヒル、マックスウェル、コラボレーターのアンジーストーンなどのアーティストとともに、ネオソウルムーブメントに関連しています。
    # 2.ペンテコステ派の息子、バージニア州リッチモンドに生まれる
    # ダンジェロ牧師は子供の頃ピアノを学びました。18歳の彼は、ハーレムのアポロ劇場で3週間連続してアマチュアの才能コンテストに優勝しました。ヒップホップグループI.D.U.との短い提携の後、彼の最初の大きな成功は、1994年に「U Will Know」という歌の共同作家および共同プロデューサーとして生まれました。
    # """
    #
    # text = """
    #      电影《甜蜜蜜》由陈可辛导演，张曼玉、黎明和曾志伟主演，1996年公映? 1996年正值香港回归前夕，也是一代歌后邓丽君逝世翌年。电影借助这一特殊时代背景，讲述了20世纪末期香港新移民的艰辛岁月，并以邓丽君的歌曲《甜蜜蜜》贯穿始终，成功抓住两岸三地中国人的共通情感。影片剧情始于1986年，终于1995年邓丽君骤逝当天，在中国出现移民潮的大背景下，通过小人物的命运展现了香港回归前十年的历史变迁。
    #     """

    # text = """
    # “Hello again, Miss Dunbar. I’m afraid you’re not having a very pleasant holiday.” He motioned for her to sit.
    # “People do seem to be dying in my vicinity,” she said.
    # """
    text = '①. 슬로건 및 비전 : 가까이 두고 싶은 정보 친구가 되자 ex_아이언맨에 등장하는 비전,'
    print(sentence_tokenize(text, 'ko'))
