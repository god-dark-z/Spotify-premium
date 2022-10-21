           
            dpg.add_input_text(label="logger", tag="log_section", multiline=True, width=-1, height=300, readonly=True)
    
    def start(self):
        dpg.show_viewport()
        dpg.start_dearpygui()