from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from convert import Convert, DATABASE_PATH

import sqlite3


class SelectWindow(Toplevel):

    # TODO Save selection for same current_line

    def __init__(self, parent):
        super(SelectWindow, self).__init__()

        self.current_item = 0
        self.selected_items = dict()

        self.parent = parent
        self.transient(self.parent)

        width = 650
        height = 405

        optionheight = (self.winfo_screenheight() // 2) - (height // 2)
        optionwidth = (self.winfo_screenwidth() // 2) - (width // 2)

        self.geometry(f"{width}x{height}+{optionwidth}+{optionheight}")
        # self.resizable(False, False)
        self.minsize(width, height)

        self.title("Generate")
        # self.iconbitmap("icon.ico")

        self.convert = Convert(self.parent.source.get())
        self.data = self.convert.parse()

        self.designators = [dat["designator"] for dat in self.data]
        self.items = self.convert.search(self.designators[self.current_item])

        line_frame = Frame(self)
        self.current_line_label = Label(line_frame, text=f"Line {self.current_item + 1}/{len(self.designators)}")
        self.current_line_label.grid(column=0, row=0, padx=10)

        self.current_line_text = StringVar(value=self.designators[self.current_item])
        self.current_line = ttk.Entry(line_frame, state=NORMAL, textvariable=self.current_line_text,
                                      justify="center", width=30)
        self.current_line.grid(column=1, row=0, sticky=E+W, padx=10)
        line_frame.columnconfigure(1, weight=1)
        line_frame.grid(column=0, row=0, pady=5, sticky=E+W)

        self.tree_view = ttk.Treeview(self, selectmode=BROWSE)

        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree_view.yview)
        vsb.grid(column=1, row=1, sticky=N+S)

        self.tree_view.configure(yscrollcommand=vsb.set)

        self.tree_view["columns"] = ("chip_group", "feeder")

        self.tree_view.column("chip_group", width=120, minwidth=120, stretch=NO)
        self.tree_view.column("feeder", width=100, minwidth=100, stretch=NO)

        self.tree_view.heading("#0", text="Name", anchor=W)
        self.tree_view.heading("chip_group", text="Chip group", anchor=W)
        self.tree_view.heading("feeder", text="Feeder", anchor=W)

        self.tree_view.grid(column=0, row=1, columnspan=2, sticky=N+S+E+W, padx=10)
        self.update_treeview(self.items)

        buttons_frame = Frame(self)
        self.add_button = ttk.Button(buttons_frame, text="Add", command=self.add_manually, takefocus=0)
        self.add_button.grid(column=0, row=0, padx=3, pady=3, sticky=E+W)

        self.show_button = ttk.Button(buttons_frame, text="Show all", command=self.show_all, takefocus=0)
        self.show_button.grid(column=1, row=0, padx=3, pady=3, sticky=E + W)

        self.skip_value = IntVar(value=0)
        self.skip_button = ttk.Checkbutton(buttons_frame, text="Skip",
                                           command=self.skip, takefocus=0, variable=self.skip_value)
        self.skip_button.grid(column=2, row=0, padx=3, pady=3, sticky=E+W)

        self.previous_button = ttk.Button(buttons_frame, text="Previous",
                                          command=lambda: self.select_item(False), takefocus=0)
        self.previous_button.grid(column=0, row=1, padx=3)

        self.next_button = ttk.Button(buttons_frame, text="Next", command=self.select_item, takefocus=0)
        self.next_button.grid(column=1, row=1, padx=3)

        self.done_button = ttk.Button(buttons_frame, text="Done", command=self.done, state=DISABLED, takefocus=0)
        self.done_button.grid(column=2, row=1, padx=3)
        buttons_frame.grid(column=0, row=2, columnspan=3, pady=5)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Shorcuts
        self.bind("<F7>", lambda e: self.select_item(False))
        self.bind("<F8>", lambda e: self.select_item(True))
        self.bind("<Left>", lambda e: self.select_item(False))
        self.bind("<Right>", lambda e: self.select_item(True))

        self.focus_set()
        self.grab_set()

    def select_item(self, next_=True) -> None:
        """Display item from list and save selected item"""

        selected = self.tree_view.item(self.tree_view.focus())["text"]

        # Save selected item
        if len(selected) > 0 and not self.skip_value.get():
            self.selected_items[self.current_item] = selected

            # Enable done button if all items have been selected
            if len(self.selected_items) == len(self.designators):
                self.done_button.config(state=NORMAL)

        if next_:
            self.current_item += 1
            if self.current_item >= len(self.designators):
                self.current_item = 0
        else:
            self.current_item -= 1
            if self.current_item < 0:
                self.current_item = len(self.designators) - 1

        self.current_line_label.config(text=f"Line {self.current_item + 1}/{len(self.designators)}")
        self.current_line_text.set(f"{self.data[self.current_item]['desc']} {self.designators[self.current_item]}")

        self.items = self.convert.search(self.designators[self.current_item])
        self.update_treeview(self.items)

        if self.current_item in self.selected_items and self.selected_items[self.current_item] is None:
            self.skip_value.set(1)
        else:
            self.skip_value.set(0)

    def show_all(self) -> None:
        """Show all items in the treeview"""
        self.items = self.convert.search("")
        self.update_treeview(self.items)

    def update_treeview(self, items: list) -> None:
        """Update treeview with matching item"""

        # Clear all items
        self.tree_view.config(selectmode=BROWSE)
        self.tree_view.delete(*self.tree_view.get_children())

        items.sort(key=lambda x: int(x[2][:6]))  # Sort by Excalibur number

        for i in items:
            self.tree_view.insert("", "end", text=i[2], iid=i[2], values=(i[1], i[6].split("|")[3]))

        # Highlight line if selected
        if self.current_item in self.selected_items:
            if self.selected_items[self.current_item] is not None:
                try:
                    self.tree_view.selection_set(self.selected_items[self.current_item])
                except TclError:
                    self.show_all()
                    self.tree_view.selection_set(self.selected_items[self.current_item])
            else:
                self.tree_view.config(selectmode=NONE)

    def skip(self) -> None:
        """Add to selected item None and disable selection"""

        if self.skip_value.get():
            self.selected_items[self.current_item] = None
            self.tree_view.selection_remove(*self.tree_view.get_children())
            self.tree_view.config(selectmode=NONE)
        else:
            del self.selected_items[self.current_item]
            self.tree_view.config(selectmode=BROWSE)

        # Enable done button if all items have been selected
        if len(self.selected_items) == len(self.designators):
            self.done_button.config(state=NORMAL)
        else:
            self.done_button.config(state=DISABLED)

    def add_manually(self) -> None:
        """Add an item to the database"""

        selected = self.tree_view.item(self.tree_view.focus())["text"]
        if len(selected) > 0:
            name = self.current_line_text.get()
            if not name[:6].isdecimal():
                messagebox.showwarning("Warning", "Missing Excalibur number.\n"
                                                  "You can rename item in the above entry.", parent=self)
            else:
                item_data = None
                for item in self.items:
                    if item[2] == selected:
                        item = list(item)  # Convert tuple to list
                        item[2] = name  # Replace name
                        item_data = item
                        break

                conn = sqlite3.connect(DATABASE_PATH)
                cur = conn.cursor()
                cur.execute(f"INSERT INTO chip_lib VALUES {tuple(item_data)};")

                conn.commit()
                conn.close()

                messagebox.showinfo("Success", "Item successfully added.")
                self.items = self.convert.search(self.designators[self.current_item])
                self.update_treeview(self.items)
        else:
            messagebox.showwarning("Warning", "First select an item.\n"
                                              "Data from the selected item will be copied to the new item.",
                                   parent=self)

    def done(self) -> None:
        """Send back to main window data"""

        # Save data to parent
        self.parent.data = self.data
        self.parent.selected_items = self.selected_items
        # Enable generate button
        self.parent.gen_button.config(state=NORMAL)

        self.destroy()
