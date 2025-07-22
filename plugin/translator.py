"""
Google Translate in Flowlauncher.

This plugin allows translation using Google Translate.
"""

import urllib.parse
import urllib.request
import html
import re
import concurrent.futures
from flowlauncher import FlowLauncher, FlowLauncherAPI
from language import LANGUAGES, guess_lang_code
from utils import copy_to_clipboard


def translate(query: str, from_language="auto", to_language="en") -> str:
    """
    Get translated query from Google translate.

    Args:
        query (str): Query to translate.
        from_language (str, optional): Translate from this language.
            Defaults to "auto".
        to_language (str, optional): Translate to this language.
            Defaults to "en".

    Returns:
        str: Translated query.
    """
    headers = {"User-Agent": "Edge, Brave, Firefox, Chrome, Opera"}
    base_link = "https://translate.google.com/m?tl=%s&sl=%s&q=%s"

    query_quoted = urllib.parse.quote(query)
    link = base_link % (to_language, from_language, query_quoted)
    request = urllib.request.Request(link, headers=headers)

    try:
        data = urllib.request.urlopen(request).read().decode("utf-8")
        expr = r'class="result-container">(.*?)<'
        re_result = re.findall(expr, data)
        return html.unescape(re_result[0]) if len(re_result) > 0 else ""
    except:
        raise Exception("Could not access translate.google.com")


class Translator(FlowLauncher):
    # !!! ADD DEBOUNCE/THROTTLE !!!
    # TODO: Too many requests are being sent while typing, add debounce
    # TODO: or throttle to avoid hitting google's request limit.
    def query(self, param: str = '') -> list:
        param = param.strip()
        default_langs: list[str] = [
            lang for x in self.get_setting('default_languages').split(',')
            if (lang := guess_lang_code(x)) is not None
        ]
        code_separator: str = self.get_setting('code_separator')
        try:
            from_language = None
            to_language = None
            param_parts = param.split(maxsplit=1)
            query = param

            # Extract language notation if present
            if (
                len(param_parts) > 1
                and param_parts[0].count(code_separator) == 1
                and len(param_parts[0]) > 1
            ):
                lang_parts = param_parts[0].split(code_separator)
                from_language = guess_lang_code(lang_parts[0])
                to_language = guess_lang_code(lang_parts[1])
                if (not from_language and lang_parts[0]
                        or not to_language and lang_parts[1]):
                    raise Exception("Invalid language notation")
                query = param_parts[1]
            from_language = from_language or "Auto"

            # Placeholder if query is empty
            if len(query) == 0:
                return [{
                    "Title": f"[from]{code_separator}[to] text to translate",
                    "SubTitle": (
                        f"e.g., `tr {code_separator}es your text` to "
                        "translate from auto-detected to Spanish"
                    ),
                    "IcoPath": "images/gt.png"}]

            # Default languages except to_language/from_language
            filtered_langs = [
                lang for lang in default_langs
                if lang != to_language and lang != from_language
            ]
            # List of default + specified translations
            translations = []
            # Sending translation requests in parallel for better performance
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures: list[concurrent.futures.Future] = []
                if to_language:
                    futures.append(executor.submit(
                        translate, query, from_language, to_language))
                for lang in filtered_langs:
                    futures.append(executor.submit(
                        translate, query, from_language, lang))

                # Waiting for results and then appending them to the list
                results = [f.result() for f in futures]

                if len(results) == 0 and not to_language:
                    raise Exception("Default language is not set")
                elif len(results) == 0:
                    raise Exception("Add a second default language "
                                    "to translate from the first one")

                if to_language:
                    translations.append({
                        "lang": to_language,
                        "default": False,
                        "result": results[0]
                    })
                for i, lang in enumerate(filtered_langs):
                    translations.append({
                        "lang": lang,
                        "default": True,
                        "result": results[i + bool(to_language)]
                    })
            # Return translations list:
            # if to/from languages are not specified by user, render
            # bright icon, but if they are - render dimmed icon for
            # every default translation, and bright for the rest.
            return [
                {
                    "Title": tr["result"],
                    "SubTitle":
                        f'{LANGUAGES.get(from_language, from_language)} → '
                        f'{LANGUAGES.get(tr["lang"], tr["lang"])}',
                    "IcoPath":
                        "images/gt"
                        f'{"-dimmed" if tr["default"] and to_language else ""}'
                        ".png",
                    "JsonRPCAction": {"method": "copy",
                                      "parameters": [tr["result"]]}
                } for tr in translations
            ]
        except Exception as e:
            return [{
                "Title": "Error",
                "SubTitle": str(e),
                "IcoPath": "images/gt-dimmed.png"}]

    def copy(self, txt: str) -> None:
        """Copy translation to clipboard."""
        if copy_to_clipboard(txt):
            FlowLauncherAPI.show_msg("Copied to clipboard", f"\"{txt}\"")
        else:
            FlowLauncherAPI.show_msg(
                "Failed to copy", "Error copying translation to clipboard")

    def get_setting(self, name: str) -> str:
        """Get plugin setting by its name in `SettingsTemplate.yaml` file"""
        return self.rpc_request['settings'][name]
