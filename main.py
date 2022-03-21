from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

from select_components import SelectWindow
from preview import PreviewWindow
from convert import Convert


class MainWindow(Tk):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.data = dict()
        self.selected_items = dict()

        self.title("Faroad PnP Convert Tool - Version 0.4.0")
        # self.iconbitmap("icon.ico")
        self.geometry("640x200")
        self.resizable(False, False)

        browsers_frame = Frame(self)
        self.source = self.make_file_chooser(browsers_frame, "Source: ", self.select_file, 0)
        self.dest = self.make_file_chooser(browsers_frame, "Save dir: ", self.select_save_dir, 1)
        browsers_frame.grid(column=0, row=0)

        options_frame = Frame(self)

        Label(options_frame, text="Units: ").grid(column=0, row=0)
        self.units = ttk.Combobox(options_frame, state="readonly", takefocus=0, width=10, values=["mm", "inch", "mil"])
        self.units.set("mm")
        self.units.grid(column=1, row=0, sticky=N+S+E+W, padx=10, pady=10)

        Label(options_frame, text="Rot: ").grid(column=2, row=0)
        self.rot = ttk.Combobox(options_frame, state="readonly", takefocus=0, width=10,
                                values=["0", "90", "180", "270"])
        self.rot.set("0")
        self.rot.grid(column=3, row=0, sticky=N+S+E+W, padx=10, pady=10)

        Label(options_frame, text="X offset: ").grid(column=4, row=0)
        self.x_offset = DoubleVar(value=0.0)
        self.x_offset_spinbox = ttk.Spinbox(options_frame, width=10, from_=-1000, to=1000, increment=0.1,
                                            textvariable=self.x_offset)
        self.x_offset_spinbox.grid(column=5, row=0, sticky=N+S+E+W, padx=10, pady=10)

        Label(options_frame, text="Y offset: ").grid(column=6, row=0)
        self.y_offset = DoubleVar(value=0.0)
        self.y_offset_spinbox = ttk.Spinbox(options_frame, width=10, from_=-1000, to=1000, increment=0.1,
                                            textvariable=self.y_offset)
        self.y_offset_spinbox.grid(column=7, row=0, sticky=N+S+E+W, padx=10, pady=10)

        options_frame.grid(column=0, row=1)

        ttk.Separator(self, orient="horizontal") \
            .grid(column=0, row=2, sticky=N+S+E+W, padx=10, pady=10)

        buttons_frame = Frame()
        self.select_button = ttk.Button(buttons_frame, text="Select components", command=lambda: SelectWindow(self),
                                        state=DISABLED, takefocus=0, width=50)
        self.select_button.grid(column=0, row=0, sticky=E+W, padx=3)

        self.preview_button = ttk.Button(buttons_frame, text="Preview", command=lambda: PreviewWindow(self),
                                         state=DISABLED, takefocus=0, width=50)
        self.preview_button.grid(column=1, row=0, sticky=E+W, padx=3)

        self.gen_button = ttk.Button(buttons_frame, text="Generate", command=self.generate,
                                     state=DISABLED, takefocus=0)
        self.gen_button.grid(column=0, row=1, columnspan=2, sticky=E+W, pady=3, padx=5)

        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)
        buttons_frame.grid(column=0, row=3, sticky=E+W, padx=100)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        self.mainloop()

    @staticmethod
    def make_file_chooser(frame: Frame, text: str, command, row: int) -> StringVar:
        """Create file chooser with label, entry and browse button"""

        Label(frame, text=text).grid(column=0, row=row, sticky=N+S+W+E, pady=5)

        filepath = StringVar()
        ttk.Entry(frame, textvariable=filepath, width=75) \
            .grid(column=1, row=row, sticky=N+S+W+E, pady=5)

        ttk.Button(frame, text="Browse", command=command, takefocus=0) \
            .grid(column=2, row=row, sticky=N+S+W+E, pady=5, padx=5)

        return filepath

    def select_file(self) -> None:
        """Display file dialog and enable buttons"""

        filepath = filedialog.askopenfilename(title="Source", filetypes=[("All files", ".*")])

        if len(filepath) > 0:
            self.source.set(filepath)
            self.enable_buttons()

    def select_save_dir(self) -> None:
        """Display file dialog and enable buttons"""

        filepath = filedialog.askdirectory(title="Save directory")

        if len(filepath) > 0:
            self.dest.set(filepath)
            self.enable_buttons()

    def enable_buttons(self) -> None:
        """Enable Select components and Preview buttons"""

        if len(self.source.get()) > 0 and len(self.dest.get()) > 0:
            self.select_button.config(state=NORMAL)
            self.preview_button.config(state=NORMAL)

    def generate(self) -> None:
        """Create FAROAD_PP.txt file"""

        positions = [d["position"] for d in self.data]

        # Change units
        if self.units.get() == "inch":
            positions = [[x * 25.4, y * 25.4] for x, y in positions]
        elif self.units.get() == "mil":
            positions = [[x / 39.37, y / 39.37] for x, y in positions]

        # Rotate
        x_dim, y_dim = Convert.panel_dimensions(positions)
        positions = Convert.rotate((x_dim / 2, y_dim / 2), positions, int(self.rot.get()))

        lines = ["X Y R Desc ChipName\n"]
        for key, item in self.selected_items.items():
            if item is not None:
                line = f"{self.x_offset.get() - (positions[key][0]):.3f} " \
                       f"{(positions[key][1] + self.y_offset.get()):.3f} " \
                       f"{self.data[key]['rotation']:.3f} {self.data[key]['desc']} {item}\n"
                lines.append(line)

        with open(self.dest.get() + "/FAROAD_PP.txt", "w") as file:
            file.writelines(lines)

        messagebox.showinfo("Success", "Pick and place file successfully generated.")


if __name__ == "__main__":
    MainWindow()
