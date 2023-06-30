import discord
import yaml

from discord import Locale, app_commands
from discord.app_commands import locale_str, TranslationContextLocation, TranslationContextTypes
from discord.ext import commands
from typing import Optional, Union
from os.path import join, exists

from classes.utilities import root_directory

class CustomTranslator(app_commands.Translator):
    async def load(self) -> None:
        self.EN = { Locale.british_english, Locale.american_english }

        self.NAME = [
            TranslationContextLocation.command_name,
            TranslationContextLocation.group_name,
            TranslationContextLocation.parameter_name,
        ]
        self.DESCRIPTION = [
            TranslationContextLocation.command_description,
            TranslationContextLocation.group_description,
            TranslationContextLocation.parameter_description,
        ]

    def __get_i18n(self,
                    i18n_path: str,
                    groups: list[str],
                    command: Optional[str],
                    narrowing: Optional[dict[str, str]],
                    target: Optional[str],
                    locale: str
                ) -> Optional[str]:
        with open(i18n_path, 'r') as file:
            data = yaml.safe_load(file)

        # groups
        for group in groups:
            if "groups" not in data:
                return None
            data = data["groups"]
            if group not in data:
                return None
            data = data[group]

        # command
        if command is not None and "commands" in data:
            data = data["commands"]
            if command not in data:
                return None
            data = data[command]

        # parameters | choices | other
        if narrowing:
            for key, value in narrowing.items():
                if key not in data:
                    return None
                data = data[key]
                if value not in data:
                    return None
                data = data[value]

        # name | description
        if target not in data:
            return None
        data = data[target]

        # locale
        if locale not in data:
            return None
        data = data[locale]

        return data

    def __get_i18n_simple(self,
                                i18n_path: str,
                                command: str,
                                locale: str
                            ) -> Optional[str]:
        with open(i18n_path, 'r') as file:
            data = yaml.safe_load(file)

        if "context-menus" not in data:
            return None
        data = data["context-menus"]

        if command not in data:
            return None
        data = data[command]

        if "name" not in data:
            return None
        data = data["name"]

        if locale not in data:
            return None
        return data[locale]

    def __to_top(self, command: Union[app_commands.Command, app_commands.Group], entries: Optional[list[Union[app_commands.Command, app_commands.Group]]] = None) -> list[Union[app_commands.Command, app_commands.Group]]:
        """
        Parameters
        ------------
        command: Union[:class:`app_commands.Command`, :class:`app_commands.Group`]
            The command or group to get the top level list from.
        
        Returns
        --------
        list[Union[:class:`app_commands.Command`, :class:`app_commands.Group`]]
            The list of commands or groups from the top level to the command or group.
            Root parent -> ... -> command or group provided.
        """
        if not entries:
            entries = []
        while command.parent is not None:
            command = command.parent
            entries.append(command)

        entries.reverse()
        return entries

    def __get_str_path(self, obj_path: list[Union[app_commands.Command, app_commands.Group]]):
        return [obj.name.lower() for obj in obj_path]

    def __i18n_file(self, cog: str) -> str:
        return join(root_directory, "i18n", f"{cog}.yml")

    async def translate(self,
                        _: locale_str,
                        locale: discord.Locale,
                        context: TranslationContextTypes
                        ) -> Optional[str]:
        """
        Command v
        Group v
        Parameter v
        ContextMenu v
        Choice v
        Other x
        
        Parameters
        ------------
        string: :class:`locale_str`
            The string being translated.
        locale: :class:`discord.Locale`
            The locale the target language to translate to.
        context: :class:`TranslationContext`
            The translation context where the string originated from.
            For better type checking ergonomics, the ``TranslationContextTypes``
            type can be used instead to aid with type narrowing. It is functionally
            equivalent to :class:`TranslationContext`.
        
        Returns
        ---------
        Optional[:class:`str`]
        If the translation is not found, then ``None`` is returned and no translation is set on discord's side.
        """
        locale_code = str(locale)

        if locale_code not in ["en", "fr"]: # ! REMOVE
            return None

        if locale in self.EN:
            locale_code = "en"
            return None # Don't translate English as it's supposed to be the default language.

        target = None
        if context.location in self.NAME:
            target = "name"
        elif context.location in self.DESCRIPTION:
            target = "description"

        reference = context.data

        if isinstance(reference, app_commands.Command):
            obj_path = self.__to_top(reference)
            if isinstance(reference.binding, commands.Cog):
                file = self.__i18n_file(reference.binding.qualified_name.lower())
                if not exists(file):
                    print(f"Missing i18n file for {reference.binding.qualified_name.lower()}") # ! REMOVE
                    return None
                return self.__get_i18n(file, self.__get_str_path(obj_path), reference.name.lower(), None, target, locale_code)

        elif isinstance(reference, app_commands.Group):
            obj_path = self.__to_top(reference, [reference])
            if obj_path:
                file = self.__i18n_file(obj_path[0].name.lower())
            else:
                file = self.__i18n_file(reference.name.lower())
            if not exists(file):
                return None
            return self.__get_i18n(file, self.__get_str_path(obj_path), None, None, target, locale_code)

        elif isinstance(reference, app_commands.Parameter):
            obj_path = self.__to_top(reference.command)
            if isinstance(reference.command.binding, commands.Cog):
                file = self.__i18n_file(reference.command.binding.qualified_name.lower())
                if not exists(file):
                    print(f"Missing i18n file for {reference.command.binding.qualified_name.lower()}")
                    return None
                return self.__get_i18n(file, self.__get_str_path(obj_path), reference.command.name.lower(), {"parameters": reference.name.lower()}, target, locale_code)

        elif isinstance(reference, app_commands.ContextMenu):
            file = self.__i18n_file("i18n.contextmenus")
            if not exists(file):
                print(f"Missing i18n file for i18n.contextmenus")
                return None
            return self.__get_i18n_simple(file, reference.name.lower(), locale_code)

        elif isinstance(reference, app_commands.Choice):
            file = self.__i18n_file("i18n.choices")
            if not exists(file):
                print(f"Missing i18n file for i18n.choices")
                return None
            return self.__get_i18n_simple(file, reference.name.lower(), locale_code)

        else: # Other
            return None