from tkinter import *
from PIL import Image, ImageTk
from tkinter import filedialog
from tkinter import font
from tkinter import colorchooser
import openai
import os
from dotenv import load_dotenv

# Load OpenAI API key from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

root = Tk()
root.title("Simple Text Editor")
root.geometry("1000x600")
root.resizable(True, True)

# Set variable for open file name
global open_status_name
open_status_name = False

global selected
selected = False

# Create a toolbar
toolbar_frame = Frame(root)
toolbar_frame.pack(fill=X, pady=5)

# Create a main frame
my_frame = Frame(root)
my_frame.pack(pady=5)

# Create scrollbar for the textbox
text_scroll = Scrollbar(my_frame)
text_scroll.pack(side=RIGHT, fill=Y)

# Horizontal scrollbar
hor_scroll = Scrollbar(my_frame, orient='horizontal')
hor_scroll.pack(side=BOTTOM, fill=X)

# Create text box
my_text = Text(my_frame, width=80, height=20, font=("Helvetica", 16), selectbackground="lightgrey",
               selectforeground="black", undo=True,
               yscrollcommand=text_scroll.set, xscrollcommand=hor_scroll.set, wrap="none")
my_text.pack()

# Configure scrollbar
text_scroll.config(command=my_text.yview)
hor_scroll.config(command=my_text.xview)

# Create menu
my_menu = Menu(root)
root.config(menu=my_menu)

# Add status bar to bottom
status_bar = Label(root, text='Ready        ', anchor=E)
status_bar.pack(fill=X, side=BOTTOM, ipady=15)

# ***************************** File Menu ********************************
def new_file(e):
    my_text.delete("1.0", END)
    root.title("Untitled")
    status_bar.config(text="New File        ")
    global open_status_name
    open_status_name = False

# Open file
def open_file(e):
    my_text.delete("1.0", END)
    text_file = filedialog.askopenfilename(initialdir="E:/", title="Open File",
                                           filetypes=(("Text Files", "*.txt"), ("HTML Files", "*.html"),
                                                     ("Python Files", "*.py"), ("All Files", "*.*")))

    if text_file:
        global open_status_name
        open_status_name = text_file

    name = text_file
    status_bar.config(text=f'{name}        ')
    name = name.replace("E:/", "")
    root.title(f'{name}')

    with open(text_file, 'r') as file:
        stuff = file.read()
        my_text.insert(END, stuff)

def save_as_file(e):
    text_file = filedialog.asksaveasfilename(defaultextension=".*", initialdir="E:/", title="Save File",
                                             filetypes=(("Text Files", "*.txt"), ("HTML Files", "*.html"),
                                                       ("Python Files", "*.py"), ("All Files", "*.*")))

    if text_file:
        name = text_file
        status_bar.config(text=f'Saved: {name}        ')
        name = name.replace("E:/", "")
        root.title(f'{name}')

        with open(text_file, 'w') as file:
            file.write(my_text.get(1.0, END))

def save_file(e):
    global open_status_name
    if open_status_name:
        with open(open_status_name, 'w') as file:
            file.write(my_text.get(1.0, END))
        status_bar.config(text=f'Saved: {open_status_name}        ')

    else:
        save_as_file(e)

# Add file menu
file_menu = Menu(my_menu, tearoff=False)
my_menu.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="New", command=new_file, accelerator="(Ctrl+n)")
file_menu.add_command(label="Open", command=open_file, accelerator="(Ctrl+o)")
file_menu.add_command(label="Save", command=save_file, accelerator="(Ctrl+s)")
file_menu.add_command(label="Save As", command=save_as_file)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)

# File bindings
root.bind('<Control-Key-n>', new_file)
root.bind('<Control-Key-o>', open_file)
root.bind('<Control-Key-s>', save_file)

# ************************* Edit Menu *************************
def cut_text(e):
    global selected
    if e:
        selected = root.clipboard_get()
    else:
        if my_text.selection_get():
            selected = my_text.selection_get()
            my_text.delete("sel.first", "sel.last")
            root.clipboard_clear()
            root.clipboard_append(selected)

def copy_text(e):
    global selected
    if e:
        selected = root.clipboard_get()
    if my_text.selection_get():
        selected = my_text.selection_get()
        root.clipboard_clear()
        root.clipboard_append(selected)

def paste_text(e):
    global selected
    if e:
        selected = root.clipboard_get()
    else:
        if selected:
            position = my_text.index(INSERT)
            my_text.insert(position, selected)

def select_all(e):
    my_text.tag_add('sel', '1.0', 'end')

# Add edit menu
edit_menu = Menu(my_menu, tearoff=False)
my_menu.add_cascade(label="Edit", menu=edit_menu)
edit_menu.add_command(label="Cut", command=lambda: cut_text(False), accelerator="(Ctrl+x)")
edit_menu.add_command(label="Copy", command=lambda: copy_text(False), accelerator="(Ctrl+c)")
edit_menu.add_command(label="Paste", command=lambda: paste_text(False), accelerator="(Ctrl+v)")
edit_menu.add_separator()
edit_menu.add_command(label="Undo", command=my_text.edit_undo, accelerator="(Ctrl+z)")
edit_menu.add_command(label="Redo", command=my_text.edit_redo, accelerator="(Ctrl+y)")
edit_menu.add_separator()
edit_menu.add_command(label="Select All", command=lambda: select_all(True), accelerator="(Ctrl+a)")

# Edit bindings
root.bind('<Control-Key-x>', cut_text)
root.bind('<Control-Key-c>', copy_text)
root.bind('<Control-Key-v>', paste_text)

# **************************** AI Integration (OpenAI API) *****************************
def generate_summary():
    text_content = my_text.get("1.0", END)
    
    if text_content.strip():
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"Summarize the following text:\n\n{text_content}"}
                ],
                max_tokens=150
            )
            summary = response.choices[0].message['content'].strip()
            my_text.delete(1.0, END)  # Clear existing text
            my_text.insert(END, summary)  # Insert the summary directly
        except Exception as e:
            print(f"Error: {e}")

def suggest_content():
    text_content = my_text.get("1.0", END)
    if text_content.strip():
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"Suggest content based on the following text:\n\n{text_content}"}
                ],
                max_tokens=500
            )
            suggestion = response.choices[0].message['content'].strip()
            my_text.delete(1.0, END)  # Clear existing text
            my_text.insert(END, suggestion)  # Insert the suggested content directly
        except Exception as e:
            print(f"Error: {e}")

def improve_vocabulary():
    text_content = my_text.get("1.0", END)
    if text_content.strip():
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"Improve the vocabulary of the following text:\n\n{text_content}"}
                ],
                max_tokens=150
            )
            improved_text = response.choices[0].message['content'].strip()
            my_text.delete(1.0, END)  # Clear existing text
            my_text.insert(END, improved_text)  # Insert the improved text directly
        except Exception as e:
            print(f"Error: {e}")

def correct_grammar():
    text_content = my_text.get("1.0", END)
    if text_content.strip():
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"Correct the grammar of the following text:\n\n{text_content}"}
                ],
                max_tokens=150
            )
            corrected_text = response.choices[0].message['content'].strip()
            my_text.delete(1.0, END)  # Clear existing text
            my_text.insert(END, corrected_text)  # Insert the corrected grammar directly
        except Exception as e:
            print(f"Error: {e}")

def correct_spelling():
    text_content = my_text.get("1.0", END)
    if text_content.strip():
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"Correct the spelling of the following text:\n\n{text_content}"}
                ],
                max_tokens=150
            )
            corrected_text = response.choices[0].message['content'].strip()
            my_text.delete(1.0, END)  # Clear existing text
            my_text.insert(END, corrected_text)  # Insert the corrected spelling directly
        except Exception as e:
            print(f"Error: {e}")

# Add AI options to the Edit menu
edit_menu.add_command(label="Generate Summary", command=generate_summary, accelerator="(Ctrl+g)")
edit_menu.add_command(label="Suggest Content", command=suggest_content, accelerator="(Ctrl+shift+s)")
edit_menu.add_command(label="Improve Vocabulary", command=improve_vocabulary, accelerator="(Ctrl+shift+i)")
edit_menu.add_command(label="Correct Grammar", command=correct_grammar, accelerator="(Ctrl+shift+g)")
edit_menu.add_command(label="Correct Spelling", command=correct_spelling, accelerator="(Ctrl+shift+p)")

# ***************************** ToolBar *****************************
# Buttons for the new features
suggest_button = Button(toolbar_frame, text="Suggest Content", command=suggest_content)
suggest_button.grid(row=0, column=0, padx=8, pady=2)

vocabulary_button = Button(toolbar_frame, text="Improve Vocabulary", command=improve_vocabulary)
vocabulary_button.grid(row=0, column=1, padx=8, pady=2)

grammar_button = Button(toolbar_frame, text="Correct Grammar", command=correct_grammar)
grammar_button.grid(row=0, column=2, padx=8, pady=2)

spelling_button = Button(toolbar_frame, text="Correct Spelling", command=correct_spelling)
spelling_button.grid(row=0, column=3, padx=8, pady=2)

root.mainloop()
