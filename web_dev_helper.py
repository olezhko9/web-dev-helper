import sublime
import sublime_plugin
import re

class WebDevHelperCommand(sublime_plugin.WindowCommand):

    def __init__(self, window):
        super().__init__(window)
        self.view = self.window.active_view()
        self.command_text = None
        self.command_type = None
        self.command_pos = None

    def get_command_type(self, command_position):
        line = self.view.substr(self.view.line(command_position.end())).lower()
        if re.search(re.compile(self.command_text + ':'), line):
            return 'css'
        elif re.search(re.compile('\.' + self.command_text + '[\.\(]'), line):
            return 'js'
        elif re.search(re.compile('\</?' + self.command_text), line):
            return 'html'
        else:
            return None

    def get_command_text(self, command_position):
        selected_text = self.view.substr(command_position).lower().strip(' ')
        selected_text = re.search(r'[a-z\-]+', selected_text)
        if selected_text:
            return selected_text.group(0)
        else:
            return None

    def show_command_description(self, content):
        cursor_text_point = self.view.sel()[0]
        cursor_line = self.view.rowcol(cursor_text_point.end())[0]
        cursor_zero_col = self.view.text_point(cursor_line, 0)
        viewport_width = self.view.viewport_extent()[0]

        self.view.show_popup(content=content,
                             location=cursor_zero_col,
                             max_width=int(viewport_width),
                             max_height=300)

    def run(self):
        content = "<h4>Background</h4>" + \
                  "<p>Универсальное свойство background позволяет установить одновременно несколько характеристик фона.</p>" + \
                  "<p>Универсальное свойство background позволяет установить одновременно несколько характеристик фона.Универсальное свойство background позволяет установить одновременно несколько характеристик фона.</p>" + \
                  "<p>Универсальное свойство background позволяет установить одновременно несколько характеристик фона.</p>"

        self.command_pos = self.view.sel()[0]
        if self.command_pos.end() != self.command_pos.begin():
            self.command_text = self.get_command_text(self.command_pos)
            self.command_type = self.get_command_type(self.command_pos)
            self.show_command_description(content)
        else:
            print('0' * 10)
