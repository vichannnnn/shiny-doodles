from abc import ABC
import lightbulb
import yaml
import hikari
from os import listdir
from os.path import abspath
import miru
from lightbulb.ext import tasks

with open("authentication.yaml", "r", encoding="utf8") as stream:
    yaml_data = yaml.safe_load(stream)

test_guilds = (
    948311226159624254,
    660135595250810881,
    976107813900267565,
    990477516802232352,
)


class Yuna(lightbulb.BotApp, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def load_configuration(self):
        self.load_all_extensions()

    def load_all_extensions(self):
        for file in listdir(abspath("components/")):
            if file != "__pycache__":
                if file.endswith(".py"):
                    file = "components." + file[:-3]
                    self.load_extensions(file)
                    print(f"Successfully loaded {file}")

                else:
                    for script in listdir(abspath(f"components/{file}/")):
                        if script != "__pycache__":
                            if script.endswith(".py"):
                                loading_file = f"components.{file}." + script[:-3]
                                self.load_extensions(loading_file)
                                print(f"Successfully loaded {loading_file}")

    def load_tasks(self):
        tasks.load(self)


intents = hikari.Intents.GUILD_MEMBERS | hikari.Intents.ALL_UNPRIVILEGED


def main():
    instance = Yuna(
        token=yaml_data["Token"],
        help_class=None,
        prefix=lightbulb.when_mentioned_or(None),
        intents=intents,
        default_enabled_guilds=test_guilds,
    )
    miru.load(instance)

    @instance.listen(lightbulb.LightbulbStartedEvent)
    async def on_ready(event: lightbulb.LightbulbStartedEvent) -> None:
        print(f"Hikari Version: {hikari.__version__}")
        print(f"Lightbulb Version: {lightbulb.__version__}")
        print(f"Miru Version: {miru.__version__}")

        guilds = instance.rest.fetch_my_guilds()
        print(
            f"{instance.get_me().username} ({instance.get_me().id}) successfully started."
        )
        print(f"Currently in {await guilds.count()} guilds.")

    instance.load_tasks()
    instance.load_configuration()
    instance.run(
        asyncio_debug=True,
        activity=hikari.Activity(
            name=f"Testing CI Pipeline...",
            type=hikari.ActivityType.WATCHING,
        ),
    )


main()
