import hikari
import lightbulb
import random
from components.field_handler import View, Field


plugin = lightbulb.Plugin("Admin Commands")


async def embed_creator(ctx: lightbulb.Context, title: str, description: str):
    colour = random.randint(0x0, 0xFFFFFF)
    embed = hikari.Embed(title=title, description=description, colour=hikari.Colour(colour))
    embed.set_footer(text=f"Command used by {ctx.author}", icon=ctx.author.display_avatar_url)
    return await ctx.respond(embed=embed)


@plugin.command()
@lightbulb.command("start", "Button to press on.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def adventure_test(ctx: lightbulb.Context) -> None:

    field_object = Field(12, 12, 15, 3)
    await field_object.generate_field()
    view = View(ctx, field_object)
    embed = hikari.Embed(description=field_object.field_text)
    embed.set_footer(text=f"Played by {ctx.author}", icon=str(ctx.author.display_avatar_url))
    proxy = await ctx.respond(content=field_object.text, embed=embed, components=view.build())
    message = await proxy.message()
    view.start(message)  # Start listening for interactions


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
