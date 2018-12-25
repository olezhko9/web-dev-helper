import sublime
import sublime_plugin
import re
import sys
import os

# path to python site-packages
site_packages_full_path = \
    sorted([path if re.search(r'[pP]ython\d{1,2}\-\d{1,2}\\$', path) else '' for path in os.environ.get('PATH')
           .split(';')], key=lambda s: len(s))[-1]
sys.path.insert(0, site_packages_full_path + 'Lib\site-packages')
import requests
from bs4 import BeautifulSoup


class WebDevHelperCommand(sublime_plugin.WindowCommand):

    def __init__(self, window):
        super().__init__(window)
        self.view = self.window.active_view()
        self.command_text = None
        self.command_type = None
        self.command_pos = None

    def get_command_type(self, command_position):
        if command_position.begin() == command_position.end():
            return None
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
        if command_position.begin() == command_position.end():
            return None
        selected_text = self.view.substr(command_position).lower().strip(' ')
        selected_text = re.search(r'[a-z\-]+', selected_text)
        if selected_text:
            return selected_text.group(0)
        else:
            return None

    def get_command_description(self, command_text, command_type):
        command_description = "Похоже, здесь нечего показывать."

        if command_text is None or command_type is None:
            return command_description

        mozila_catalog = {
            'root': 'https://developer.mozilla.org/en-US/docs/Web/',
            'css': ['CSS/'],
            'html': ['HTML/Element/'],
            'js': ['API/Document/', 'API/Element/', 'API/EventTarget/']
        }
        url_catalog = mozila_catalog

        base_url = url_catalog.get('root')

        for u in url_catalog.get(command_type):
            url = base_url + u + command_text
            print(url)
            try:
                response = requests.get(url)
                bs = BeautifulSoup(response.text, features="html.parser")
                try_count = 0
                html_selector = '#wikiArticle > p'
                is_description = -1
                while is_description == -1 and try_count < 2:
                    command_description = bs.select(html_selector)[try_count].getText().replace('<', '&lt;').replace(
                        '>', '&gt;')
                    is_description = command_description.lower().find(command_text)
                    try_count += 1
                if is_description != -1:
                    break
            except IndexError:
                command_description = "Похоже, здесь нечего показывать..."

        return command_description

    def show_command_description(self, content):
        cursor_text_point = self.view.sel()[0]
        cursor_line = self.view.rowcol(cursor_text_point.end())[0]
        cursor_zero_col = self.view.text_point(cursor_line, 0)
        viewport_width = self.view.viewport_extent()[0]

        self.view.show_popup(content=content,
                             location=cursor_zero_col,
                             max_width=int(viewport_width / 2),
                             max_height=300)

    def run(self):
        self.command_pos = self.view.sel()[0]
        self.command_text = self.get_command_text(self.command_pos)
        self.command_type = self.get_command_type(self.command_pos)

        content = self.get_command_description(self.command_text, self.command_type)
        self.show_command_description(content)
