"""Contains the utilities needed for translation."""


import configparser



def getLang(inter, section, line):
    language = inter.locale

    languages = {
        'en-US': "translation/lang_en.ini",
        'en-GB': "translation/lang_en.ini",
        'ko': "translation/lang_ko.ini"
    }

    if language in languages:
        file = languages[language]
    else:
        file = languages['en-US']

    lang = configparser.ConfigParser()
    lang.read(file, encoding='utf-8')
    try:
        lineStr = lang.get(section, line)
    except configparser.NoOptionError:
        file = languages['en-US']
        lang.read(file, encoding='utf-8')
        lineStr = lang.get(section, line)
    return lineStr
