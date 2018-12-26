# -*- coding: utf-8 -*-
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
import webbrowser

class WebDevHelperCommand(sublime_plugin.WindowCommand):

    def __init__(self, window):
        super().__init__(window)
        self.command_text = None
        self.command_type = None
        self.command_pos = None
        self.url = None

    def get_command_type(self, command_position):
        if command_position.begin() == command_position.end():
            return None
        line = self.view.substr(self.view.line(command_position.end())).lower()
        if re.search(re.compile(self.command_text + '[\w-]*:'), line):
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

    def extract_command_summary(self, html_text, command_text):
        command_summary = None
        try:
            bs = BeautifulSoup(html_text, features="html.parser")
            try_count = 0
            html_selector = '#wikiArticle > p'
            is_description = -1
            while is_description == -1 and try_count < 3:
                command_summary = bs.select(html_selector)[try_count].getText().replace('<', '&lt;').replace(
                    '>', '&gt;')
                is_description = command_summary.lower().find(command_text)
                try_count += 1
            if is_description != -1:
                return command_summary
            else:
                return None
        except IndexError:
            return None

    def extract_command_parameters(self, html_text, command_type):
        command_parameters = {}
        try:
            bs = BeautifulSoup(html_text, features="html.parser")
            dt_list = bs.select('dl')[0].select('dt')
            dd_list = bs.select('dd')
            for dt, dd in zip(dt_list, dd_list):
                parameter_title = ""
                for child in dt.children:
                    parameter_title = child.getText().replace('<', '&lt;').replace('>', '&gt;')
                    if len(parameter_title) > 0:
                        break
                parameter_description = dd.getText().replace('<', '&lt;').replace('>', '&gt;')
                command_parameters[parameter_title] = parameter_description

        except IndexError:
            pass
        return command_parameters

    def get_command_description(self, command_text, command_type):
        command_summary_none = "There is no information to show."
        command_summary = ""
        command_parameters_none = {"There are no attributes": 'Check out the selected fragment.'}
        command_parameters = None
        if command_text is None or command_type is None:
            self.url = ""
            return [command_summary_none, command_parameters_none]

        mozila_catalog = {
            'root': 'https://developer.mozilla.org/en-US/docs/Web/',
            'css': ['CSS/'],
            'html': ['HTML/Element/'],
            'js': ['API/Document/', 'API/Element/', 'API/EventTarget/']
        }
        url_catalog = mozila_catalog

        base_url = url_catalog.get('root')

        for u in url_catalog.get(command_type):
            self.url = base_url + u + command_text
            response = requests.get(self.url)

            command_summary = self.extract_command_summary(response.text, command_text)
            if command_summary is not None:
                command_parameters = self.extract_command_parameters(response.text, command_type)
                if len(command_parameters) == 0:
                    command_parameters = command_parameters_none
                break
            else:
                command_parameters = command_parameters_none
        return [command_summary, command_parameters]

    def show_command_description(self, content):
        cursor_text_point = self.view.sel()[0]
        cursor_line = self.view.rowcol(cursor_text_point.end())[0]
        cursor_zero_col = self.view.text_point(cursor_line, 0)
        viewport_width = self.view.viewport_extent()[0]

        parameters_html = ""
        for key in content[1]:
            parameters_html += "<h3>" + key + "</h3><p>" + content[1].get(key) + "</p>\n"

        html_content = """
        <a href=\"""" + self.url + """\">""" + self.command_text + """</a>
        <div>
           <p>
        """ + content[0] + \
        """
           </p>
        """ + parameters_html + \
        """
        </div>
        """

        self.view.show_popup(content=html_content,
                             location=cursor_zero_col,
                             max_width=viewport_width,
                             max_height=300,
                             on_navigate=webbrowser.open)

    def run(self):
        self.view = self.window.active_view()
        self.command_pos = self.view.sel()[0]
        self.command_text = self.get_command_text(self.command_pos)
        self.command_type = self.get_command_type(self.command_pos)
        # print(self.command_text, self.command_type)
        content = self.get_command_description(self.command_text, self.command_type)
        self.show_command_description(content)
