import os
import time
from enum import Enum

import dearpygui.dearpygui as dpg
from bot import SpotifyBot, parse_cards


class State(Enum):
    IDLE = 1
    RUNNING = 2
    STOPPED = 3
    CANCELLED = 4

    

class Window:
    def __init__(self, name, width=800, height=600, resizeable=True):
        self.window_name = name
        self.main_window = "main_window"
        self.width = width
        self.height = height
        self.resizeable = resizeable

        self.curr_email = ""
        self.curr_passwd = ""
        self.curr_card = ""

        self.run_state = State.IDLE
        self.current_file = ""



        # init settings
        self.init_settings()


    def init_settings(self):
        dpg.create_context()
        dpg.create_viewport()
        dpg.setup_dearpygui()
        dpg.set_viewport_title(self.window_name)
        dpg.set_viewport_width(self.width)
        dpg.set_viewport_height(self.height)
        dpg.set_viewport_resizable(self.resizeable)
        with dpg.font_registry():
            self.default_font = dpg.add_font("arial.ttf", 15)

        with dpg.file_dialog(directory_selector=False, show=False, callback=self.file_pick_cb, id="file_dialog", height=400):
            dpg.add_file_extension(".txt", color=(150, 255, 150, 255))

    def file_pick_cb(self, sender: int, app_data):
        self.current_file = app_data["file_path_name"]
        dpg.set_value("current_file", f"File: {os.path.basename(self.current_file)}")

        
    def get_create_account(self) -> bool:
        return dpg.get_value("create_acc")

    def get_headless(self) -> bool:
        return dpg.get_value("headless")

    def set_state(self, state: State):
        self.run_state = state
        dpg.set_value("status_text", f"Status: {self.run_state.name}")

    def log(self, msg: str):
        val = dpg.get_value("log_section")
        dpg.set_value("log_section", val + msg + "\n")

    def clear_logs(self):
        dpg.set_value("log_section", "")

    def start_collection(self):
        if self.current_file == "":
            self.log("No file selected")
            return

        if self.run_state == State.RUNNING:
            self.log("Already running")
            return
        self.set_state(State.RUNNING)

        cards_dict = parse_cards(self.current_file)

        for indx, info in cards_dict.items():
            bot = SpotifyBot(
                card=info["card"],
                email=info["email"],
                password=info["password"],
                reference=f"refer-{indx}",
                is_headless=self.get_headless(),
                logger=self.log
            )

            dpg.set_value("current_email", info["email"])
            dpg.set_value("current_passwd", info["password"])
            dpg.set_value("current_card", info["card"])

            if self.get_create_account():
                if not bot.create_account(loger=self.log):
                    self.log(f"Account Error: {bot.email}:{bot.password}:{info['card']}")
                    self.log("Moving to next")
                    bot.driver.quit()
                    continue
            else:
                bot.login(info["email"], info["password"], logger=self.log)

            res = bot.premify(loger=self.log)
            if res:
                self.log("Success!")
            else:
                self.log(
                    f"Error! failed to premify {info['email']}:{info['password']}:{info['card']}"
                )
                with open(bot.log_file_name, "w") as f:
                    f.write(dpg.get_value("log_section"))
                self.log("Saved log to file")
                self.log("Moving to next")
                time.sleep(0.1)
                bot.driver.quit()
                continue

    def init_window(self):
        with dpg.window(tag=self.main_window) as window:
            dpg.set_item_theme(window, "theme_dark")
            dpg.set_primary_window(window, True)
            dpg.bind_font(self.default_font)
            dpg.add_spacer(height=5)

            with dpg.group(horizontal=True, width=self.width/2.1):
                with dpg.group(label="left", horizontal=False, width=50):
                    dpg.add_text(f"Status: {self.run_state.name}", 
                            color=(255, 255, 0), 
                            tag="status_text", bullet=True)
        

                    dpg.add_text(f"File: {os.path.basename(self.current_file)}", tag="current_file", color=(66, 135, 245), bullet=True)
                    dpg.add_text(f"Email: {self.curr_email}", tag="current_email", color=(66, 135, 245), bullet=True)
                    dpg.add_text(f"Password: {self.curr_passwd}", tag="current_password", color=(66, 135, 245), bullet=True)
                    dpg.add_text(f"Card: {self.curr_card}", tag="current_card", color=(66, 135, 245), bullet=True)
                    
                    dpg.add_spacer(height=10)
                    

                with dpg.group(label="right", horizontal=False):
                    with dpg.group(horizontal=True):
                        dpg.add_checkbox(label="Create Account", tag="create_acc")
                        dpg.add_checkbox(label="Show Browser Window", tag="headless")

                    dpg.add_spacer(height=10)
                       
                    dpg.add_button(label="Start Bot", tag="start_bot", callback=lambda: self.start_collection())
                    dpg.add_spacer(height=3)
                    dpg.add_button(label="Select File", tag="select_file", callback=lambda: dpg.configure_item("file_dialog", show=True))
                    dpg.add_spacer(height=3)
                    dpg.add_button(label="Clear Logs", callback=lambda: self.clear_logs(), width=5)
                    dpg.add_spacer(height=10)

            dpg.add_text("Logs:", color=(255, 255, 0), bullet=True)
            dpg.add_input_text(
                label="logger", 
                tag="log_section", 
                multiline=True, 
                width=-1, 
                height=300, 
                readonly=True
            )
    
    def show(self):
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

    def close(self):
        dpg.stop_dearpygui()




if __name__ == '__main__':
    win = Window(
        "Spotify Bot", 
        width=800, 
        height=535,
        resizeable=False
    )

    win.init_window()
    win.show()
