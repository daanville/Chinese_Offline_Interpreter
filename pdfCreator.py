from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
import re
import argparse
import pinyin as pinyin_library


class PdfCreator:
    """
    A PDF Creator which transforms a Chinese text into a formatted PDF file with Chinese text and corresponding Pinyin
    """

    def __init__(self, input_file=None, input_text="", headline="", output_file='OutputFile',
                 new_line_for_sentence=False, large_text=False):
        """
        The PDF Creator initializes with either an input file or an input text, as well as several optional parameters.
        __init__ sets up the pdf canvas and page measurements.

        Parameters:
            input_file: str
                Path to an .txt file containing Chinese text that will be used to create the pdf
            input_text: str
                If no file is given, this input text in Chinese characters will be used to create the pdf
            input_file: str
                The name of the pdf file, and the document's headline. No file suffix needed. Default: 'Output_PDF'
            new_line_for_sentence: Bool (optional)
                Whether a new line should be automatically added whenever a new sentence starts. Default: False
            large_text: Bool (optional)
                Whether the text should be extra large for increased visibility
        """
        print("\n...PDF Creator launched...\n")
        self.input_text = input_text
        if input_file:
            try:
                with open(input_file, "r", encoding="utf8") as in_file:
                    self.input_text = in_file.read()
                    print("Text file found. Text loaded.\n")
            except (FileNotFoundError, IsADirectoryError, PermissionError):
                print("The file you indicated does not seem to exist, or is not a valid text file.\n")
        elif len(input_text) > 0:
            print("Input text loaded.\n")
        else:
            print("No valid input text available!\n")
        self.headline = headline
        self.output_file = output_file
        self.new_line_for_sentence = new_line_for_sentence
        self.ignore_for_pinyin = "：。，！；’【0123456789’、】【/@#……&*（）()——-=+“”？:;"

        # Initialize text measurements
        self.chars_per_line = 24
        self.char_width = 0.85 * cm
        self.line_height = 1.5 * cm
        self.hanzi_size = 22
        self.pinyin_size = 9
        self.pinyin_offset = .5 * cm
        if large_text:
            self.init_large_text()

        # Initialize page measurements
        self.page_height = 29.7 * cm
        self.page_width = 21 * cm
        self.border_side = .5 * cm
        self.border_top = 2 * cm
        self.border_bottom = 1.7 * cm
        self.x_on_page = self.border_side
        self.y_on_page = self.border_top
        self.canvas = Canvas(self.output_file, pagesize=(self.page_width, self.page_height))
        self.canvas.setTitle(self.headline)

        # Initialize fonts
        pdfmetrics.registerFont(TTFont('Noto', 'res/NotoSansSC-Medium.ttf'))
        pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
        self.font_color_hanzi = (.2, .2, .5)
        self.font_color_pinyin = (.6, .6, .6)

    def init_large_text(self):
        """ Initializes measurements for large text """
        self.chars_per_line = 12
        self.char_width = 1.8 * cm
        self.line_height = 2.8 * cm
        self.hanzi_size = 34
        self.pinyin_size = 20
        self.pinyin_offset = .8 * cm

    def next_line(self):
        """ Advances to a new line on the pdf canvas"""
        self.y_on_page += self.line_height
        self.x_on_page = self.border_side

    def next_page(self):
        """ Adds a new page to the pdf document """
        self.canvas.showPage()
        self.y_on_page = self.border_top
        self.x_on_page = self.border_side

    def write_onto_canvas(self, text, is_hanzi, is_filename=False):
        """
        Writes text onto the correct place on the pdf canvas.

        Parameters
        ----------
        text : str
            the text to be written onto the PDF
        is_hanzi: bool
            a flag to decide if the written text is in Chinese (Hanzi) or Pinyin
        is_filename : bool, optional
            a flag to decide if the text written is a filename (default is False)
        """
        x_pos = self.page_width / 2 if is_filename else self.x_on_page + self.char_width * 0.5
        y_pos = self.page_height - self.y_on_page
        if is_hanzi:
            self.canvas.setFillColorRGB(*self.font_color_hanzi)
            self.canvas.setFont('STSong-Light', self.hanzi_size)
            self.canvas.drawCentredString(x_pos, y_pos, text)
        else:
            self.canvas.setFillColorRGB(*self.font_color_pinyin)
            self.canvas.setFont("Noto", self.pinyin_size)
            self.canvas.drawCentredString(x_pos, y_pos - self.pinyin_offset, text)

    def place_headline_on_canvas(self):
        """ Puts the headline at the top of page 1 of the pdf canvas"""
        self.write_onto_canvas(self.headline, True, is_filename=True)
        self.next_line()

    def place_sentence_on_canvas(self, sentence):
        """
        Takes in a single Chinese sentence, adds the pinyin, and places both onto the pdf canvas
        Parameters
        ----------
        sentence: str
            The sentence to be placed onto the pdf canvas
        """
        if len(sentence) > 0:
            print("Working on Sentence:", sentence)
            pos_in_sentence = 0
            pos_in_line = 0

            # extract hanzi and pinyin from sentence; ignore except numbers, punctuation etc.
            sentence_hanzis = []
            sentence_pinyins = []
            for hanzi in sentence:
                if len(hanzi) > 0 and hanzi not in "  ":
                    pinyin = " " if hanzi in self.ignore_for_pinyin else pinyin_library.get(hanzi)
                    sentence_hanzis.append(hanzi)
                    sentence_pinyins.append(pinyin)

            # write hanzi and pinyin onto the pdf canvas
            while pos_in_sentence < len(sentence_hanzis):

                # Check for new line / new page
                if pos_in_line >= self.chars_per_line - 1:
                    self.next_line()
                    pos_in_line = 0
                    if self.y_on_page > self.page_height - self.border_bottom:
                        self.next_page()

                # Write onto canvas
                self.write_onto_canvas(sentence_hanzis[pos_in_sentence], True)
                self.write_onto_canvas(sentence_pinyins[pos_in_sentence], False)

                # Advance positions
                pos_in_sentence += 1
                pos_in_line += 1
                self.x_on_page += self.char_width

            # Finalize writing sentence
            self.next_line()
            if self.y_on_page > 27 * cm:
                self.next_page()

    def create_pdf(self):
        """
        Creates a pdf with Chinese characters and corresponding Pinyin
        """
        if len(self.input_text) > 0:
            self.place_headline_on_canvas()

            # Split the text into portions
            split_triggers = '。|\n' if self.new_line_for_sentence else '\n'
            sentences = re.split(split_triggers, self.input_text)

            # Write text to Canvas
            for sentence in sentences:
                self.place_sentence_on_canvas(sentence)

            # Save pdf file
            self.canvas.save()
            print(f"\nSuccess! Text has been written to '{self.output_file}'.\n")
        else:
            print(
                "Failure to create PDF file: No input text to create a pdf file from. You need to specify either a "
                "text file, or pass a text directly through the command line. Please see --help for help.\n")


def create_pdf_from_commandline():
    parser = argparse.ArgumentParser(description='Create a PDF from a given Chinese text.')
    parser.add_argument('--input_file', type=str, default=None,
                        help='Path to a text file containing the Chinese Input text to convert to PDF')
    parser.add_argument('--input_text', type=str, default='', help='Chinese Input text to convert to PDF')
    parser.add_argument('--headline', type=str, default='', help='Headline for the PDF')
    parser.add_argument('--output_file', type=str, default='OutputFile', help='Filename for the output PDF')
    parser.add_argument('--new_line_for_sentence', type=bool, default=False,
                        help='True if you want a new line for each sentence')
    parser.add_argument('--large_text', type=bool, default=False, help='True if you want extra large text')

    args = parser.parse_args()

    pdf_maker = PdfCreator(args.input_file, args.input_text, args.headline, args.output_file + ".pdf",
                           args.new_line_for_sentence, args.large_text)
    pdf_maker.create_pdf()


if __name__ == '__main__':
    create_pdf_from_commandline()