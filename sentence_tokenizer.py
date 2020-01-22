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
        # Regex pattern: remove spaces of > 1 length, remove bracketed headings
        text = re.sub(
            r' {2,}|^\s*【\d+】|^【特許文献\d+】|^【書類名】明細書$|^【請求項\d+】$', '', full_text, flags=re.MULTILINE)
        words_to_delete = ['整理番号', '(Proof)', '提出日']
        lines = text.split('\n')
        lines = [line for line in lines if not any(word in line for word in words_to_delete)]
        text = '\n'.join(lines)
        # Remove lenticular brackets and ideographic spaces
        text = re.sub(r'[【】]|^\s*\n$|\u3000', '', text)
    elif lang == 'en':
        # Remove text that is unique to the English document
        text = re.sub(
            r' {2,} |This application is based upon(.*)herein by reference.|CROSS-REFERENCE(.*)APPLICATION|\[\d+\]|\s*\d+\.\s+', '',
            full_text, flags=re.MULTILINE | re.IGNORECASE)
        # Fix Fig. 1 being separatedz by removing the space
        text = re.sub(r'FIG.\s+', 'FIG.', text, flags=re.IGNORECASE)
        text = re.sub(r'FIGS.\s+', 'FIGS.', text, flags=re.IGNORECASE)
    return text


def tokenize(tokenize_fn, full_text):
    text_infos = []
    sents = []
    extra_tokenizer = RegexpTokenizer('[^【】]*')
    full_text = full_text.replace('\n', '')
    for subsentence in tokenize_fn(full_text):
        #for subsentence in extra_tokenizer.tokenize(sentence): #Regex second pass
        if subsentence.strip():  # Checks that it is not just whitespace/ doesn't actually do anything
            sents.append(subsentence)
            text_infos.append({'text': subsentence.strip()})


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
