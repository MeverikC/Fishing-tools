import tkinter as tk
from tkinter import filedialog, messagebox


class TextPaginator:
    def __init__(self, root):
        self.root = root
        self.root.title("文本分页阅读器")

        # 设置初始变量
        self.pages = []
        self.current_page = 0
        self.page_size = 30  # 默认每页字符数
        self.border_hidden = False

        # 快捷键配置
        self.shortcuts = {
            "minimize_window": "<Escape>",
            "prev_page": "<Up>",
            "next_page": "<Down>",
            "toggle_border": "<Control-Alt-;>",  # 新增快捷键
        }

        # 创建界面
        self.create_widgets()

        # 用于拖动的变量
        self.drag_start_x = 0
        self.drag_start_y = 0

        # 绑定鼠标事件
        self.text_display.bind("<Button-1>", self.on_drag_start)
        self.text_display.bind("<B1-Motion>", self.on_drag)

    def create_widgets(self):
        # 文本显示框
        self.text_display = tk.Text(self.root, wrap="none", font=("Arial", 10), height=1, state=tk.DISABLED)
        self.text_display.pack(expand=True, fill="both", padx=10, pady=5)

        # 菜单
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        file_menu = tk.Menu(self.menubar, tearoff=0)
        file_menu.add_command(label="打开文件", command=self.open_file)
        file_menu.add_command(label="上一页", command=self.prev_page)
        file_menu.add_command(label="下一页", command=self.next_page)
        file_menu.add_command(label="设置每页字符数", command=self.set_page_size)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.quit_program)
        self.menubar.add_cascade(label="文件", menu=file_menu)

        options_menu = tk.Menu(self.menubar, tearoff=0)
        options_menu.add_command(label="最小化窗口", command=self.minimize_window)
        options_menu.add_command(label="隐藏/显示边框", command=self.toggle_border)
        self.menubar.add_cascade(label="选项", menu=options_menu)

        shortcuts_menu = tk.Menu(self.menubar, tearoff=0)
        shortcuts_menu.add_command(label="自定义快捷键", command=self.custom_shortcuts)
        self.menubar.add_cascade(label="快捷键", menu=shortcuts_menu)

    def bind_shortcuts(self):
        for action, key in self.shortcuts.items():
            self.root.bind(key, self.create_callback(action))

    def create_callback(self, action):
        """创建一个快捷键回调函数"""

        def callback(event):
            method = getattr(self, action, None)
            if method:
                method(event)

        return callback

    def open_file(self):
        # 打开文件对话框
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read().replace('\n', ' ')  # 用空格替代换行
        except Exception as e:
            messagebox.showerror("错误", f"无法读取文件：{e}")
            return

        self.paginate_text(content)
        self.display_page(0)

    def paginate_text(self, text):
        # 分页
        self.pages = [text[i:i + self.page_size] for i in range(0, len(text), self.page_size)]
        self.current_page = 0
        self.display_page(0)

    def display_page(self, page_index):
        if not self.pages:
            return

        self.current_page = page_index
        content = self.pages[self.current_page]
        page_info = f"Page {self.current_page + 1}/{len(self.pages)}"

        self.text_display.config(state=tk.NORMAL)
        self.text_display.delete(1.0, tk.END)
        self.text_display.insert(tk.END, f"{content}\n{page_info}")
        self.text_display.config(state=tk.DISABLED)

    def prev_page(self, event=None):
        if self.current_page > 0:
            self.display_page(self.current_page - 1)

    def next_page(self, event=None):
        if self.current_page < len(self.pages) - 1:
            self.display_page(self.current_page + 1)

    def minimize_window(self, event=None):
        self.root.iconify()

    def toggle_border(self, event=None):
        """切换窗口边框的显示状态，并设置窗口置顶"""
        if self.root.overrideredirect():
            # 显示边框和菜单
            self.root.overrideredirect(False)
            self.root.config(menu=self.menubar)  # 重新设置菜单
            self.root.wm_attributes("-topmost", False)  # 取消置顶
        else:
            # 隐藏边框和菜单，设置置顶
            self.root.overrideredirect(True)
            self.root.config(menu="")  # 移除菜单
            self.root.wm_attributes("-topmost", True)  # 设置窗口置顶

    def set_page_size(self):
        # 设置每页字符数
        def save_page_size():
            try:
                new_size = int(entry.get())
                if new_size <= 0:
                    raise ValueError
                self.page_size = new_size
                messagebox.showinfo("成功", f"每页字符数已设置为 {new_size}")
                size_window.destroy()
            except ValueError:
                messagebox.showerror("错误", "请输入有效的正整数！")

        size_window = tk.Toplevel(self.root)
        size_window.title("设置每页字符数")
        size_window.geometry("300x100")

        tk.Label(size_window, text="每页字符数:").pack(pady=10)
        entry = tk.Entry(size_window)
        entry.pack(pady=5)

        tk.Button(size_window, text="保存", command=save_page_size).pack(pady=5)

    def custom_shortcuts(self):
        # 用户自定义快捷键的对话框
        top = tk.Toplevel(self.root)
        top.title("自定义快捷键")

        # 这里只是一个示例，实际实现可能需要更复杂的逻辑
        tk.Label(top, text="当前快捷键配置为默认配置").pack()

    def quit_program(self):
        """优雅退出程序"""
        if messagebox.askokcancel("退出", "确定要退出程序吗？"):
            self.root.destroy()

    def on_drag_start(self, event):
        # 记录鼠标起始位置
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def on_drag(self, event):
        # 计算鼠标移动的距离，并更新窗口位置
        x = self.root.winfo_x() - self.drag_start_x + event.x
        y = self.root.winfo_y() - self.drag_start_y + event.y
        self.root.geometry(f"+{x}+{y}")


def main():
    root = tk.Tk()
    root.geometry("300x100")  # 设置窗口大小
    app = TextPaginator(root)
    app.bind_shortcuts()  # 确保快捷键被绑定
    root.protocol("WM_DELETE_WINDOW", app.quit_program)  # 覆盖关闭窗口动作
    root.mainloop()


if __name__ == "__main__":
    main()
