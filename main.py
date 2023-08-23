from tkinter import Frame, Text, Message, Label, Entry, Button, Tk, StringVar, filedialog, END
from tkinter.font import Font
import pinyin
from pdfCreator import *
from dict import Dict
import os


def hex_to_rgb(hex_color):
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb_color):
    return ''.join(['{:02x}'.format(x) for x in rgb_color])


class Interpreter:
    """
    This application serves as a live interpreter for Chinese text. As the user writes Chinese text into the input
    field, the pinyin and a simple character-per-character translation (using the cedict library) appears,
    updating with every keystroke. By pressing the enter key, the content of the input field gets pushed to an
    archive frame below, showing the Chinese text and its pinyin. Also features a save function which saves to either
    a .txt file or to .pdf. This application uses no online services whatsoever.
    """

    @staticmethod
    def has_string_chinese_characters(string):
        for c in string:
            if ord(c) < 32 or ord(c) > 122:
                return True
        return False

    def __init__(self):
        """Sets up the tkinter window and prepares it for the user input."""
        # Define colors
        self.bg_color = '#444444'
        self.fg_color = '#AAAAAA'
        self.input_color = '#EEEECC'
        self.pinyin_color = "#CCCCEE"
        self.enough_space_color = "#002200"
        self.crowded_color = "#662200"
        self.archive_bg_color = '#333333'
        # Load the dictionary for character-per-character translation
        self.dict = Dict()
        # Set up variables for input text and live interpretation frame columns
        self.columns = []
        self.full_chinese_text = ""
        # Create  and configure the tkinter root window
        self.root = Tk("Hanzi Interpreter")
        self.root.iconbitmap('res/icon.ico')
        screen_width = self.root.winfo_screenwidth()
        self.window_width = screen_width - 200
        self.input_content = StringVar()
        self.root.geometry(f"{self.window_width}x800+100+100")
        self.root.configure(background=self.bg_color)
        self.root.bind('<Configure>', self.update_window_width)


        # Populate the root window: Text Input
        self.input_content.set("你好")
        self.input_content.trace("w", self.text_changed)
        self.frame_input = Frame(self.root, width=self.window_width,borderwidth=0, bg=self.bg_color)
        self.frame_input.grid(row=0, column=0, stick = "nswe")
        self.entry_chinese_text = Entry(self.frame_input, textvariable=self.input_content, bg=self.bg_color,
                                        fg=self.input_color, justify='center')
        self.entry_chinese_text.grid(row=0, column=0, sticky = "nwe")
        self.entry_chinese_text.config(font=("Courier", 45))
        self.frame_input.grid_columnconfigure(0, weight=1)
        self.entry_chinese_text.bind("<FocusIn>", self.select_text)
        self.entry_chinese_text.focus()

        # Populate the root window: Live Interpretation
        self.frame_live_interpretation = Frame(self.root, width=self.window_width,  borderwidth=0, bg=self.bg_color)
        self.frame_live_interpretation.grid(row=1, column=0, sticky = "nswe")
        self.frame_live_interpretation.grid_columnconfigure(0, weight=1)

        # Populate the root window: Archive
        self.frame_archive = Frame(self.root, width=self.window_width,  borderwidth=0)
        self.frame_archive.grid(row=2, column=0, sticky="swe")

        self.archive_title = Label(self.frame_archive, text = "Archive", bg = self.enough_space_color, fg=self.pinyin_color, padx=3, pady=5)
        self.archive_title.grid(row=0, column=0, sticky="new")
        self.archive_title.config(font=("Courier", 16))

        self.archive = Text(self.frame_archive, bg=self.archive_bg_color, fg=self.fg_color)
        self.archive.grid(row=1, column=0, sticky="ew")
        self.archive.config(state='disabled')

        # Populate the root window: Save Button
        self.button_save_pdf = Button(self.frame_archive, text="Save Archive to File", command=self.save_to_file)
        self.button_save_pdf.grid(row=2, column=0, sticky="sew")
        self.button_save_pdf.config(font=("Courier", 40))

        self.frame_archive.grid_columnconfigure(0, weight=1)

        self.root.bind("<Key>", self.key_pressed)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=1)
        self.text_changed(initial=True)
        self.root.update()
        self.root.mainloop()

    def update_window_width(self, event):
        """Updates the self.window_width variable whenever the users changes the window size"""
        self.window_width = self.root.winfo_width()

    def get_color(self, column_width):
        """Calculates an interpolated color between self.enough_space_color and self.archive_color. """
        upper_limit = 130
        lower_limit = 80

        # Convert hexadecimal to RGB
        rgb_bg_color = hex_to_rgb(self.enough_space_color[1:])
        rgb_archive_color = hex_to_rgb(self.crowded_color[1:])

        # Handling the edge cases
        if column_width >= upper_limit:
            return self.enough_space_color
        elif column_width <= lower_limit:
            return self.crowded_color

        # Linear interpolation
        ratio = (column_width - lower_limit) / (upper_limit - lower_limit)  # will range from 0 to 1
        result_color = tuple(int(ratio * bg + (1 - ratio) * archive) for bg, archive in zip(rgb_bg_color, rgb_archive_color))

        # Converting back to hexadecimal
        return '#' + rgb_to_hex(result_color)

    def set_color_according_to_input_length(self, initial=False):
        """Changes the input field's background color. Used to indicate to the user that the text in the input field
        is getting too long."""
        if initial:
            self.entry_chinese_text.configure(bg=self.enough_space_color)
        else:
            column_width = self.window_width / (len(self.columns) + 1)
            self.entry_chinese_text.configure(bg=self.get_color(column_width))

    def clear_frame_live_interpretation(self):
        # Clear the live interpretation frame
        for widget in self.frame_live_interpretation.winfo_children():
            widget.destroy()
        # Reset the grid configuration for the columns
        for i in range(self.frame_live_interpretation.grid_size()[0]):
            self.frame_live_interpretation.grid_columnconfigure(i, weight=0)
        # Clear the list of columns
        self.columns = []

    def get_translation(self, hanzi):
        """Translate a Chinese character to English"""
        english_translation_raw = self.dict.translate(hanzi)
        english_translation = (english_translation_raw[1:40] + '...') if len(
            english_translation_raw) > 75 else english_translation_raw[1:]
        return english_translation

    def make_interpretation_column(self, i, hanzi):
        """Returns a single column for a single Chinese character, including Hanzi, Pinyin, and translation.
            If there is no Chinese character, the column will contain a message"""
        column = []
        if len(hanzi) > 0:
            # Create the column's upper part (Chinese character)
            message_chinese = Message(self.frame_live_interpretation, text=hanzi, bg=self.bg_color,
                                      fg=self.input_color, padx=30, pady=5)
            message_chinese.config(font=Font(family="Noto Serif SC SemiBold", size=70))
            message_chinese.grid(row=0, column=i, sticky="nsew", padx=1, pady=1)
            # Create the column's middle part (Pinyin)
            label_pinyin = Label(self.frame_live_interpretation, text=pinyin.get(hanzi), bg=self.bg_color,
                                 fg=self.pinyin_color, padx=3, pady=5)
            label_pinyin.grid(row=1, column=i, sticky="nsew", padx=1, pady=1)
            label_pinyin.config(font=("Courier", 30))

            # Create the column's bottom part (English translation)
            message_english = Message(self.frame_live_interpretation, text=self.get_translation(hanzi),
                                      bg=self.bg_color, fg=self.fg_color, padx=0, pady=5)
            message_english.grid(row=2, column=i, padx=1, pady=1)
            message_english.config(font=("Courier", 8))
            # Populate the column with the newly created parts
            column.append(message_chinese)
            column.append(label_pinyin)
            column.append(message_english)
        else:
            message_waiting = Message(self.frame_live_interpretation, text="Waiting for Chinese Text...",
                                      bg=self.bg_color, fg=self.fg_color, padx=3, pady=5)
            message_waiting.grid(row=0, column=0, padx=1, pady=1)
            message_waiting.config(font=("Courier", 20))
            column.append(message_waiting)
        return column

    def text_changed(self, *args, initial=False):
        """updates the live interpretation frame"""
        #print ("Text Changed-------------------------")
        # first, remove previous columns
        self.clear_frame_live_interpretation()
        user_input = self.entry_chinese_text.get()
        if Interpreter.has_string_chinese_characters(user_input):
            # if there are Chinese characters in the input field: rebuild all columns
            for i, hanzi in enumerate(user_input):  # creates a new column for each Chinese character
                if ord(hanzi) < 32 or ord(hanzi) > 122:
                    column = self.make_interpretation_column(i, hanzi)
                    self.columns.append(column)
        else:
            # if there are no Chinese characters in the input field: display a message
            column = self.make_interpretation_column(0, "")
            self.columns.append(column)

        # place all columns in the live interpretation frame
        for j in range(len(self.columns)):
            #print(f"arranging colum {j+1} of {len(self.columns)}")
            self.frame_live_interpretation.grid_columnconfigure(j, weight=1)

        # color the input field according to how full it is.
        self.set_color_according_to_input_length(initial)

    def select_text(self, event):
        """Selects all text in entry_chinese_text"""
        self.entry_chinese_text.select_range(0, 'end')
        self.entry_chinese_text.icursor('end')

    def drop_current_line_to_archive(self):
        """Clears the entry_chinese_text input field and adds its content to the archive below"""
        user_input = self.entry_chinese_text.get()
        print(f"Moving current line '{user_input}' to archive below.")
        self.archive.config(state='normal')
        self.full_chinese_text += user_input + "\n"
        # Add the Chinese text

        self.archive.insert(END, user_input)
        self.archive.insert(END, "  -  ")

        # Add the Pinyin
        for hanzi in user_input:
            if ord(hanzi) < 32 or ord(hanzi) > 122:
                self.archive.insert(END, pinyin.get(hanzi) + " ")
            else:
                self.archive.insert(END, pinyin.get(hanzi))
        self.archive.insert(END, "\n")
        self.archive.see("end")
        self.archive.config(state='disabled')
        # Clear input field and live interpretation frame.
        self.input_content.set("")
        self.clear_frame_live_interpretation()
        self.text_changed()

    def key_pressed(self, event):
        """Checks if the user has pressed the enter key. If so, the text from the entry is moved to the archive frame.
        Also, refocuses on the input field in case the user has clicked anywhere else on the window."""
        if event.keysym == 'Return':
            self.drop_current_line_to_archive()
        self.entry_chinese_text.focus()


    def save_to_file(self):
        """Opens a file dialog and saves all text the user has entered to a file (either .pdf or .txt)"""
        # Make sure the input field is included in the export file, even if not dropped manually by the user
        if len(self.entry_chinese_text.get()) > 0:
            self.drop_current_line_to_archive()
        # Open file dialog for output file location and fily type:
        save_location = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                     filetypes=[("PDF Files", "*.pdf"), ("Text Files", "*.txt")])
        # Save file
        if save_location.endswith(".pdf"):
            print("saving pdf....")
            headline = os.path.splitext(os.path.basename(save_location))[0]
            pdf_creator = PdfCreator(input_text=self.full_chinese_text, headline=headline, output_file=save_location)
            pdf_creator.create_pdf()
        elif save_location.endswith(".txt"):
            print("saving txt....")
            with open(save_location, "w+", encoding="utf8") as f:
                f.write(self.archive.get("1.0", END))
        else:
            print("invalid file type")


if __name__ == '__main__':
    interpreter = Interpreter()
