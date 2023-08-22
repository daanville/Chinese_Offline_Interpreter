# Chinese-Offline-Interpreter-and-Pdf-Exporter

Chinese Offline Interpreter and Pdf Exporter is a live Chinese to English interpreter, utilizing the Chinese-English dictionary(cedict library) to provide real-time translations. The interpreter will update with every keystroke in the input field. The entire project is completely offline and uses no online services. Please note that it does not translate whole sentences, instead it only give character by character translations. The project's GUI is built using the tkinter library in python. The pdf Creator can also be used standalone (via commandline).
This application is intended to be used either in Chinese lessons, or as a tool for Chinese learners to quickly grasp pronounciation / meaning of a Chinese text.

## Features

- Real-time interpretation from Chinese to English.
- Archiving the translations.
- Capability to save the entire translation session to either a .txt file or .pdf.

### Prerequisites

This program is written in Python 3.10. See the requirements.txt for needed packages.

Use pip to install the required packages:

```sh
pip install tkinter
pip install pinyin
pip install reportlab
pip install argparse
```

### How to Use the Interpreter

1. Clone or download this repository.
2. Open the interpreter.py file in your Python IDE (like PyCharm) or run it from your terminal.
3. This will open up a GUI. You can start typing Chinese text into the green input field at the top. As you type, you will see the pinyin and character by character English translation below, updating with every keystroke.
4. Pressing the Enter key will push the content of the input field to the archive frame below, this shows both the Chinese text and its pinyin.
5. The "Save to File" button at the bottom allows you to save your whole session either to a .txt file or to a .pdf file.

### How to Use the pdfCreator standalone via commandline

The `pdfCreator.py` script is a command-line utility that transforms Chinese text into a PDF with a simplified Chinese text and its corresponding Pinyin. The Chinese text can be provided either as a file, or directly in the commandline.

## Parameters
| Parameter | Default Value | Description |
| --- |---| --- |
| --input_file | None | Path to a `.txt` file containing Chinese text. If the text file is not provided, the `input_text` argument should be used |
| --input_text | '' | Chinese text to be added to the PDF. This can be ignored if `input_file` is provided |
| --headline | '' | Headline for the generated PDF |
| --output_file | 'OutputFile' | Filename of the output PDF (the .pdf extension will be added automatically)|
| --new_line_for_sentence | False | if `True`, a new line will be automatically added after every Chinese full stop (。)|
| --large_text | False | if `True`, the text in the PDF will be extra large for increased visibility (12 instead of 24 characters per line)|

## Steps

1. Open a terminal window.

2. Navigate to the directory containing the `pdfCreator.py` script.

3. Use the following command to run the script:
```
python pdfCreator.py --input_file "my_chinese_text.txt" --headline "My Chinese Text" --output_file "my_chinese_pdf"
```

This command will create a PDF titled "my_chinese_pdf.pdf", with the heading "My Chinese Text", using the text found in the "my_chinese_text.txt" file.

You can also specify the `input_text` directly if there is no input file:
```
python pdfCreator.py --input_text "你好，世界！" --headline "Hello World" --output_file "hello_world"
```

This command will create a PDF titled "hello_world.pdf", with the heading "Hello World" and a single sentence "你好，世界！" (Hello, World!).
Please note that most terminals will not display Chinese characters correctly. This does not affect the resulting file though.

The optional parameters `large_text` and `new_line_for_sentence` will modify the appearance of the text in the PDF. For example:
```
python pdfCreator.py --input_file "my_document.txt" --headline "My Document" --output_file "my_pdf" --large_text True --new_line_for_sentence True
```
This will result in new lines for each sentence and a larger font size.


## License

This project is licensed under the MIT License. See the `LICENSE.md` file for details.

## Contact

Daan Henderson - daan@daanville.com
