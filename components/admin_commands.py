import hikari
import lightbulb

plugin = lightbulb.Plugin("Admin Commands")
plugin.add_checks(lightbulb.checks.owner_only)


@plugin.command
@lightbulb.command("kill", "Kills the bot.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def kill_command(ctx: lightbulb.Context):
    await ctx.respond("Successfully killed the bot.")
    await plugin.bot.close()


@plugin.command
@lightbulb.command("ping", "Kills the bot.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def ping_command(ctx: lightbulb.Context):
    await ctx.respond("Pong!")


@plugin.command
@lightbulb.option("file_name", "file name", str)
@lightbulb.command("reload", "Reloads an extension.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def reload_extensions_command(ctx: lightbulb.Context):
    try:
        plugin.bot.unload_extensions(f"components." + ctx.options.file_name)
        plugin.bot.load_extensions(f"components." + ctx.options.file_name)
        await ctx.respond(f"Reloaded `{ctx.options.file_name}`")

    except lightbulb.errors.ExtensionAlreadyLoaded:
        await ctx.respond(f"`{ctx.options.file_name}` is already loaded!")

    except lightbulb.errors.ExtensionNotFound:
        await ctx.respond(f"`{ctx.options.file_name}` does not exist!")

    except Exception as e:
        embed = hikari.Embed(title="An error has occurred!", description=f"```python\n{repr(e)}\n```")
        await ctx.respond(embed=embed)


@plugin.command
@lightbulb.option("file_name", "file name", str)
@lightbulb.command("load", "Loads an extension.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def load_extensions_command(ctx: lightbulb.Context):
    try:
        plugin.bot.load_extensions(f"components." + ctx.options.file_name)
        await ctx.respond(f"Loaded `{ctx.options.file_name}`")

    except lightbulb.errors.ExtensionAlreadyLoaded:
        await ctx.respond(f"`{ctx.options.file_name}` is already loaded!")

    except lightbulb.errors.ExtensionNotFound:
        await ctx.respond(f"`{ctx.options.file_name}` does not exist!")

    except Exception as e:
        embed = hikari.Embed(title="An error has occurred!", description=f"```python\n{repr(e)}\n```")
        await ctx.respond(embed=embed)


@plugin.command
@lightbulb.option("file_name", "file name", str)
@lightbulb.command("unload", "Unloads an extension.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def unload_extensions_command(ctx: lightbulb.Context):
    try:
        plugin.bot.unload_extensions(f"components." + ctx.options.file_name)
        await ctx.respond(f"Unloaded `{ctx.options.file_name}`")

    except lightbulb.errors.ExtensionNotLoaded:
        await ctx.respond(f"`{ctx.options.file_name}` is not loaded yet!")

    except lightbulb.errors.ExtensionNotFound:
        await ctx.respond(f"`{ctx.options.file_name}` does not exist!")

    except Exception as e:
        embed = hikari.Embed(title="An error has occurred!", description=f"```python\n{repr(e)}\n```")
        await ctx.respond(embed=embed)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
