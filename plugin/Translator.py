# -*- coding: utf-8 -*-
"""
Google Translate in Flowlauncher.

This plugin allows translation using Google Translate and copy it.
"""

from flowlauncher import FlowLauncher, FlowLauncherAPI
import urllib.parse
import urllib.request
import html
import re
import subprocess


def translate(query: str, to_language="en", from_language="auto"):
    """Get translated query from Google translate."""
    headers = {"User-Agent": "Edge, Brave, Firefox, Chrome, Opera"}
    base_link = "https://translate.google.com/m?tl=%s&sl=%s&q=%s"

    query_quoted = urllib.parse.quote(query)
    link = base_link % (to_language, from_language, query_quoted)
    request = urllib.request.Request(link, headers=headers)

    data = urllib.request.urlopen(request).read().decode("utf-8")
    expr = r'class="result-container">(.*?)<'
    re_result = re.findall(expr, data)
    return html.unescape(re_result[0]) if len(re_result) > 0 else ""


def copy2clip(txt: str):
    """Put translation into clipboard."""
    # Allows to copy text without trailing '\n'
    cmd = f'cmd /c "echo|set /p={txt}"| clip'
    try:
        subprocess.check_call(cmd, shell=True)
        return True
    except:
        return False


class GoogTranslate(FlowLauncher):
    def query(self, param: str = ''):
        param = param.strip()
        try:
            from_language = "auto"
            to_language = "en"
            param_parts = param.split(maxsplit=1)
            query = param

            if ( # If the first word is either "from:to" or "from:" or ":to"
                len(param_parts) > 1
                and param_parts[0].count(":") == 1
                and len(param_parts[0]) > 1
            ):
                lang_parts = param_parts[0].split(":")
                from_language = lang_parts[0] or from_language
                to_language = lang_parts[1] or to_language
                query = param_parts[1]

            if len(query) == 0:
                return [{
                    "Title": ":es text to translate",
                    "SubTitle": ("use: 'tr :es your expresion' to translate"
                                 "from auto-detected to Spanish"),
                    "IcoPath": "Images/gt.png"}]

            try:
                translation = translate(query, to_language, from_language)
            except:
                raise Exception("Could not access translate.google.com")

            return [{
                "Title": to_language + ": " + translation,
                "SubTitle": from_language + ": " + query,
                "IcoPath": "Images/gt.png",
                "JsonRPCAction": {"method": "copy",
                                  "parameters": [translation]}}]
        except Exception as e:
            return [{
                "Title": "Error",
                "SubTitle": str(e),
                "IcoPath": "Images/gt.png"}]

    def copy(self, txt: str):
        """Copy translation to clipboard."""
        if copy2clip(txt):
            FlowLauncherAPI.show_msg("Copied to clipboard", f"\"{txt}\"")
        else:
            FlowLauncherAPI.show_msg(
                "Failed to copy", "Error copying translation to clipboard")


if __name__ == "__main__":
    GoogTranslate()
