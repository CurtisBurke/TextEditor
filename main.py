import tkinter as tk
from tkinter import ttk, messagebox, font
import tkinter.filedialog as fd
import tkinter.scrolledtext as st
import os
import pickle
import datetime


class TextEditor(tk.Tk):
    def __init__(self, parent=None, font=("Arial", 12, "normal", "roman")):
        tk.Tk.__init__(self)
        self.font=font
        self.title_txt = "Text Editor"
        self.title(self.title_txt)
        self.supported_extensions = (".txt", ".texteditor")
        self.ext = ".texteditor"
        self.preferences = {"dir" : "C:Users\\{}\\Documents\\".format(os.getlogin()),
                            "font" : ("Arial", 12, "normal", "roman")
                            }
        self.runs = []
        self.runs.append(Run("0.0", tk.END))
        self.menu = tk.Menu(self)
        self.configure(menu=self.menu)
        self.file= tk.Menu(self.menu, tearoff=False)
        self.file.add_command(label="New     Ctr+N", command=self.new)
        self.file.add_command(label="Open     Ctr+O", command=self.open)
        self.file.add_separator()
        self.file.add_command(label="Save     Ctr+S", command=lambda askfile=False : self.save(askfile))
        self.file.add_command(label="Save As", command=self.save)
        self.file.add_separator()
        self.file.add_command(label="Exit")
        self.menu.add_cascade(label="File", menu=self.file)
        self.filename = tk.Label(self, text = "Untitled")
        self.filename.pack()
        self.format_frame = tk.Frame(self)
        self.font_selector = ttk.Entry(self.format_frame)
        self.font_selector.insert(0, self.preferences["font"][0])
        self.font_button = ttk.Button(self.format_frame, width=2, command=self.show_drop_down)
        self.font_size_selector = tk.Spinbox(self.format_frame, width=4, values=list(range(6, 100)), wrap=True)
        self.font_size_selector.bind("<Button-1>", self.change_font_size)
        self.font_selector.pack(side="left")
        self.font_button.pack(side="left")
        self.font_size_selector.pack(side="left")
        self.format_buttons = {"bold":{"method":self.bold},
                               "italic":{"method":self.italic},
                               "left":{"method":lambda t = "left" : self.justify(t)},
                               "center":{"method":lambda  t = "center" : self.justify(t)},
                               "right":{"method": lambda t = "right": self.justify(t)}}
        for key in self.format_buttons.keys():
            self.format_buttons[key]["button"] = ttk.Button(self.format_frame, text=key, command=self.format_buttons[key]["method"])
            self.format_buttons[key]["button"].pack(side="left")
        self.text_editor = tk.Text(self)
        self.text_editor.configure(font=self.preferences["font"])
        self.format_frame.pack()
        self.text_editor.pack(fill="both", expand=True)
        self.text_editor.tag_configure("bold", font=("Arial", 12, "bold"))
        self.text_editor.tag_configure("italic", font=("Arial", 12, "italic"))
        self.text_editor.tag_configure("bold_italic", font=("Arial", 12, "bold", "italic"))
        self.text_editor.tag_configure("right", justify="right")
        self.text_editor.tag_configure("center", justify="center")
        self.hot_keys()
        self.document = Document(directory = self.preferences["dir"])
        self.update()
        self.config_drop_down()

    def change_font_size(self, *event):
        if tk.SEL:
            print("Selected")
        else:
            print("Not selected")

    def show_drop_down(self, *event):
        x = self.format_frame.winfo_x()
        y = self.text_editor.winfo_y()
        self.t.place(x=x, y=y, anchor="nw")

    def config_drop_down(self):
        # self.update_idletasks()
        self.t = st.ScrolledText(width=20, background="pink", wrap="word")
        x = self.format_frame.winfo_x()
        y = self.text_editor.winfo_y()
        self.t.tag_configure("highlight", background="blue")
        self.t.configure(cursor="hand2")

        x = 0
        for f in font.families():
            tag = f.replace(" ", "")
            print(tag)
            self.t.tag_configure(tag, font=(f, 10))
            self.t.tag_bind(tag, "<Enter>", lambda event, t = tag : self.highlight(t))
            self.t.tag_bind(tag, "<Leave>", lambda event, t=tag: self.remove_highlight(t))
            self.t.tag_bind(tag, "<Button-1>", lambda event, t = f : self.change_font(t))
            self.t.insert(tk.END, "{}\n".format(f), tag)
            x += 1
            if x == 5:
                break
        self.t.place(x=x, y=y, anchor="nw")
        self.t.configure(state="disabled")
        self.t.place_forget()

    def change_font(self, t):
        self.font_selector.delete(0, tk.END)
        self.font_selector.insert(0, t)
        self.t.place_forget()
        if self.text_editor.tag_ranges(tk.SEL):
            self.text_editor.tag_configure("font", font=(t, 10, "normal", "roman"))
            self.text_editor.tag_add("font", tk.SEL_FIRST, tk.SEL_LAST)
            self.runs.append(Run(tk.SEL_FIRST, tk.SEL_LAST))
        else:
            print("Not selected")
        #self.text_editor.configure(font=(t, 10, "normal", "roman"))

    def highlight(self, t):
        self.t.tag_configure(t, background="blue")

    def remove_highlight(self, t):
        self.t.tag_configure(t, background="pink")

    def hot_keys(self):
        self.bind("<Control-o>", self.open)
        self.bind("<Control-s>", lambda event, b=False : self.save(askfile=b))


    def bold(self):
        if not self.text_editor.tag_ranges(tk.SEL):
            return
        if "bold" in self.text_editor.tag_names(tk.SEL_FIRST):
            self.text_editor.tag_remove("bold", tk.SEL_FIRST, tk.SEL_LAST)
        elif "italic" in self.text_editor.tag_names(tk.SEL_FIRST):
            self.bold_italic()
        elif "bold_italic" in self.text_editor.tag_names(tk.SEL_FIRST):
            self.bold_italic(self.italic)
        else:
            self.text_editor.tag_add("bold", tk.SEL_FIRST, tk.SEL_LAST)

    def italic(self):
        if not self.text_editor.tag_ranges(tk.SEL):
            return
        if "italic" in self.text_editor.tag_names(tk.SEL_FIRST):
            self.text_editor.tag_remove("italic", tk.SEL_FIRST, tk.SEL_LAST)
        elif "bold" in self.text_editor.tag_names(tk.SEL_FIRST):
            self.bold_italic()
        elif "bold_italic" in self.text_editor.tag_names(tk.SEL_FIRST):
            self.bold_italic(self.bold)
        else:
            self.text_editor.tag_add("italic", tk.SEL_FIRST, tk.SEL_LAST)

    def bold_italic(self, *args):
        if not self.text_editor.tag_ranges(tk.SEL):
            return
        if args:
            self.text_editor.tag_remove("bold_italic", tk.SEL_FIRST, tk.SEL_LAST)
            args[0]()
        else:
            self.text_editor.tag_remove("bold", tk.SEL_FIRST, tk.SEL_LAST)
            self.text_editor.tag_remove("italic", tk.SEL_FIRST, tk.SEL_LAST)
            self.text_editor.tag_add("bold_italic", tk.SEL_FIRST, tk.SEL_LAST)


    def underline(self):
        self.text_editor.tag_add("underline", tk.SEL_FIRST, tk.SEL_LAST)

    def justify(self, type):
        if not self.text_editor.tag_ranges(tk.SEL):
            return
        for just in ["left", "right", "center"]:
            if just in self.text_editor.tag_names(tk.SEL_FIRST):
                self.text_editor.tag_remove(just, tk.SEL_FIRST)
        self.text_editor.tag_add(type, tk.SEL_FIRST, tk.SEL_LAST)

    def new(self):
        if not messagebox.askyesno(self.title_txt, "Do you want to save first?"):
            self.text_editor.delete("1.0", tk.END + "-1c")

    def open(self, *hotkey):
        file_to_open =  fd.askopenfile(
        initialdir = self.preferences["dir"],
        title = "Select a file",
        filetypes = [('Text Files', self.supported_extensions)])
        #self.new()
        if file_to_open:
            if file_to_open.name.split(".")[1] != "texteditor":
                with open(file_to_open.name, "rb") as f:
                    self.document.raw = f.read()
            else:
                with open(file_to_open.name, "rb") as f:
                    self.document = pickle.load(f)
            self.text_editor.insert("1.0", self.document.raw)
            self.filename.configure(text=file_to_open.name)
            self.apply_formatting(self.document.formatting)


    def apply_formatting(self, formatting_dict):
        for key in formatting_dict:
            for idx in formatting_dict[key]:
                self.text_editor.tag_add(key, idx[0], idx[1])

    def save(self, *event, askfile=True):
        print("askfile", askfile)
        if askfile:
            fn = fd.asksaveasfile()
            if fn == None:
                return
            else:
                suffix = ".texteditor"
                if not fn.name.endswith(self.supported_extensions):
                    path = os.path.join(fn.name + suffix)
                else:
                    self.document.path = fn.name

        # Save as txt
        if not self.document.path.endswith(self.ext):
            with open(self.document.path, "w") as f:
                f.write(self.text_editor.get("1.0", tk.END+"-1c"))

        #Save as this format
        else:
            self.document.raw = self.text_editor.get("1.0", tk.END + "-1c")
            for tag in self.text_editor.tag_names("1.0"):
               if tag in self.document.formatting.keys():
                   rge = self.text_editor.tag_ranges(tag)
                   for x in range(0, len(rge), 2):
                        self.document.formatting[tag].append([rge[x].string, rge[x+1].string])
            try:
                with open(self.document.path, "wb") as f:
                    pickle.dump(self.document, f, protocol=pickle.HIGHEST_PROTOCOL)
            except FileNotFoundError:
                self.save(askfile=True)



class Document:
    def __init__(self, directory):
        self.raw = ""
        self.path = directory + "untitled.texteditor"
        self.name = None
        self.created_at = datetime.datetime.now()
        self.created_by = os.getlogin()
        self.history = []
        self.formatting = {
                            "bold" : [],
                            "italic" : [],
                            "bold_italic" : [],
                            "center" : [],
                            "right" : [],
                            "font" : []
        }

class Run:
    def __init__(self, start, end, bold="normal", italic="roman", center=False, right=False, font="Arial", size=12):
        self.bold = bold
        self.italic = italic

        self.center = center
        self.right = right

        self.font = font
        self.font_size = size


if __name__ == '__main__':
    text_editor = TextEditor()
    text_editor.mainloop()

