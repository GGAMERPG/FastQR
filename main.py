import tkinter as tk
from tkinter import messagebox, filedialog
import qrcode
from PIL import Image, ImageTk
import os
import sys
import traceback


# ===== Перехват ошибок =====
def log_error_to_file():
    with open("error_log.txt", "a", encoding="utf-8") as f:
        f.write("\n" + "=" * 50 + "\n")
        traceback.print_exc(file=f)


sys.excepthook = lambda exctype, value, tb: log_error_to_file()

# ===== Цветовая схема =====
COLORS = {
    "bg_dark": "#1e1e1e",
    "bg_medium": "#252526",
    "bg_light": "#2d2d30",
    "text": "#cccccc",
    "text_bright": "#ffffff",
    "accent": "#2e7d32",
    "button": "#2e7d32",
    "button_hover": "#1b5e20",
    "border": "#3f3f46"
}

# ===== Словарь переводов =====
TEXTS = {
    "ru": {
        "title": "FastQR — генератор QR-кодов",
        "logo_sub": "десктопный генератор QR-кодов",
        "link_label": "Введите ссылку:",
        "format_label": "Формат сохранения:",
        "none": "не сохранять",
        "png": ".png",
        "jpeg": ".jpeg",
        "size_label": "Размер QR-кода (px):",
        "400": "400",
        "600": "600",
        "800": "800",
        "1000": "1000",
        "folder_label": "Папка для сохранения:",
        "not_selected": "не выбрана",
        "browse": "Обзор",
        "update": "Обновить QR-код",
        "save": "Сохранить в файл",
        "exit": "Выход",
        "info_none": "Информация",
        "info_none_msg": "Выбран формат 'не сохранять'.",
        "warning_no_link": "Предупреждение",
        "warning_no_link_msg": "Не указана ссылка для генерации QR-кода.",
        "success": "Успех",
        "success_msg": "QR-код сохранён:\n{}",
        "error": "Ошибка",
        "error_msg": "Не удалось сохранить файл:\n{}",
        "error_startup": "Не удалось запустить программу. Подробности в error_log.txt",
        "enter_link": "Введите ссылку",
        "ru": "Русский",
        "en": "English",
    },
    "en": {
        "title": "FastQR — QR code generator",
        "logo_sub": "desktop QR generator",
        "link_label": "Enter link:",
        "format_label": "Save format:",
        "none": "don't save",
        "png": ".png",
        "jpeg": ".jpeg",
        "size_label": "QR code size (px):",
        "400": "400",
        "600": "600",
        "800": "800",
        "1000": "1000",
        "folder_label": "Save folder:",
        "not_selected": "not selected",
        "browse": "Browse",
        "update": "Update QR code",
        "save": "Save to file",
        "exit": "Exit",
        "info_none": "Information",
        "info_none_msg": "Selected format 'don't save'.",
        "warning_no_link": "Warning",
        "warning_no_link_msg": "No link provided for QR code generation.",
        "success": "Success",
        "success_msg": "QR code saved:\n{}",
        "error": "Error",
        "error_msg": "Failed to save file:\n{}",
        "error_startup": "Failed to start the program. See error_log.txt for details.",
        "enter_link": "Enter link",
        "ru": "Русский",
        "en": "English",
    }
}


class QRCodeGenerator:
    def __init__(self, master):
        self.master = master
        self.master.iconbitmap("LOGO_QR-CODE_Generated.ico")
        self.lang = "ru"
        self.update_title()

        self.master.resizable(True, True)
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.master.configure(bg=COLORS["bg_dark"])

        self.link_var = tk.StringVar()
        self.format_var = tk.StringVar(value="none")
        self.size_var = tk.IntVar(value=400)
        self.last_dir = ""

        self.folder_label = None
        self.canvas = None
        self.lang_ru_rb = None
        self.lang_en_rb = None

        self.create_layout()
        self.update_qr()
        self.center_window()

    def center_window(self):
        self.master.update_idletasks()
        width = self.master.winfo_width()
        height = self.master.winfo_height()
        x = (self.master.winfo_screenwidth() // 2) - (width // 2)
        y = (self.master.winfo_screenheight() // 2) - (height // 2)
        self.master.geometry(f'{width}x{height}+{x}+{y}')

    def update_title(self):
        self.master.title(TEXTS[self.lang]["title"])

    def get_text(self, key):
        return TEXTS[self.lang].get(key, key)

    def switch_language(self):
        self.update_title()
        self.update_header_texts()
        self.update_main_content_texts()

    def update_header_texts(self):
        self.title_label.config(text="FastQR")
        self.subtitle_label.config(text=self.get_text("logo_sub"))

    def update_main_content_texts(self):
        self.link_label.config(text=self.get_text("link_label"))
        self.format_label.config(text=self.get_text("format_label"))
        self.size_label.config(text=self.get_text("size_label"))
        self.folder_label_text.config(text=self.get_text("folder_label"))

        self.none_rb.config(text=self.get_text("none"))
        self.png_rb.config(text=self.get_text("png"))
        self.jpeg_rb.config(text=self.get_text("jpeg"))

        self.size400_rb.config(text=self.get_text("400"))
        self.size600_rb.config(text=self.get_text("600"))
        self.size800_rb.config(text=self.get_text("800"))
        self.size1000_rb.config(text=self.get_text("1000"))

        self.browse_btn.config(text=self.get_text("browse"))
        self.update_btn.config(text=self.get_text("update"))
        self.save_btn.config(text=self.get_text("save"))
        self.exit_btn.config(text=self.get_text("exit"))

        if self.last_dir:
            self.folder_label.config(text=self.last_dir)
        else:
            self.folder_label.config(text=self.get_text("not_selected"))

        self.lang_ru_rb.config(text=self.get_text("ru"))
        self.lang_en_rb.config(text=self.get_text("en"))

        self.update_qr()

    def create_layout(self):
        # Главный контейнер
        main_container = tk.Frame(self.master, bg=COLORS["bg_dark"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Левая колонка (шапка + настройки)
        left_column = tk.Frame(main_container, bg=COLORS["bg_medium"])
        left_column.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_column.config(width=350)
        left_column.pack_propagate(False)

        # === Шапка ===
        header_frame = tk.Frame(left_column, bg=COLORS["bg_medium"], height=60)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)

        self.title_label = tk.Label(
            header_frame,
            text="FastQR",
            font=("Segoe UI", 24, "bold"),
            fg=COLORS["accent"],
            bg=COLORS["bg_medium"],
            anchor="w"
        )
        self.title_label.pack(side=tk.LEFT, padx=(20, 5))

        self.subtitle_label = tk.Label(
            header_frame,
            text=self.get_text("logo_sub"),
            font=("Segoe UI", 10),
            fg=COLORS["accent"],
            bg=COLORS["bg_medium"],
            anchor="w"
        )
        self.subtitle_label.pack(side=tk.LEFT, padx=(0, 20), pady=(12, 0))

        # === Панель настроек ===
        left_content = tk.Frame(left_column, bg=COLORS["bg_medium"])
        left_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # ===== Переключатель языка =====
        lang_frame = tk.Frame(left_content, bg=COLORS["bg_medium"])
        lang_frame.pack(fill=tk.X, pady=(0, 15))

        self.lang_var = tk.StringVar(value=self.lang)

        self.lang_ru_rb = tk.Radiobutton(
            lang_frame,
            text=self.get_text("ru"),
            variable=self.lang_var,
            value="ru",
            command=self.on_language_change,
            bg=COLORS["bg_medium"],
            fg=COLORS["text"],
            selectcolor=COLORS["bg_light"],
            activebackground=COLORS["bg_medium"],
            activeforeground=COLORS["text_bright"],
            font=("Segoe UI", 9)
        )
        self.lang_ru_rb.pack(side=tk.LEFT, padx=(0, 15))

        self.lang_en_rb = tk.Radiobutton(
            lang_frame,
            text=self.get_text("en"),
            variable=self.lang_var,
            value="en",
            command=self.on_language_change,
            bg=COLORS["bg_medium"],
            fg=COLORS["text"],
            selectcolor=COLORS["bg_light"],
            activebackground=COLORS["bg_medium"],
            activeforeground=COLORS["text_bright"],
            font=("Segoe UI", 9)
        )
        self.lang_en_rb.pack(side=tk.LEFT, padx=(0, 15))
        # ===== Конец переключателя =====

        self.link_label = tk.Label(
            left_content,
            text=self.get_text("link_label"),
            anchor="w",
            bg=COLORS["bg_medium"],
            fg=COLORS["text"],
            font=("Segoe UI", 10)
        )
        self.link_label.pack(fill=tk.X, pady=(0, 5))

        # Поле ввода
        entry_link = tk.Entry(
            left_content,
            textvariable=self.link_var,
            width=35,
            bg=COLORS["bg_light"],
            fg=COLORS["text_bright"],
            insertbackground=COLORS["text_bright"],
            relief=tk.FLAT,
            bd=3
        )
        entry_link.pack(fill=tk.X, pady=(0, 5))

        # Кнопка вставки
        def paste_from_clipboard():
            try:
                text = entry_link.clipboard_get()
                entry_link.insert(tk.INSERT, text)
            except:
                pass

        paste_btn = tk.Button(
            left_content,
            text="Вставить из буфера обмена",
            command=paste_from_clipboard,
            bg=COLORS["button"],
            fg=COLORS["text_bright"],
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            padx=8,
            pady=4,
            cursor="hand2"
        )
        paste_btn.pack(fill=tk.X, pady=(0, 15))

        self.format_label = tk.Label(
            left_content,
            text=self.get_text("format_label"),
            anchor="w",
            bg=COLORS["bg_medium"],
            fg=COLORS["text"],
            font=("Segoe UI", 10)
        )
        self.format_label.pack(fill=tk.X, pady=(0, 5))

        format_frame = tk.Frame(left_content, bg=COLORS["bg_medium"])
        format_frame.pack(fill=tk.X, pady=(0, 15))

        self.none_rb = tk.Radiobutton(
            format_frame,
            text=self.get_text("none"),
            variable=self.format_var,
            value="none",
            bg=COLORS["bg_medium"],
            fg=COLORS["text"],
            selectcolor=COLORS["bg_light"],
            activebackground=COLORS["bg_medium"],
            activeforeground=COLORS["text_bright"],
            font=("Segoe UI", 9)
        )
        self.none_rb.pack(side=tk.LEFT, padx=(0, 15))

        self.png_rb = tk.Radiobutton(
            format_frame,
            text=self.get_text("png"),
            variable=self.format_var,
            value="png",
            bg=COLORS["bg_medium"],
            fg=COLORS["text"],
            selectcolor=COLORS["bg_light"],
            activebackground=COLORS["bg_medium"],
            activeforeground=COLORS["text_bright"],
            font=("Segoe UI", 9)
        )
        self.png_rb.pack(side=tk.LEFT, padx=(0, 15))

        self.jpeg_rb = tk.Radiobutton(
            format_frame,
            text=self.get_text("jpeg"),
            variable=self.format_var,
            value="jpeg",
            bg=COLORS["bg_medium"],
            fg=COLORS["text"],
            selectcolor=COLORS["bg_light"],
            activebackground=COLORS["bg_medium"],
            activeforeground=COLORS["text_bright"],
            font=("Segoe UI", 9)
        )
        self.jpeg_rb.pack(side=tk.LEFT, padx=(0, 15))

        self.size_label = tk.Label(
            left_content,
            text=self.get_text("size_label"),
            anchor="w",
            bg=COLORS["bg_medium"],
            fg=COLORS["text"],
            font=("Segoe UI", 10)
        )
        self.size_label.pack(fill=tk.X, pady=(0, 5))

        size_frame = tk.Frame(left_content, bg=COLORS["bg_medium"])
        size_frame.pack(fill=tk.X, pady=(0, 15))

        self.size400_rb = tk.Radiobutton(
            size_frame,
            text=self.get_text("400"),
            variable=self.size_var,
            value=400,
            command=self.update_qr,
            bg=COLORS["bg_medium"],
            fg=COLORS["text"],
            selectcolor=COLORS["bg_light"],
            activebackground=COLORS["bg_medium"],
            activeforeground=COLORS["text_bright"],
            font=("Segoe UI", 9)
        )
        self.size400_rb.pack(side=tk.LEFT, padx=(0, 15))

        self.size600_rb = tk.Radiobutton(
            size_frame,
            text=self.get_text("600"),
            variable=self.size_var,
            value=600,
            command=self.update_qr,
            bg=COLORS["bg_medium"],
            fg=COLORS["text"],
            selectcolor=COLORS["bg_light"],
            activebackground=COLORS["bg_medium"],
            activeforeground=COLORS["text_bright"],
            font=("Segoe UI", 9)
        )
        self.size600_rb.pack(side=tk.LEFT, padx=(0, 15))

        self.size800_rb = tk.Radiobutton(
            size_frame,
            text=self.get_text("800"),
            variable=self.size_var,
            value=800,
            command=self.update_qr,
            bg=COLORS["bg_medium"],
            fg=COLORS["text"],
            selectcolor=COLORS["bg_light"],
            activebackground=COLORS["bg_medium"],
            activeforeground=COLORS["text_bright"],
            font=("Segoe UI", 9)
        )
        self.size800_rb.pack(side=tk.LEFT, padx=(0, 15))

        self.size1000_rb = tk.Radiobutton(
            size_frame,
            text=self.get_text("1000"),
            variable=self.size_var,
            value=1000,
            command=self.update_qr,
            bg=COLORS["bg_medium"],
            fg=COLORS["text"],
            selectcolor=COLORS["bg_light"],
            activebackground=COLORS["bg_medium"],
            activeforeground=COLORS["text_bright"],
            font=("Segoe UI", 9)
        )
        self.size1000_rb.pack(side=tk.LEFT, padx=(0, 15))

        self.folder_label_text = tk.Label(
            left_content,
            text=self.get_text("folder_label"),
            anchor="w",
            bg=COLORS["bg_medium"],
            fg=COLORS["text"],
            font=("Segoe UI", 10)
        )
        self.folder_label_text.pack(fill=tk.X, pady=(0, 5))

        folder_frame = tk.Frame(left_content, bg=COLORS["bg_medium"])
        folder_frame.pack(fill=tk.X, pady=(0, 15))

        self.folder_label = tk.Label(
            folder_frame,
            text=self.get_text("not_selected"),
            relief=tk.SUNKEN,
            bd=1,
            anchor="w",
            bg=COLORS["bg_light"],
            fg=COLORS["text"],
            width=30
        )
        self.folder_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.browse_btn = tk.Button(
            folder_frame,
            text=self.get_text("browse"),
            command=self.choose_folder,
            bg=COLORS["button"],
            fg=COLORS["text_bright"],
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            padx=10,
            pady=3,
            activebackground=COLORS["button_hover"],
            activeforeground=COLORS["text_bright"],
            cursor="hand2"
        )
        self.browse_btn.pack(side=tk.RIGHT)

        # Первая строка кнопок: Обновить и Сохранить
        button_frame_row1 = tk.Frame(left_content, bg=COLORS["bg_medium"])
        button_frame_row1.pack(fill=tk.X, pady=(10, 5))

        self.update_btn = tk.Button(
            button_frame_row1,
            text=self.get_text("update"),
            command=self.update_qr,
            bg=COLORS["button"],
            fg=COLORS["text_bright"],
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=15,
            pady=5,
            activebackground=COLORS["button_hover"],
            activeforeground=COLORS["text_bright"],
            cursor="hand2"
        )
        self.update_btn.pack(side=tk.LEFT, padx=(0, 10), expand=True, fill=tk.X)

        self.save_btn = tk.Button(
            button_frame_row1,
            text=self.get_text("save"),
            command=self.save_qr,
            bg=COLORS["button"],
            fg=COLORS["text_bright"],
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=15,
            pady=5,
            activebackground=COLORS["button_hover"],
            activeforeground=COLORS["text_bright"],
            cursor="hand2"
        )
        self.save_btn.pack(side=tk.LEFT, expand=True, fill=tk.X)

        # Вторая строка: кнопка Выход
        button_frame_row2 = tk.Frame(left_content, bg=COLORS["bg_medium"])
        button_frame_row2.pack(fill=tk.X, pady=(5, 0))

        self.exit_btn = tk.Button(
            button_frame_row2,
            text=self.get_text("exit"),
            command=self.on_closing,
            bg=COLORS["button"],
            fg=COLORS["text_bright"],
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=15,
            pady=5,
            activebackground=COLORS["button_hover"],
            activeforeground=COLORS["text_bright"],
            cursor="hand2"
        )
        self.exit_btn.pack(expand=True, fill=tk.X)

        # Правая область — QR-код
        right_frame = tk.Frame(
            main_container,
            bg=COLORS["bg_medium"],
            relief=tk.FLAT,
            bd=1
        )
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        canvas_container = tk.Frame(right_frame, bg=COLORS["bg_medium"])
        canvas_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        self.canvas = tk.Canvas(
            canvas_container,
            bg=COLORS["bg_light"],
            highlightthickness=1,
            highlightbackground=COLORS["border"]
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def on_language_change(self):
        new_lang = self.lang_var.get()
        if new_lang != self.lang:
            self.lang = new_lang
            self.switch_language()

    def choose_folder(self):
        folder = filedialog.askdirectory(initialdir=self.last_dir if self.last_dir else os.path.expanduser("~"))
        if folder:
            self.last_dir = folder
            self.folder_label.config(text=folder)

    def generate_qr_image(self):
        link = self.link_var.get().strip()
        if not link:
            return None

        size = self.size_var.get()
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(link)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

        try:
            resample_filter = Image.Resampling.LANCZOS
        except AttributeError:
            resample_filter = Image.ANTIALIAS
        img = img.resize((size, size), resample_filter)
        return img

    def update_qr(self):
        img = self.generate_qr_image()
        self.canvas.delete("all")
        if img is None:
            self.canvas.create_text(
                self.canvas.winfo_width() // 2,
                self.canvas.winfo_height() // 2,
                text=self.get_text("enter_link"),
                font=("Segoe UI", 16),
                fill=COLORS["text"]
            )
            return

        self.tk_image = ImageTk.PhotoImage(img)
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x = (canvas_width - img.width) // 2 if canvas_width > img.width else 0
        y = (canvas_height - img.height) // 2 if canvas_height > img.height else 0
        self.canvas.create_image(x, y, anchor=tk.NW, image=self.tk_image)

    def save_qr(self):
        if self.format_var.get() == "none":
            messagebox.showinfo(
                self.get_text("info_none"),
                self.get_text("info_none_msg")
            )
            return

        img = self.generate_qr_image()
        if img is None:
            messagebox.showwarning(
                self.get_text("warning_no_link"),
                self.get_text("warning_no_link_msg")
            )
            return

        save_dir = self.last_dir
        if not save_dir:
            save_dir = filedialog.askdirectory(initialdir=os.path.expanduser("~"))
            if not save_dir:
                return
            self.last_dir = save_dir
            self.folder_label.config(text=save_dir)

        ext = self.format_var.get()
        filename = f"qrcode.{ext}"
        filepath = os.path.join(save_dir, filename)

        try:
            if ext == "png":
                img.save(filepath, "PNG")
            else:
                img.save(filepath, "JPEG")
            messagebox.showinfo(
                self.get_text("success"),
                self.get_text("success_msg").format(filepath)
            )
        except Exception as e:
            messagebox.showerror(
                self.get_text("error"),
                self.get_text("error_msg").format(e)
            )

    def on_closing(self):
        self.master.destroy()


if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = QRCodeGenerator(root)
        root.mainloop()
    except Exception:
        with open("error_log.txt", "w", encoding="utf-8") as f:
            traceback.print_exc(file=f)
        try:
            messagebox.showerror("Ошибка", "Не удалось запустить программу. Подробности в error_log.txt")
        except:
            pass
