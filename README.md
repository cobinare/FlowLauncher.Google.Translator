# FlowLauncher.Google.Translator

A [Flow Launcher](https://www.flowlauncher.com/) plugin that allows you to translate things with [Google Translate](https://translate.google.com/).

This plugin is a modified port of the Wox plugin [Wox.Plugin.GoogleTranslate](https://github.com/laercioskt/Wox.Plugin.GoogleTranslate) by [laercioskt](https://github.com/laercioskt).

## Installation

Type `pm install Google Translate` in your Flow Launcher to have the plugin installed.

## Usage

Use `tr [from_language]:[to_language] (query)` syntax. See some usage examples:

- `tr es:en es mi traducción` - translate the phrase "es mi traducción" from Spanish to English;
- `tr es mi traducción` - translate from auto-detected to default language(s) (only English by default);
- `tr :es my translation` - translate from auto-detected to Spanish;
- `tr es: es mi traducción` - translate from Spanish to default language(s). Useful if auto-detection fails.

> **Tip:** the plugin will try to guess language codes you type, which means, for example, instead of typing `en:es` you can type something like `eng:spanish`, and it will work just fine!

## Plugin Settings

- **Default language code(s).**  
  Every query you enter will additionaly be translated to your default language(s). Multiple defaults are useful if you often translate from two or more languages back to back.  
  Use [language codes](https://cloud.google.com/translate/docs/languages) and use commas for separation, e.g.:
  - `en` - your only default language is English;
  - `es, de` - both Spanish and German are your default languages.
- **Language code separator.**  
  By default you have to use `:` symbol when specifying languages while using a plugin. You can change that to either be `>` or `|` symbol instead.
