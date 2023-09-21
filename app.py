from customtkinter import *
from tkinter import filedialog as fd
from PIL import Image, ImageTk
import json
from api import *
from data import *
import datetime
from constants import *
import matplotlib.colors as mcolors


api = GymManager()
basedir = os.path.dirname(__file__)
set_default_color_theme(os.path.join(basedir, "custom.json"))

try:
    from ctypes import windll

    myappid = "ugg.gmapi.tool.1.0"
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass


class App(CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("800x800")
        self.title("Gym Manager Membership API Tool")
        self.minsize(width=800, height=650)
        self.resizable(width=False, height=True)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(12, weight=1)
        self.console_text = []

        # ---------------------------------- UI GRAPHIC HEADER ---------------------------------- #

        self.bg_img = ImageTk.PhotoImage(
            file=os.path.join(basedir, "assets/background.png")
        )
        self.canvas = CTkCanvas(self, width=800, height=100, highlightthickness=0)
        self.canvas.create_image(400, 50, image=self.bg_img)
        self.canvas.grid(column=2, row=0, sticky="e")

        # ---------------------------------- UI FRAMES ---------------------------------- #

        self.frame_auth = CTkFrame(self)
        self.frame_auth.grid(
            column=2, row=1, padx=(15, 15), pady=(15, 15), sticky="nsew"
        )
        self.frame_auth.grid_columnconfigure(2, weight=6)

        self.frame_file = CTkFrame(self)
        self.frame_file.grid(
            column=2, row=2, padx=(15, 15), pady=(0, 15), sticky="nsew"
        )
        self.frame_file.grid_columnconfigure(2, weight=6)

        self.frame_upload = CTkFrame(self)
        self.frame_upload.grid(
            column=2, row=3, padx=(15, 15), pady=(0, 15), sticky="nsew"
        )
        self.frame_upload.grid_columnconfigure(2, weight=6)

        # ---------------------------------- UI LOG IN ---------------------------------- #

        self.label_authenticate = CTkLabel(
            self.frame_auth, text="LOG IN", font=("Roboto", 12, "bold")
        )
        self.label_authenticate.grid(
            column=2,
            row=1,
            padx=UNIVERSAL_X_PADDING,
            pady=UNIVERSAL_PADDING,
            sticky="w",
        )

        self.entry_username = CTkEntry(self.frame_auth, placeholder_text="Username")
        self.entry_username.grid(
            column=2,
            row=2,
            padx=(UNIVERSAL_X_PADDING, 180),
            pady=UNIVERSAL_PADDING,
            sticky="ew",
        )

        with open(os.path.join(basedir, "user.json"), "r") as data_file:
            self.stored_user_name = json.load(data_file)["user"]

        if self.stored_user_name != "":
            self.entry_username.insert(0, self.stored_user_name)

        self.entry_password = CTkEntry(
            self.frame_auth, placeholder_text="Password", show="●"
        )
        self.entry_password.grid(
            column=2,
            row=3,
            padx=(UNIVERSAL_X_PADDING, 180),
            pady=UNIVERSAL_PADDING,
            sticky="ew",
        )

        self.checkbox_remember_me = CTkCheckBox(
            self.frame_auth, text="Remember username"
        )
        self.checkbox_remember_me.select()
        self.checkbox_remember_me.grid(
            column=2,
            row=2,
            padx=UNIVERSAL_X_PADDING,
            pady=UNIVERSAL_PADDING,
            sticky="e",
        )

        self.button_login = CTkButton(
            self.frame_auth, text="Log in", command=self.log_in, width=152
        )
        self.button_login.grid(
            column=2,
            row=3,
            padx=UNIVERSAL_X_PADDING,
            pady=(UNIVERSAL_PADDING + 10, UNIVERSAL_X_PADDING),
            sticky="e",
        )

        # ---------------------------------- UI SELECT FILE ---------------------------------- #

        self.label_file = CTkLabel(
            self.frame_file, text="SELECT FILE", font=("Roboto", 12, "bold")
        )
        self.label_file.grid(
            column=2,
            row=6,
            padx=UNIVERSAL_X_PADDING,
            pady=UNIVERSAL_PADDING,
            sticky="w",
        )

        self.button_locate_file = CTkButton(
            self.frame_file, text="Select File", command=self.select_file
        )
        self.button_locate_file.grid(
            column=2,
            row=7,
            padx=UNIVERSAL_X_PADDING,
            pady=(UNIVERSAL_PADDING, 15),
            sticky="w",
        )

        self.checkbox_validate = CTkCheckBox(self.frame_file, text="Validate input")
        self.checkbox_validate.select()
        self.checkbox_validate.grid(
            column=2,
            row=7,
            padx=(170, UNIVERSAL_PADDING),
            pady=(UNIVERSAL_PADDING, 15),
            sticky="w",
        )

        # ---------------------------------- UI UPLOAD ---------------------------------- #

        self.label_upload = CTkLabel(
            self.frame_upload, text="UPLOAD", font=("Roboto", 12, "bold")
        )
        self.label_upload.grid(
            column=2,
            row=8,
            padx=UNIVERSAL_X_PADDING,
            pady=UNIVERSAL_PADDING,
            sticky="w",
        )

        self.button_upload = CTkButton(
            self.frame_upload,
            text="Upload records",
            state="disabled",
            command=self.upload,
        )
        self.button_upload.grid(
            column=2,
            row=9,
            padx=UNIVERSAL_X_PADDING,
            pady=(UNIVERSAL_PADDING, 15),
            sticky="w",
        )

        self.progressbar = CTkProgressBar(self.frame_upload, mode="determinate")
        self.progressbar.grid(
            column=2,
            row=9,
            padx=(170, UNIVERSAL_X_PADDING),
            pady=(12, 20),
            sticky="ew",
        )
        self.progressbar.set(0)

        # ---------------------------------- UI CONSOLE ---------------------------------- #

        self.label_console = CTkLabel(self, text="CONSOLE", font=("Roboto", 12, "bold"))
        self.label_console.grid(
            column=2,
            row=11,
            padx=(30, 0),
            pady=(0, 0),
            sticky="w",
        )

        self.text_box = CTkTextbox(master=self, wrap="none")
        self.text_box.grid(
            column=2, row=12, padx=(15, 15), pady=UNIVERSAL_PADDING, sticky="nsew"
        )

        self.button_export_report = CTkButton(
            self, text="Save report", command=self.save_report, state="disabled"
        )
        self.button_export_report.grid(
            column=2,
            row=13,
            padx=(UNIVERSAL_X_PADDING, 170),
            pady=(5, 10),
            sticky="se",
        )

        self.button_clear_console = CTkButton(
            self, text="Clear console", command=self.clear_console
        )
        self.button_clear_console.grid(
            column=2,
            row=13,
            padx=UNIVERSAL_X_PADDING,
            pady=(5, 10),
            sticky="se",
        )

        self.label_copyright = CTkLabel(
            self,
            text="© Urban Gym Group | Developed by a.verhoeff@cmotions.nl",
            font=("Roboto", 10),
            text_color="gray",
        )
        self.label_copyright.grid(
            column=2,
            row=13,
            padx=(15, 0),
            pady=(0, 10),
            sticky="sw",
        )

    # ---------------------------------- FUNCTIONALITY ---------------------------------- #

    def log_in(self):
        user_name = self.entry_username.get()
        password = self.entry_password.get()

        if self.checkbox_remember_me.get() == 1 and user_name != "":
            new_data = {"user": user_name}

            with open(os.path.join(basedir, "user.json"), "w") as data_file:
                json.dump(obj=new_data, fp=data_file, indent=4)

        elif self.checkbox_remember_me.get() == 0:
            new_data = {"user": ""}

            with open(os.path.join(basedir, "user.json"), "w") as data_file:
                json.dump(obj=new_data, fp=data_file, indent=4)

        if user_name == "" or password == "":
            self.update_console(f"Failed to log in: Either username or password empty.")
        else:
            try:
                api.authenticate(user_name=user_name, password=password)
            except ConnectionFailed as error_message:
                self.update_console(f"Failed to log in: {error_message}")
            else:
                self.update_console(
                    f"Login succeeded: User {self.entry_username.get()} logged in."
                )
                self.update_console(f"Connection test: {api.connection_test()}")

    def update_console(self, input_string) -> None:
        self.console_text.append(
            f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {input_string}\n"
        )
        self.text_box.delete(0.0, END)
        self.text_box.insert(0.0, "".join(self.console_text))
        self.text_box.see(END)

    def clear_console(self) -> None:
        self.console_text.clear()
        self.text_box.delete(0.0, END)

    def save_report(self):
        try:
            file = fd.asksaveasfile(
                initialfile="report.csv",
                title="Save report",
                defaultextension=".csv",
                filetypes=((("csv files", "*.csv"), ("All files", "*.*"))),
            )
            file.write(api.report_export)
            file.close()
        except:
            self.update_console(
                "An error occured when saving the report. Please retry."
            )
        else:
            self.update_console("Report was successfully saved.")

    def select_file(self):
        filename = fd.askopenfilename(
            filetypes=((("csv files", "*.csv"), ("All files", "*.*")))
        )
        self.update_console(f"File selected: {filename}")

        if self.checkbox_validate.get() == 1:
            transform_data = TransformData(filepath=filename, validate=True)
        else:
            transform_data = TransformData(filepath=filename, validate=False)

        try:
            self.data_to_upload = transform_data.Output()
            self.update_console(transform_data.Report())
        except AttributeError as error_message:
            self.update_console(
                f"Unexpected input: {error_message}. Import file not correctly formatted."
            )
        except ValidationFailed as error_message:
            self.update_console(f"Validation failed\n\n{error_message}")
        else:
            transform_data.Report()
            self.button_upload.configure(state="normal")

    def interpolate_color(self, start_color, end_color, fraction):
        start_rgb = mcolors.hex2color(start_color)
        end_rgb = mcolors.hex2color(end_color)
        interpolated_rgb = [
            start + fraction * (end - start) for start, end in zip(start_rgb, end_rgb)
        ]
        return mcolors.rgb2hex(interpolated_rgb)

    def generate_colors(self, num_colors):
        start_color = "#b20000"
        end_color = "#467000"

        colors = []
        for i in range(num_colors):
            fraction = i / (num_colors - 1)
            color = self.interpolate_color(start_color, end_color, fraction)
            colors.append(color)

        return colors

    def update_progressbar(self, progress, step, item_count):
        self.progressbar.set(progress)
        colors = self.generate_colors(item_count)
        self.progressbar.configure(progress_color=colors[step])
        self.update_idletasks()

    def upload(self):
        try:
            api.post_data(data=self.data_to_upload, callbck=self.update_progressbar)
        except:
            self.update_console("Undefined error. Please try again.")
        else:
            self.update_console(f"Uploading complete.\n" + api.report())
            self.button_export_report.configure(state="normal")

            try:
                api.export_report()
            except:
                self.update_console(
                    "An error occured when saving the report file. Please try again."
                )


app = App()
app.iconbitmap(os.path.join(basedir, "assets/favicon.ico"))
app.mainloop()
