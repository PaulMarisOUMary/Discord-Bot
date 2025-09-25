from typing import Callable, Awaitable, Type, TypeVar, Union

from discord.ext import commands
from discord import app_commands


DiscordError = Union[commands.CommandError, app_commands.AppCommandError]

E = TypeVar('E', bound=DiscordError)

ErrorHandler = Callable[[E, Callable[..., Awaitable]], Awaitable[None]]


class ErrorDispatcher:
    def __init__(self):
        self.handlers: dict[Type[BaseException], ErrorHandler] = {}

    def register(self, *exc: Type[E]):
        """Decorator to register a handler for a specific exception."""
        def decorator(func: ErrorHandler[E]) -> ErrorHandler[E]:
            for e in exc:
                self.handlers[e] = func
            return func
        return decorator

    async def dispatch(self, error: DiscordError, responder: Callable[..., Awaitable]) -> bool:
        """Dispatch error to the nearest matching handler."""
        for cls in type(error).__mro__:
            if cls in self.handlers:
                await self.handlers[cls](error, responder)
                return True

        await responder(content=f"🕳️ Unhandled error: {type(error).__name__}")
        return False