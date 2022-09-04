import hikari
import lightbulb
import random
from Database import Database
import miru
from components.error_handler import OutOfBoundError, BarrierTraverseError

plugin = lightbulb.Plugin("Field")
plugin.add_checks(lightbulb.checks.has_guild_permissions(hikari.Permissions.ADMINISTRATOR))


class Field:
    def __init__(self, size_x: int, size_y: int, buff_tile: int, level: int):
        self.text = None
        self.size_x = size_x
        self.size_y = size_y
        self.start_x = 1
        self.start_y = 1
        self.exit_x = self.size_x
        self.exit_y = self.size_y
        self.boss_coordinates = [(self.size_x, self.size_y)]
        self.barrier_coordinates = [(self.exit_x, self.exit_y - 1), (self.exit_x - 1, self.exit_y - 1)]
        self.buff_tile = buff_tile
        self.level = level
        self.field_text = ''
        self.description = ''
        self.event_description = f"Started a new game. You're currently at level {self.level}!"
        self.field = None
        self.buff_coordinates = self.generate_event_tiles()
        self.boss_fight_state = False

    def generate_event_tiles(self):
        """ This sets the coordinates of the event buffs in the field. """
        buff_tiles = []
        while True:
            x, y = random.choice(range(1, self.size_x)), random.choice(range(1, self.size_y))
            if (x, y) in [(1, 1), self.boss_coordinates[0]] + self.barrier_coordinates:
                continue
            if (x, y) in buff_tiles:
                continue
            buff_tiles.append((x, y))

            # Breaks when all the buff tiles are already generated for current level field without modifying the buff tile values.
            if len(buff_tiles) == self.buff_tile:
                break
        self.buff_coordinates = buff_tiles
        return buff_tiles

    async def generate_field(self):
        """
        This first populates the entire x * y field with trees.
        Then it replaces trees in the event coordinates with their respective event.
        """
        self.field = []
        for _ in range(self.size_y):
            self.field.append(['🌴' for _ in range(self.size_x)])

        await self.check_event()

        try:
            if not self.size_y >= self.start_y > 0:
                raise IndexError
            if not self.size_x >= self.start_x > 0:
                raise IndexError

            self.field[-self.exit_y][self.exit_x - 1] = '🕳️'
            self.field[-self.start_y][self.start_x - 1] = '<:cute:664406344824258560>'

            if self.buff_coordinates:
                for x, y in self.buff_coordinates:
                    self.field[-y][x - 1] = '<a:gold:907835366726336543>'
            if self.boss_coordinates:
                for x, y in self.boss_coordinates:
                    self.field[-y][x - 1] = '🐭'
                self.field[-(self.exit_y - 1)][self.exit_x - 1] = '⛰️'
                self.field[-(self.exit_y - 1)][self.exit_x - 2] = '⛰️'

        except IndexError:
            raise IndexError("Starting coordinate should be within the x & y field boundaries.")

        self.field_text = ''
        for i in self.field:
            self.field_text += f"{' '.join(i)}\n"
        await self.text_generator()

    async def text_generator(self):
        self.text = ''
        if self.event_description:
            self.text += f'> **{self.event_description}**\n'
            self.event_description = ''
        self.text += f'> {self.description}\n' if self.description else ''

    async def move(self, delta_x: int = 0, delta_y: int = 0):
        self.start_x += delta_x
        self.start_y += delta_y

    async def move_validation(self, before_x: int, before_y: int, suffix: str):
        try:
            await self.check_out_of_bound(before_x, before_y)
            await self.check_exit()
            self.description = f"You've moved {suffix}."

        except OutOfBoundError:
            self.description = "**You're not allowed to travel out of the map!**"

        except BarrierTraverseError:
            self.description = "**You're not allowed to travel through the barriers!**"
        await self.generate_field()

    async def move_left(self):
        before_x, before_y = self.start_x, self.start_y
        await self.move(delta_x=-1)
        await self.move_validation(before_x, before_y, "left")

    async def move_right(self):
        before_x, before_y = self.start_x, self.start_y
        await self.move(delta_x=1)
        await self.move_validation(before_x, before_y, "right")

    async def move_up(self):
        before_x, before_y = self.start_x, self.start_y
        await self.move(delta_y=1)
        await self.move_validation(before_x, before_y, "up")

    async def move_down(self):
        before_x, before_y = self.start_x, self.start_y
        await self.move(delta_y=-1)
        await self.move_validation(before_x, before_y, "down")

    async def check_out_of_bound(self, before_x: int, before_y: int):
        if self.size_y < self.start_y or self.start_y <= 0 or self.size_x < self.start_x or self.start_x <= 0:
            # Revert to original position if they're out of bound
            self.start_x, self.start_y = before_x, before_y
            raise OutOfBoundError

        if (self.start_x, self.start_y) in self.barrier_coordinates:
            # Revert to original position if they're attempting to traverse through the barrier
            self.start_x, self.start_y = before_x, before_y
            raise BarrierTraverseError
        return True

    async def check_exit(self):
        """
        Checks if you've moved to the next level, if so, restart from the starting coordinates (1, 1)
        and regenerates a new level field.
        """
        if self.start_x == self.exit_x and self.start_y == self.exit_y:
            self.level += 1
            self.start_x = 1
            self.start_y = 1
            self.event_description = f"**You're now at level {self.level:,}!**"
            self.generate_event_tiles()

    async def boss_encounter(self):
        if self.start_x == self.exit_x and self.start_y == self.exit_y:
            self.boss_fight_state = True

    async def check_event(self):
        if (self.start_x, self.start_y) in self.buff_coordinates:
            self.buff_coordinates.remove((self.start_x, self.start_y))
            self.event_description = f"You've triggered a buff event."
        if self.start_y == self.size_y and self.start_x == self.size_x:
            self.boss_coordinates.remove((self.size_x, self.size_y))
            self.event_description = f"You've triggered a boss event."


class View(miru.View):
    def __init__(self, lb_ctx: lightbulb.Context, field: Field):
        self.lb_ctx = lb_ctx
        self.value = None
        self.field = field
        self.ctx: miru.Context = None
        super().__init__(timeout=300)

    async def view_check(self, ctx: miru.Context) -> bool:
        self.ctx = ctx
        return self.lb_ctx.author == ctx.user

    async def on_timeout(self) -> None:
        i = 0
        for button in self.children:
            if not i:
                button.emoji = "❎"
                button.label = "Timed Out"
                button.style = hikari.ButtonStyle.DANGER
                button.disabled = True
                i += 1
                continue
            self.remove_item(button)
            await self.ctx.edit_response(content="Game has timed out. Please restart the command.", components=[])

    @miru.button(style=hikari.ButtonStyle.SECONDARY, emoji=hikari.Emoji.parse("<:432536324252:960939610098249820>"),
                 row=1)
    async def top_left_health_potion_button(self, button: miru.Button, ctx: miru.Context) -> None:
        pass

    @miru.button(style=hikari.ButtonStyle.PRIMARY, emoji="🔼", row=1)
    async def up_button(self, button: miru.Button, ctx: miru.Context) -> None:
        await self.field.move_up()
        embed = hikari.Embed(description=self.field.field_text)
        embed.set_footer(text=f"Played by {self.lb_ctx.author}", icon=str(self.lb_ctx.author.display_avatar_url))
        await ctx.edit_response(content=self.field.text, embed=embed, components=self.build(),
                                flags=hikari.MessageFlag.EPHEMERAL)

    @miru.button(style=hikari.ButtonStyle.SECONDARY,
                 emoji=hikari.Emoji.parse("<a:927159465332051998:960935542491586570>"), row=1)
    async def top_right_stamina_potion_button(self, button: miru.Button, ctx: miru.Context) -> None:
        pass

    @miru.button(style=hikari.ButtonStyle.PRIMARY, emoji="◀", row=2)
    async def left_button(self, button: miru.Button, ctx: miru.Context) -> None:
        await self.field.move_left()
        embed = hikari.Embed(description=self.field.field_text)
        embed.set_footer(text=f"Played by {self.lb_ctx.author}", icon=str(self.lb_ctx.author.display_avatar_url))
        await ctx.edit_response(content=self.field.text, embed=embed, components=self.build(),
                                flags=hikari.MessageFlag.EPHEMERAL)

    @miru.button(style=hikari.ButtonStyle.SECONDARY, emoji=hikari.Emoji.parse("<a:Attack:769715971421896734>"), row=2)
    async def middle_attack_button(self, button: miru.Button, ctx: miru.Context) -> None:
        pass

    @miru.button(style=hikari.ButtonStyle.PRIMARY, emoji="▶", row=2)
    async def right_button(self, button: miru.Button, ctx: miru.Context) -> None:
        await self.field.move_right()
        embed = hikari.Embed(description=self.field.field_text)
        embed.set_footer(text=f"Played by {self.lb_ctx.author}", icon=str(self.lb_ctx.author.display_avatar_url))
        await ctx.edit_response(content=self.field.text, embed=embed, components=self.build(),
                                flags=hikari.MessageFlag.EPHEMERAL)

    @miru.button(style=hikari.ButtonStyle.SECONDARY, emoji=hikari.Emoji.parse("<a:kleeRun:861497168112517150>"), row=3)
    async def bottom_left_retreat_button(self, button: miru.Button, ctx: miru.Context) -> None:
        pass

    @miru.button(style=hikari.ButtonStyle.PRIMARY, emoji="🔽", row=3)
    async def down_button(self, button: miru.Button, ctx: miru.Context) -> None:
        await self.field.move_down()
        embed = hikari.Embed(description=self.field.field_text)
        embed.set_footer(text=f"Played by {self.lb_ctx.author}", icon=str(self.lb_ctx.author.display_avatar_url))
        await ctx.edit_response(content=self.field.text, embed=embed, components=self.build(),
                                flags=hikari.MessageFlag.EPHEMERAL)

    @miru.button(style=hikari.ButtonStyle.SECONDARY,
                 emoji=hikari.Emoji.parse("<a:857039592074117120:960935540558028850>"), row=3)
    async def bottom_right_buff_button(self, button: miru.Button, ctx: miru.Context) -> None:
        pass


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
