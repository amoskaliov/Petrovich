# coding: utf-8
import os
import json
import re

__author__ = 'damirazo <me@damirazo.ru>'


# Текущая директория
CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
# Путь до файла с правилами округления
DEFAULT_RULES_PATH = os.path.join(CURRENT_PATH, 'rules', 'rules.json')


class Petrovich(object):
    """
    Основной класс для склонения кириллических ФИО
    """
    # Разделители
    separators = ("-", " ")

    def __init__(self, rules_path=None):
        """
        :param rules_path: Путь до файла с правилами.
            В случае отсутствия будет взят путь по умолчанию,
            указанный в `DEFAULT_RULES_PATH`
        :return:
        """
        if rules_path is None:
            rules_path = DEFAULT_RULES_PATH

        if not os.path.exists(rules_path):
            raise IOError((
                'File with rules {} does not exists!'
            ).format(rules_path))

        with open(rules_path, 'r', encoding='utf8') as fp:
            self.data = json.load(fp)

    def firstname(self, value, case, gender=None):
        """
        Склонение имени

        :param value: Значение для склонения
        :param case: Падеж для склонения (значение из класса Case)
        :param gender: Грамматический род
        """
        if not value:
            raise ValueError('Firstname cannot be empty.')

        return self.__inflect(value, case, 'firstname', gender)

    def lastname(self, value, case, gender=None):
        """
        Склонение фамилии

        :param value: Значение для склонения
        :param case: Падеж для склонения (значение из класса Case)
        :param gender: Грамматический род
        """
        if not value:
            raise ValueError('Lastname cannot be empty.')

        return self.__inflect(value, case, 'lastname', gender)

    def middlename(self, value, case, gender=None):
        """
        Склонение отчества

        :param value: Значение для склонения
        :param case: Падеж для склонения (значение из класса Case)
        :param gender: Грамматический род
        """
        if not value:
            raise ValueError('Middlename cannot be empty.')

        return self.__inflect(value, case, 'middlename', gender)

    def __inflect(self, value, case, name_form, gender=None):
        segments = re.split('([' + "".join(self.separators) + '])', value)
        result = str()

        for segment in segments:
            if segment and (segment not in self.separators):
                inflected = self.__apply_rule(segment.lower(), case, name_form, gender)
                if segment.lower() == segment:
                    result += inflected
                elif segment.capitalize() == segment:
                    result += inflected.capitalize()
                elif segment.upper() == segment:
                    result += inflected.upper()
                else:
                    result += inflected.capitalize()
            else:
                result += segment

        return result

    def __find_rule(self, name, name_form, gender):
        exception_rule = self.__find_exception_rule(name, name_form, gender)
        if exception_rule:
            return exception_rule

        for rule in self.data[name_form]['suffixes']:
            if gender is not None and rule['gender'] not in (gender, 'androgynous'):
                continue

            for pattern in rule['test']:
                if name.endswith(pattern):
                    return rule

        return False

    def __find_exception_rule(self, name, name_form, gender):
        if 'exceptions' not in self.data[name_form]:
            return False

        for rule in self.data[name_form]['exceptions']:
            if gender is not None and rule['gender'] not in (gender, 'androgynous'):
                continue

            if name in rule['test']:
                return rule

        return False

    def __apply_rule(self, name, case, name_form, gender=None):
        rule = self.__find_rule(name, name_form, gender)

        if rule['mods'][case] == '.':
            return name
        else:
            result = name[:len(name) - rule['mods'][case].count('-')]
            result += rule['mods'][case].replace('-', '')

        return result
