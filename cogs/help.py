import discord
from core import Paginator
from discord.ext import commands


class Help(commands.Cog, name="Help"):
	def __init__(self, client):
		self.client = client
		self.FOOTER = self.client.config.FOOTER_TEXT
		self.commands = [c for c in self.client.walk_commands()]
		self.exceptions = ("owner", "help", "jishaku")
		self.allowed_cogs = self.client.config.ALLOWED_COGS
		self.cogs_commands = {
			cog.lower(): [c for c in self.commands if c.cog_name is not None and c.cog_name.lower() == cog.lower()]
			for cog in self.client.cogs
			if cog.lower() not in self.exceptions
		}

	def get_cog_commands(self, cog: str) -> list:
		return self.cogs_commands[cog.lower()]

	async def build_help_by_cog(self, ctx, prefix: str, cog_name: str) -> discord.Embed:
		commands_string = ""
		for command in self.get_cog_commands(cog_name):
			try:
				if await command.can_run(ctx):
					commands_string += f"`{prefix}{command}` {command.description}\n"
			except commands.CommandError:
				pass

		if not commands_string:
			commands_string = "Вы не можете использовать ни одну из команд этой категории"

		return discord.Embed(
			title=f"Категория команд: {cog_name.capitalize()} - {prefix}help {cog_name.lower()}",
			description=commands_string,
			colour=discord.Color.green()
		).set_author(
			name=self.client.user.name,
			icon_url=self.client.user.avatar_url
		).set_footer(
			text=f"Вызвал: {ctx.author.name}",
			icon_url=ctx.author.avatar_url
		)

	async def build_help(self, ctx, prefix: str) -> list:
		emb = discord.Embed(
			title="**Доступные команды:**",
			description=f'Префикс на этом сервере - `{prefix}`. Показаны только те команды которые вы можете выполнить',
			colour=discord.Color.green()
		)
		emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
		emb.set_footer(text=f"Вызвал: {ctx.author.name}", icon_url=ctx.author.avatar_url)

		embeds = [emb]
		for cog_name in self.client.cogs:
			if cog_name.lower() in self.exceptions or cog_name not in self.allowed_cogs:
				continue

			embeds.append(await self.build_help_by_cog(ctx, prefix, cog_name))

		return embeds

	@commands.command(
		help="**Примеры использования:**\n1. {Prefix}help\n2. {Prefix}help moderate\n2. {Prefix}help ban\n\n**Пример 1:** Показывает список всех команд бота\n**Пример 2:** Показывает список всех указаной групы\n**Пример 3:** Показывает документацию по указаной команде"
	)
	async def help(self, ctx, *, entity: str = None):
		prefix = str(await self.client.database.get_prefix(guild=ctx.guild))
		cogs_aliases = {
			"economy": "Economy",
			"funeditimage": "FunEditImage",
			"funother": "FunOther",
			"funrandomimage": "FunRandomImage",
			"clans": "Clans",
			"different": "Different",
			"moderate": "Moderate",
			"settings": "Settings",
			"utils": "Utils",
			"works": "Works",
			"showconfigs": "ShowConfigs",
			"giveaways": "Giveaways",
			"information": "Information",
			"reminders": "Reminders"
		}

		if entity is None:
			embeds = await self.build_help(ctx, prefix)
			message = await ctx.send(embed=embeds[0])
			paginator = Paginator(ctx, message, embeds, footer=False)
			await paginator.start()
			return

		if entity.lower() not in cogs_aliases.keys():
			if entity.lower() not in [c.name for c in self.commands]:
				str_cogs = ", ".join([
					cogs_aliases[cog.lower()] for cog in self.client.cogs
					if cog.lower() in cogs_aliases.keys()
				])
				emb = discord.Embed(
					title="Ошибка!",
					description=f"Такой категории нет, введите названия правильно. Список доступных категорий: {str_cogs}",
					colour=discord.Color.green(),
				)
				emb.set_author(
					name=self.client.user.name, icon_url=self.client.user.avatar_url
				)
				emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
				await ctx.send(embed=emb)
				return
			else:
				aliases = (
					f"""Алиасы команды: {', '.join(self.client.get_command(entity.lower()).aliases)}\n\n"""
					if self.client.get_command(entity.lower()).aliases != []
					else ""
				)
				emb = discord.Embed(
					title=f"Команда: {prefix+entity.lower()}",
					description=aliases
					+ self.client.get_command(entity.lower()).help.format(
						Prefix=prefix
					),
					colour=discord.Color.green(),
				)
				emb.set_author(
					name=self.client.user.name, icon_url=self.client.user.avatar_url
				)
				emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
				await ctx.send(embed=emb)
				return

		await ctx.send(embed=await self.build_help_by_cog(ctx, prefix, entity))


def setup(client):
	client.add_cog(Help(client))
