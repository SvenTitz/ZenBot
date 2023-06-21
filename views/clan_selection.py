import discord
from helpers import db_manager


class ClanSelector(discord.ui.Select):
    def __init__(self, clans: list, select_callback, **kwargs):
        self.cb = select_callback
        self.kwargs = kwargs
        options = []
        for clan in clans:
            options.append(
                discord.SelectOption(
                    label=clan[1], description=clan[0], emoji=clan[2], value=clan[0]
                )
            )

        super().__init__(
            placeholder="Choose a clan...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        await self.cb(self.values[0], interaction, **self.kwargs)


class ClanSelectorView(discord.ui.View):
    def __init__(self, clans: list, select_callback, **kwargs):
        super().__init__()
        self.add_item(ClanSelector(clans, select_callback, **kwargs))
