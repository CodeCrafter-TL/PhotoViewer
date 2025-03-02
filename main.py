import tkinter as tk
import tkinter.messagebox as msgbox
import tkinter.filedialog as dialog
import tkinter.simpledialog as sdialog
import platform
from PIL import Image, ImageTk


class AboutThis(tk.Toplevel):

    def __init__(self, master: tk.Tk, version: str):
        super().__init__(master=master)

        self.wm_title("关于 Photo Viewer")
        self.wm_geometry("285x190")
        self.wm_resizable(False, False)

        self.x = int(self.winfo_screenwidth() / 2 - 142.5)
        self.y = int(self.winfo_screenheight() / 2 - 240)
        self.wm_geometry(f"+{self.x}+{self.y}")

        self.logo = Image.open("./logo.png")
        self.logotk = ImageTk.PhotoImage(self.logo, (72, 72))
        tk.Label(self, image=self.logotk).pack(side="top", pady=(18, 0))
        tk.Label(self, text="Photo Viewer", font=(
            "TkDefaultFont", 12, "bold")).pack(side="top")
        tk.Label(self, text=f"版本 {version}", font=(
            "TkDefaultFont", 10)).pack(side="top", pady=(18, 0))
        tk.Label(self, text=f"Copyright © 2023 - 2025 CodeCrafter Studio",
                 font=("TkDefaultFont", 10)).pack(side="top")

        self.mainloop()


class Viewer(tk.Tk):

    version = "1.0"

    def __init__(self):
        super().__init__()

        self.wm_geometry("500x500")
        self.wm_title("Photo Viewer")
        self.focus_force()

        self.canvas = tk.Canvas(self, highlightthickness=0, bg="gray")
        self.canvas.pack(fill=tk.BOTH, expand=1)
        self.canvas.configure(cursor="hand2")

        self.img = None
        self.imgtk = None
        self.hotkeys = []
        self.drag_data = []
        self.handlers = [
            self.open_file,
            self.quit,
            self.zoom_photo,
            self.rotate_photo,
            self.about_this
        ]

        self.__bind_drag()
        self.__get_hotkeys()
        self.__menu_init()

        self.mainloop()

    def __get_hotkeys(self):
        if platform.system() != "Darwin":
            self.hotkeys = ["Control-O", "Control-Q",
                            "Control-Z", "Control-R", "Control-A"]
        else:
            self.hotkeys = ["Command-O", "Command-Q",
                            "Command-Z", "Command-R", "Command-A"]

        for hotkey in self.hotkeys:
            self.canvas.bind_all(
                f"<{hotkey}>", self.handlers[self.hotkeys.index(hotkey)])

    def __menu_init(self):
        menu = tk.Menu(self)
        self.configure(menu=menu)

        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(
            label="打开图片...", command=self.open_file, accelerator=self.hotkeys[0])
        file_menu.add_command(label="退出 PhotoViewer...",
                              command=self.quit, accelerator=self.hotkeys[1])
        menu.add_cascade(label="文件", menu=file_menu)

        edit_menu = tk.Menu(menu, tearoff=0)
        edit_menu.add_command(
            label="缩放图片...", command=self.zoom_photo, accelerator=self.hotkeys[2])
        edit_menu.add_command(
            label="旋转图片...", command=self.rotate_photo, accelerator=self.hotkeys[3])
        edit_menu.add_command(
            label="水平翻转图片...", command=self.leftright_transpose)
        edit_menu.add_command(
            label="垂直翻转图片...", command=self.topbottom_transpose)
        menu.add_cascade(label="编辑", menu=edit_menu)

        help_menu = tk.Menu(menu, tearoff=0)
        help_menu.add_command(
            label="关于 PhotoViewer...", command=self.about_this, accelerator=self.hotkeys[4])
        menu.add_cascade(label="帮助", menu=help_menu)

    def __bind_drag(self):
        self.canvas.bind("<Button-1>", self.__start_drag)
        self.canvas.bind("<B1-Motion>", self.__on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.__end_drag)
        self.drag_data = {"x": 0, "y": 0, "item": None}

    def __start_drag(self, event: tk.Event):
        self.drag_data["item"] = self.canvas.find_withtag("photo")
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def __on_drag(self, event: tk.Event):
        if self.drag_data["item"]:
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]
            self.canvas.move(self.drag_data["item"], dx, dy)
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

    def __end_drag(self, _event: tk.Event):
        self.drag_data["item"] = None

    def open_file(self, _event: tk.Event = None):
        result = dialog.askopenfilename(title="打开图片文件", parent=self)
        if result:
            self.init_photo(result)

    def zoom_photo(self, _event: tk.Event = None):
        result = sdialog.askfloat(
            "缩放比例", "输入缩放比例来缩放: ", initialvalue=2.0, minvalue=0.1, parent=self)
        if result and self.img:
            width, height = self.img.size
            new_width = int(width * result)
            new_height = int(height * result)

            try:
                img_resized = self.img.resize(
                    (new_width, new_height), Image.Resampling.LANCZOS)
                self.img = img_resized
                self.imgtk = ImageTk.PhotoImage(self.img)
                self.canvas.itemconfigure("photo", image=self.imgtk)
                self.canvas.configure(scrollregion=self.canvas.bbox("photo"))
            except Exception as e:
                msgbox.showerror("错误", f"缩放图片时发生错误: {str(e)}")

    def rotate_photo(self, _event: tk.Event = None):
        result = sdialog.askinteger(
            "旋转度数", "输入旋转度数来旋转: ", initialvalue=90, minvalue=0, parent=self)
        if result and self.img:
            try:
                img_rotated = self.img.rotate(result, Image.Resampling.LANCZOS)
                self.img = img_rotated
                self.imgtk = ImageTk.PhotoImage(self.img)
                self.canvas.itemconfigure("photo", image=self.imgtk)
                self.canvas.configure(scrollregion=self.canvas.bbox("photo"))
            except Exception as e:
                msgbox.showerror("错误", f"旋转图片时发生错误: {str(e)}")

    def leftright_transpose(self, _event: tk.Event = None):
        if self.img:
            try:
                img_transposed = self.img.transpose(
                    Image.Transpose.FLIP_LEFT_RIGHT)
                self.img = img_transposed
                self.imgtk = ImageTk.PhotoImage(self.img)
                self.canvas.itemconfigure("photo", image=self.imgtk)
                self.canvas.configure(scrollregion=self.canvas.bbox("photo"))
            except Exception as e:
                msgbox.showerror("错误", f"翻转图片时发生错误: {str(e)}")

    def topbottom_transpose(self, _event: tk.Event = None):
        if self.img:
            try:
                img_transposed = self.img.transpose(
                    Image.Transpose.FLIP_TOP_BOTTOM)
                self.img = img_transposed
                self.imgtk = ImageTk.PhotoImage(self.img)
                self.canvas.itemconfigure("photo", image=self.imgtk)
                self.canvas.configure(scrollregion=self.canvas.bbox("photo"))
            except Exception as e:
                msgbox.showerror("错误", f"翻转图片时发生错误: {str(e)}")

    def about_this(self, _event: tk.Event = None) -> AboutThis:
        return AboutThis(self, self.version)

    def init_photo(self, file: str):
        if self.canvas.find_withtag("photo"):
            self.canvas.delete("photo")
        try:
            self.img = Image.open(file)
            self.img.thumbnail((self.winfo_width(), self.winfo_height()))
            if self.img.width > self.winfo_width() and self.img.height > self.winfo_height():
                self.img = self.img.resize((self.winfo_width(), int(
                    self.winfo_height() * self.img.height / self.img.width)))
            self.imgtk = ImageTk.PhotoImage(self.img)
            self.canvas.img = self.imgtk
            self.canvas.create_image(250, 250, image=self.imgtk, tag="photo")
        except FileNotFoundError:
            msgbox.showerror("错误", "无法找到此文件")
        except Exception as e:
            msgbox.showerror("错误", f"加载图片时发生错误: {str(e)}")


if __name__ == "__main__":
    viewer = Viewer()
    viewer.about_this()
