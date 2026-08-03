from __future__ import annotations

from collections.abc import Awaitable, Callable
from functools import partial
from typing import Any, TypeVar

from discord import app_commands
from discord.ext import commands

from views.link import View as LinkView

DiscordError = commands.CommandError | app_commands.AppCommandError

E = TypeVar('E', bound=DiscordError)

Responder = Callable[..., Awaitable[Any]]
ErrorHandler = Callable[[E, Responder], Awaitable[None]]


class ErrorDispatcher:
    def __init__(self) -> None:
        self.handlers: dict[type, ErrorHandler[Any]] = {}
        self.responders_kwargs: dict[ErrorHandler[Any], dict[str, Any]] = {}

    def register(self, *exc: type[E]) -> Callable[[ErrorHandler[E]], ErrorHandler[E]]:
        def decorator(func: ErrorHandler[E]) -> ErrorHandler[E]:
            self.responders_kwargs.setdefault(func, {})

            for e in exc:
                self.handlers[e] = func

            return func

        return decorator

    def with_responder_kwargs(
        self, **kwargs: Any
    ) -> Callable[[ErrorHandler[E]], ErrorHandler[E]]:
        def decorator(func: ErrorHandler[E]) -> ErrorHandler[E]:
            existing = self.responders_kwargs.get(func, {})
            self.responders_kwargs[func] = {**existing, **kwargs}

            return func

        return decorator

    def report_bug(self) -> Callable[[ErrorHandler[E]], ErrorHandler[E]]:
        url = "https://github.com/PaulMarisOUMary/Discord-Bot/issues/new?template=bug_report.md"
        return self.with_responder_kwargs(view=LinkView("Report a Bug", url))

    async def dispatch(self, error: DiscordError, responder: Responder) -> bool:
        for cls in type(error).__mro__:
            handler = self.handlers.get(cls)
            if handler is None:
                continue

            kwargs = self.responders_kwargs.get(handler, {})
            if kwargs:
                responder = partial(responder, **kwargs)

            await handler(error, responder)
            return True

        await responder(content=f":hole: Unhandled error: {type(error).__name__}")
        return False
