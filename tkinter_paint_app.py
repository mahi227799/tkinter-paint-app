import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox


class PaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Paint")
        self.root.geometry("1000x650")
        self.root.minsize(800, 550)
        self.root.configure(bg="#e8edf4")

        # ---------------- Application variables ----------------
        self.canvas_background = "white"
        self.current_color = "#111827"
        self.current_tool = "pencil"

        self.start_x = 0
        self.start_y = 0
        self.last_x = 0
        self.last_y = 0

        self.preview_item = None
        self.current_action = []
        self.history = []
        self.dragged = False

        self.width_var = tk.IntVar(value=5)
        self.fill_shapes_var = tk.BooleanVar(value=False)

        self.tool_buttons = {}

        self.create_header()
        self.create_main_area()
        self.create_status_bar()
        self.create_shortcuts()

        self.set_tool("pencil")
        self.update_size_preview()

    # ==========================================================
    # Interface
    # ==========================================================

    def create_header(self):
        header = tk.Frame(
            self.root,
            bg="#111827",
            height=65
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        title = tk.Label(
            header,
            text="Modern Paint",
            bg="#111827",
            fg="white",
            font=("Segoe UI", 20, "bold")
        )
        title.pack(side="left", padx=22)

        subtitle = tk.Label(
            header,
            text="Draw, design and create",
            bg="#111827",
            fg="#9ca3af",
            font=("Segoe UI", 10)
        )
        subtitle.pack(side="left", pady=(8, 0))

        export_button = self.create_action_button(
            header,
            "Export",
            self.export_canvas,
            "#2563eb"
        )
        export_button.pack(side="right", padx=(8, 20), pady=14)

        clear_button = self.create_action_button(
            header,
            "Clear",
            self.clear_canvas,
            "#dc2626"
        )
        clear_button.pack(side="right", padx=8, pady=14)

        undo_button = self.create_action_button(
            header,
            "Undo",
            self.undo,
            "#374151"
        )
        undo_button.pack(side="right", padx=8, pady=14)

    def create_main_area(self):
        main_frame = tk.Frame(self.root, bg="#e8edf4")
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        self.create_sidebar(main_frame)
        self.create_canvas(main_frame)

    def create_sidebar(self, parent):
        sidebar = tk.Frame(
            parent,
            bg="#f8fafc",
            width=185,
            highlightbackground="#d1d5db",
            highlightthickness=1
        )
        sidebar.pack(side="left", fill="y", padx=(0, 15))
        sidebar.pack_propagate(False)

        tools_label = tk.Label(
            sidebar,
            text="DRAWING TOOLS",
            bg="#f8fafc",
            fg="#6b7280",
            font=("Segoe UI", 9, "bold")
        )
        tools_label.pack(anchor="w", padx=15, pady=(18, 8))

        self.create_tool_button(sidebar, "Pencil", "pencil")
        self.create_tool_button(sidebar, "Rectangle", "rectangle")
        self.create_tool_button(sidebar, "Oval", "oval")
        self.create_tool_button(sidebar, "Eraser", "eraser")

        separator1 = tk.Frame(sidebar, bg="#d1d5db", height=1)
        separator1.pack(fill="x", padx=15, pady=15)

        size_label = tk.Label(
            sidebar,
            text="BRUSH SIZE",
            bg="#f8fafc",
            fg="#6b7280",
            font=("Segoe UI", 9, "bold")
        )
        size_label.pack(anchor="w", padx=15)

        self.size_preview = tk.Canvas(
            sidebar,
            width=55,
            height=45,
            bg="#f8fafc",
            highlightthickness=0
        )
        self.size_preview.pack(pady=(5, 0))

        size_slider = tk.Scale(
            sidebar,
            from_=1,
            to=30,
            orient="horizontal",
            variable=self.width_var,
            command=self.update_size_preview,
            bg="#f8fafc",
            fg="#111827",
            activebackground="#2563eb",
            highlightthickness=0,
            troughcolor="#dbeafe",
            font=("Segoe UI", 9)
        )
        size_slider.pack(fill="x", padx=12)

        fill_checkbox = tk.Checkbutton(
            sidebar,
            text="Fill shapes",
            variable=self.fill_shapes_var,
            bg="#f8fafc",
            activebackground="#f8fafc",
            fg="#374151",
            selectcolor="white",
            font=("Segoe UI", 10)
        )
        fill_checkbox.pack(anchor="w", padx=12, pady=(4, 0))

        separator2 = tk.Frame(sidebar, bg="#d1d5db", height=1)
        separator2.pack(fill="x", padx=15, pady=15)

        color_header = tk.Frame(sidebar, bg="#f8fafc")
        color_header.pack(fill="x", padx=15)

        color_label = tk.Label(
            color_header,
            text="COLORS",
            bg="#f8fafc",
            fg="#6b7280",
            font=("Segoe UI", 9, "bold")
        )
        color_label.pack(side="left")

        self.color_preview = tk.Label(
            color_header,
            width=3,
            height=1,
            bg=self.current_color,
            relief="solid",
            bd=1
        )
        self.color_preview.pack(side="right")

        self.create_color_palette(sidebar)

        custom_color_button = tk.Button(
            sidebar,
            text="Choose Custom Color",
            command=self.choose_custom_color,
            bg="#e5e7eb",
            fg="#111827",
            activebackground="#d1d5db",
            relief="flat",
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
            padx=8,
            pady=7
        )
        custom_color_button.pack(fill="x", padx=15, pady=(10, 0))

    def create_canvas(self, parent):
        canvas_container = tk.Frame(
            parent,
            bg="#cbd5e1",
            padx=3,
            pady=3
        )
        canvas_container.pack(side="right", fill="both", expand=True)

        self.canvas = tk.Canvas(
            canvas_container,
            bg=self.canvas_background,
            cursor="crosshair",
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<ButtonPress-1>", self.start_drawing)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)
        self.canvas.bind("<Motion>", self.update_coordinates)

    def create_status_bar(self):
        self.status_label = tk.Label(
            self.root,
            text="Tool: Pencil  |  Color: #111827  |  Size: 5",
            bg="#111827",
            fg="#d1d5db",
            anchor="w",
            padx=15,
            font=("Consolas", 9)
        )
        self.status_label.pack(fill="x", side="bottom")

    def create_shortcuts(self):
        self.root.bind("<Control-z>", lambda event: self.undo())
        self.root.bind("<Control-Z>", lambda event: self.undo())
        self.root.bind("<Control-l>", lambda event: self.clear_canvas())
        self.root.bind("<Control-e>", lambda event: self.export_canvas())

    # ==========================================================
    # Buttons and colors
    # ==========================================================

    def create_action_button(self, parent, text, command, background):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=background,
            fg="white",
            activebackground=background,
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            padx=18,
            pady=8
        )

    def create_tool_button(self, parent, text, tool_name):
        button = tk.Button(
            parent,
            text=text,
            command=lambda: self.set_tool(tool_name),
            bg="#e5e7eb",
            fg="#111827",
            activebackground="#bfdbfe",
            activeforeground="#111827",
            relief="flat",
            anchor="w",
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            padx=15,
            pady=9
        )
        button.pack(fill="x", padx=12, pady=3)

        self.tool_buttons[tool_name] = button

    def create_color_palette(self, parent):
        colors = [
            "#111827", "#6b7280", "#ffffff",
            "#7c2d12", "#dc2626", "#f97316",
            "#facc15", "#16a34a", "#14b8a6",
            "#2563eb", "#7c3aed", "#db2777"
        ]

        palette_frame = tk.Frame(parent, bg="#f8fafc")
        palette_frame.pack(padx=15, pady=(10, 0))

        for index, color in enumerate(colors):
            button = tk.Button(
                palette_frame,
                bg=color,
                activebackground=color,
                width=3,
                height=1,
                relief="solid",
                bd=1,
                cursor="hand2",
                command=lambda selected_color=color:
                self.set_color(selected_color)
            )

            row = index // 3
            column = index % 3

            button.grid(
                row=row,
                column=column,
                padx=4,
                pady=4
            )

    def set_tool(self, tool_name):
        self.current_tool = tool_name

        for name, button in self.tool_buttons.items():
            if name == tool_name:
                button.configure(
                    bg="#2563eb",
                    fg="white",
                    activebackground="#1d4ed8",
                    activeforeground="white"
                )
            else:
                button.configure(
                    bg="#e5e7eb",
                    fg="#111827",
                    activebackground="#bfdbfe",
                    activeforeground="#111827"
                )

        self.update_status()

    def set_color(self, new_color):
        self.current_color = new_color
        self.color_preview.configure(bg=new_color)

        # Selecting a color exits eraser mode.
        if self.current_tool == "eraser":
            self.set_tool("pencil")

        self.update_size_preview()
        self.update_status()

    def choose_custom_color(self):
        selected_color = colorchooser.askcolor(
            color=self.current_color,
            title="Choose a drawing color"
        )[1]

        if selected_color:
            self.set_color(selected_color)

    # ==========================================================
    # Drawing operations
    # ==========================================================

    def start_drawing(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.last_x = event.x
        self.last_y = event.y

        self.current_action = []
        self.preview_item = None
        self.dragged = False

        draw_color = self.get_draw_color()
        brush_width = self.width_var.get()

        if self.current_tool == "rectangle":
            self.preview_item = self.canvas.create_rectangle(
                self.start_x,
                self.start_y,
                self.start_x,
                self.start_y,
                outline=draw_color,
                fill=self.get_shape_fill(),
                width=brush_width
            )

        elif self.current_tool == "oval":
            self.preview_item = self.canvas.create_oval(
                self.start_x,
                self.start_y,
                self.start_x,
                self.start_y,
                outline=draw_color,
                fill=self.get_shape_fill(),
                width=brush_width
            )

    def draw(self, event):
        self.dragged = True

        draw_color = self.get_draw_color()
        brush_width = self.width_var.get()

        if self.current_tool in ("pencil", "eraser"):
            line_id = self.canvas.create_line(
                self.last_x,
                self.last_y,
                event.x,
                event.y,
                fill=draw_color,
                width=brush_width,
                capstyle=tk.ROUND,
                joinstyle=tk.ROUND,
                smooth=True
            )

            self.current_action.append(line_id)

            self.last_x = event.x
            self.last_y = event.y

        elif self.current_tool in ("rectangle", "oval"):
            if self.preview_item is not None:
                self.canvas.coords(
                    self.preview_item,
                    self.start_x,
                    self.start_y,
                    event.x,
                    event.y
                )

    def stop_drawing(self, event):
        draw_color = self.get_draw_color()
        brush_width = self.width_var.get()

        if self.current_tool in ("pencil", "eraser"):
            # Draw a dot when the mouse is clicked without dragging.
            if not self.dragged:
                radius = max(1, brush_width / 2)

                dot_id = self.canvas.create_oval(
                    event.x - radius,
                    event.y - radius,
                    event.x + radius,
                    event.y + radius,
                    fill=draw_color,
                    outline=draw_color
                )

                self.current_action.append(dot_id)

            if self.current_action:
                self.history.append(self.current_action.copy())

        elif self.current_tool in ("rectangle", "oval"):
            if self.preview_item is not None:
                self.history.append([self.preview_item])

        self.current_action = []
        self.preview_item = None

    def get_draw_color(self):
        if self.current_tool == "eraser":
            return self.canvas_background

        return self.current_color

    def get_shape_fill(self):
        if self.fill_shapes_var.get():
            return self.current_color

        return ""

    # ==========================================================
    # Utility functions
    # ==========================================================

    def undo(self):
        if not self.history:
            self.status_label.configure(text="Nothing to undo")
            return

        last_action = self.history.pop()

        for item_id in last_action:
            self.canvas.delete(item_id)

        self.update_status()

    def clear_canvas(self):
        has_drawing = bool(self.canvas.find_all())

        if not has_drawing:
            return

        should_clear = messagebox.askyesno(
            "Clear Canvas",
            "Do you want to remove everything from the canvas?"
        )

        if should_clear:
            self.canvas.delete("all")
            self.history.clear()
            self.current_action.clear()
            self.preview_item = None
            self.update_status()

    def export_canvas(self):
        file_path = filedialog.asksaveasfilename(
            title="Export Drawing",
            defaultextension=".ps",
            filetypes=[
                ("PostScript file", "*.ps"),
                ("All files", "*.*")
            ]
        )

        if not file_path:
            return

        try:
            self.canvas.postscript(
                file=file_path,
                colormode="color"
            )

            messagebox.showinfo(
                "Export Complete",
                "Your drawing was exported successfully."
            )

        except Exception as error:
            messagebox.showerror(
                "Export Error",
                f"Could not export the drawing.\n\n{error}"
            )

    def update_size_preview(self, value=None):
        self.size_preview.delete("all")

        size = self.width_var.get()
        radius = max(2, min(size, 30) / 2)

        center_x = 27
        center_y = 22

        preview_color = self.get_draw_color()

        self.size_preview.create_oval(
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius,
            fill=preview_color,
            outline="#9ca3af"
        )

        self.update_status()

    def update_coordinates(self, event):
        self.update_status(event.x, event.y)

    def update_status(self, x=None, y=None):
        tool_name = self.current_tool.capitalize()
        brush_size = self.width_var.get()

        status = (
            f"Tool: {tool_name}  |  "
            f"Color: {self.current_color}  |  "
            f"Size: {brush_size}"
        )

        if x is not None and y is not None:
            status += f"  |  Position: ({x}, {y})"

        self.status_label.configure(text=status)


if __name__ == "__main__":
    root = tk.Tk()
    app = PaintApp(root)
    root.mainloop()