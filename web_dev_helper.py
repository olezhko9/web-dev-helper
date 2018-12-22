import sublime
from sublime import Window
import sublime_plugin


class WebDevHelperCommand(sublime_plugin.TextCommand):

    def show_command_description(self, content):
        self.view.show_popup(content=content,
                             flags=sublime.COOPERATE_WITH_AUTO_COMPLETE,
                             max_width=1500,
                             max_height=100)

    def run(self, edit):
        content = "<h4>Background</h4>" + \
                  "<p>Универсальное свойство background позволяет установить одновременно несколько характеристик фона.</p>" + \
                  "<p>Универсальное свойство background позволяет установить одновременно несколько характеристик фона.Универсальное свойство background позволяет установить одновременно несколько характеристик фона.</p>" + \
                  "<p>Универсальное свойство background позволяет установить одновременно несколько характеристик фона.</p>"

        self.show_command_description(content)
