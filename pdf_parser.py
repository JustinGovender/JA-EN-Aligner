import fitz
from sentence_tokenizer import sentence_tokenize


class PdfParser:

    def get_text_from_pdf(self, file_obj, is_server):

        if is_server:
            doc = fitz.open("pdf", file_obj.read())
        else:
            doc = fitz.open(file_obj)

        page_count = doc.pageCount
        page = 0
        text = ''
        while (page < page_count):
            p = doc.loadPage(page)
            page += 1
            text = text + p.getText()

        return text

    def pdf_parse(self, file_obj, is_server, source_lang, make_full_text=None):
        full_text = ''
        parsed_string = ''
        try:
            parsed_string = self.get_text_from_pdf(file_obj, is_server)
        except Exception as e:
            print('exception {}'.format(e))

        if make_full_text:
            full_text = make_full_text(full_text, parsed_string)

        text_infos = sentence_tokenize(parsed_string, source_lang)
        return text_infos, full_text


if __name__ == "__main__":
    local_parser = PdfParser()
    print(local_parser.pdf_parse('test_data/movie.pdf', False, 'en'))
