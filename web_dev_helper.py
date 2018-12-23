import sublime
import sublime_plugin


class WebDevHelperCommand(sublime_plugin.WindowCommand):

    def __init__(self, window):
        super().__init__(window)
        self.view = self.window.active_view()

    def show_command_description(self, content):

        cursor_text_point = self.view.sel()[0].end()
        cursor_line = self.view.rowcol(cursor_text_point)[0]
        cursor_zero_col = self.view.text_point(cursor_line, 0)
        print(cursor_zero_col)

        # end_pos = self.view.sel()
        # line_content = self.view.substr(self.view.line(end_pos[0].end()))

        self.view.show_popup(content=content,
                        location=cursor_zero_col,
                        max_width=1000,
                        max_height=300)

    def run(self):
        content = "<h4>Background</h4>" + \
                  "<p>Универсальное свойство background позволяет установить одновременно несколько характеристик фона.</p>" + \
                  "<p>Универсальное свойство background позволяет установить одновременно несколько характеристик фона.Универсальное свойство background позволяет установить одновременно несколько характеристик фона.</p>" + \
                  "<p>Универсальное свойство background позволяет установить одновременно несколько характеристик фона.</p>"

        self.show_command_description(content)
