import asyncio.exceptions
import hikari
import lightbulb
import datetime

plugin = lightbulb.Plugin("Error Handler")
plugin.add_checks(lightbulb.checks.has_guild_permissions(hikari.Permissions.ADMINISTRATOR))


class OutOfBoundError(Exception):
    def __init__(self):
        self.message = f"You cannot move out of the map."
        super().__init__(self.message)


class BarrierTraverseError(Exception):
    def __init__(self):
        self.message = f"You cannot move into a barrier."
        super().__init__(self.message)


@plugin.listener(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    if isinstance(event.exception, lightbulb.CommandInvocationError):
        await event.context.respond(
            f"Oh no! Something went wrong during invocation of command `{event.context.command.name}`.",
            delete_after=10, flags=hikari.MessageFlag.EPHEMERAL)
        raise event.exception

    # Unwrap the exception to get the original cause
    exception = event.exception.__cause__ or event.exception

    if isinstance(exception, lightbulb.NotOwner):
        await event.context.respond(f"{event.context.author.mention}, You are not the owner of this bot.",
                                    delete_after=10, user_mentions=True, flags=hikari.MessageFlag.EPHEMERAL)

    elif isinstance(exception, lightbulb.CommandIsOnCooldown):
        retry_in = datetime.datetime.now() + datetime.timedelta(seconds=exception.retry_after)
        retry_in_ts = int(retry_in.timestamp())
        await event.context.respond(f"{event.context.author.mention}, "
                                    f"This command is on cooldown. "
                                    f"Retry <t:{retry_in_ts}:R>.",
                                    delete_after=10, user_mentions=True, flags=hikari.MessageFlag.EPHEMERAL)

    elif isinstance(exception, lightbulb.MissingRequiredPermission):
        await event.context.respond(
            f"{event.context.author.mention}, You do not have the permission to run this command.", delete_after=10,
            user_mentions=True, flags=hikari.MessageFlag.EPHEMERAL)

    elif isinstance(exception, lightbulb.CommandNotFound):
        await event.context.respond(
            f"{event.context.author.mention}, The command does not exist.", delete_after=10,
            user_mentions=True, flags=hikari.MessageFlag.EPHEMERAL)

    else:
        raise exception


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
