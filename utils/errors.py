from functools import partial
from typing import Any, Callable, Awaitable, Dict, Type, TypeVar, Union

from discord.ext import commands
from discord import app_commands

from views.link import View as LinkView


DiscordError = Union[commands.CommandError, app_commands.AppCommandError]

E = TypeVar('E', bound=DiscordError)

ErrorHandler = Callable[[E, Callable[..., Awaitable]], Awaitable[None]]


class ErrorDispatcher:
    def __init__(self):
        self.handlers: Dict[Type[BaseException], ErrorHandler] = {}
        self.responders_kwargs: Dict[ErrorHandler, Dict[str, Any]] = {}

    def register(self, *exc: Type[E]):
        """Decorator to register a handler for a specific exception."""
        def decorator(func: ErrorHandler[E]) -> ErrorHandler[E]:
            if func not in self.responders_kwargs:
                self.responders_kwargs[func] = {}
            for e in exc:
                self.handlers[e] = func
            return func
        return decorator

    def with_responder_kwargs(self, **kwargs):
        """Attach kwargs for the responder."""
        def decorator(func: ErrorHandler[E]) -> ErrorHandler[E]:
            existing = self.responders_kwargs.get(func, {})
            self.responders_kwargs[func] = {**existing, **kwargs}
            return func
        return decorator

    async def dispatch(self, error: DiscordError, responder: Callable[..., Awaitable]) -> bool:
        """Dispatch error to the nearest matching handler."""
        for cls in type(error).__mro__:
            if cls in self.handlers:
                handler = self.handlers[cls]
                kwargs = self.responders_kwargs.get(handler, {})
                if kwargs:
                    responder = partial(responder, **kwargs)
                await handler(error, responder)
                return True

        await responder(content=f"🕳️ Unhandled error: {type(error).__name__}")
        return False

    def report_bug(self):
        """Shortcut decorator for reporting bugs with a prefilled view."""
        return self.with_responder_kwargs(view=LinkView("Report a Bug", "https://github.com/PaulMarisOUMary/Discord-Bot/issues/new?template=bug_report.md"))