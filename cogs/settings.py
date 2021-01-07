import discord
import json
import typing
from discord.ext import commands


class Settings(commands.Cog, name="Settings"):
	def __init__(self, client):
		self.client = client
		self.FOOTER = self.client.config.FOOTER_TEXT

	@commands.group(
		help=f"""**Команды групы:** time-delete-channel, shop-role, exp-multi, text-channels-category, set-audit, idea-channel, max-warns, prefix, anti-flud, react-commands, moderation-role, ignore-channels, custom-command, auto-reactions, auto-responder\n\n"""
	)
	@commands.has_permissions(administrator=True)
	async def setting(self, ctx):
		pass

	@setting.command(
		hidden=True,
		description="**Настройка префикса**",
		usage="setting prefix [Новый префикс]",
	)
	async def prefix(self, ctx, prefix: str):
		if len(prefix) > 3:
			emb = discord.Embed(
				title="Ошибка!",
				description=f"**Количество символов в новом префиксе не должно превышать 3-х!**",
				colour=discord.Color.green(),
			)
			emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
			emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
			await ctx.send(embed=emb)
			return

		sql = """UPDATE guilds SET prefix = %s WHERE guild_id = %s AND guild_id = %s"""
		val = (prefix, ctx.guild.id, ctx.guild.id)

		await self.client.database.execute(sql, val)

		emb = discord.Embed(
			description=f"**Вы успешно изменили префикс бота на этом сервере. Новый префикс {prefix}**",
			colour=discord.Color.green(),
		)
		emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
		emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
		await ctx.send(embed=emb)

	@setting.command(
		hidden=True,
		aliases=["moder-role"],
		name="moderation-role",
		description="**Настройка ролей модераторов**",
		usage="setting moderation-role [add(Добавляет указаную роль)/clear(Очищает список)/del(Удаляет указаную роль)] |@Роль|",
	)
	async def moder_role(self, ctx, type_act: str, role: discord.Role = None):
		data = await self.client.database.sel_guild(guild=ctx.guild)
		cur_roles = data["moder_roles"]

		if type_act == "add":
			if role is None:
				emb = await self.client.utils.create_error_embed(ctx, "Укажите добавляемую роль!")
				await ctx.send(embed=emb)
				return

			cur_roles.append(role.id)
			emb = discord.Embed(
				description=f"**Вы успешно добавили новую роль модератора! Добавленная роль - `{role.name}`**",
				colour=discord.Color.green(),
			)
			emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
			emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
			await ctx.send(embed=emb)
		elif type_act == "clear":
			cur_roles = []
			emb = discord.Embed(
				description=f"**Вы успешно очистили список ролей модераторов!**",
				colour=discord.Color.green(),
			)
			emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
			emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
			await ctx.send(embed=emb)
		elif type_act == "delete":
			if role is None:
				emb = await self.client.utils.create_error_embed(ctx, "Укажите удаляемую роль!")
				await ctx.send(embed=emb)
				return

			try:
				cur_roles.remove(role.id)
			except ValueError:
				emb = discord.Embed(
					title="Ошибка!",
					description=f"**Такой роли нету в списке ролей модераторов!**",
					colour=discord.Color.green(),
				)
				emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
				emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
				await ctx.send(embed=emb)
				return

			emb = discord.Embed(
				description=f"**Вы успешно удалили роль из ролей модераторов! Удалённая роль - `{role.name}`**",
				colour=discord.Color.green(),
			)
			emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
			emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
			await ctx.send(embed=emb)
		else:
			emb = discord.Embed(
				title="Ошибка!",
				description=f"**Укажите одно из этих действий: clear, delete, add!**",
				colour=discord.Color.green(),
			)
			emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
			emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
			await ctx.send(embed=emb)
			return

		sql = """UPDATE guilds SET moderators = %s WHERE guild_id = %s AND guild_id = %s"""
		val = (json.dumps(cur_roles), ctx.guild.id, ctx.guild.id)

		await self.client.database.execute(sql, val)

	@setting.command(
		hidden=True,
		name="ignore-channels",
		description="**Игнорируемые каналы в системе уровней**",
		usage="setting ignore-channels [Действие, add - добавляет канал в исключения, clear - очищает список исключений, delete - удаляет указаный канал из списка] [Id канала]",
	)
	async def ignoredchannels(self, ctx, typech: str, channel: discord.TextChannel = None):
		data = await self.client.database.sel_guild(guild=ctx.guild)
		cur_ignchannel = data["ignored_channels"]

		if typech == "add":
			if channel is None:
				emb = await self.client.utils.create_error_embed(ctx, "Укажите добавляемый канал!")
				await ctx.send(embed=emb)
				return

			cur_ignchannel.append(channel.id)
			emb = discord.Embed(
				description=f"**Вы успешно добавили новий канал в исключения! Добавлённый канал - {channel.mention}**",
				colour=discord.Color.green(),
			)
			emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
			emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
			await ctx.send(embed=emb)
		elif typech == "clear":
			cur_ignchannel = []
			emb = discord.Embed(
				description=f"**Вы успешно очистили список исключенных каналов!**",
				colour=discord.Color.green(),
			)
			emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
			emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
			await ctx.send(embed=emb)
		elif typech == "delete":
			if channel is None:
				emb = await self.client.utils.create_error_embed(ctx, "Укажите удаляемый канал!")
				await ctx.send(embed=emb)
				return

			try:
				cur_ignchannel.remove(channel.id)
			except ValueError:
				emb = discord.Embed(
					title="Ошибка!",
					description=f"**Такого канала нету в списке игнорируемых каналов!**",
					colour=discord.Color.green(),
				)
				emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
				emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
				await ctx.send(embed=emb)
				return

			emb = discord.Embed(
				description=f"**Вы успешно удалили канал из исключений! Удалённый канал - {channel.mention}**",
				colour=discord.Color.green(),
			)
			emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
			emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
			await ctx.send(embed=emb)
		else:
			emb = discord.Embed(
				title="Ошибка!",
				description=f"**Вы не правильно указали действие!**",
				colour=discord.Color.green(),
			)
			emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
			emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
			await ctx.send(embed=emb)
			return

		sql = """UPDATE guilds SET ignored_channels = %s WHERE guild_id = %s AND guild_id = %s"""
		val = (json.dumps(cur_ignchannel), ctx.guild.id, ctx.guild.id)

		await self.client.database.execute(sql, val)

	@setting.command(
		hidden=True,
		name="shop-role",
		description="**Настройка магазина на сервере**",
		usage="setting shop-role [clear - очищает список ролей, add - добавляет роль, delete - удаляет роль] [@Роль] [Стоимость роли]",
	)
	async def shoplist(
		self, ctx, cl_add: typing.Optional[str], role: discord.Role, cost: int
	):
		data = await self.client.database.sel_guild(guild=ctx.guild)
		shoplist = data["shop_list"]

		if cost <= 0:
			emb = await self.client.create_error_embed(ctx, "Укажите стоимость предмета больше 0!")
			await ctx.send(embed=emb)
			return

		if cl_add == "add":
			shoplist.append([role.id, cost])
			emb = discord.Embed(
				description=f"**Добавленна новая роль - `{role}`, стоимость - `{cost}`**",
				colour=discord.Color.green(),
			)
			emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
			emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
			await ctx.send(embed=emb)
		elif cl_add == "clear":
			shoplist = []
			emb = discord.Embed(
				description=f"**Ваш список продаваемых ролей успешно очищен**",
				colour=discord.Color.green(),
			)
			emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
			emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
			await ctx.send(embed=emb)
		elif cl_add == "delete" or cl_add == "remove" or cl_add == "del":
			try:
				for shop_role in shoplist:
					if role.id in shop_role and cost in shop_role:
						shoplist.remove(shop_role)
			except:
				emb = discord.Embed(
					title="Ошибка!",
					description=f"**Такой роли не существует в списке продаваемых ролей!**",
					colour=discord.Color.green(),
				)
				emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
				emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
				await ctx.send(embed=emb)
				return

			emb = discord.Embed(
				description=f"**Вы успешно удалили продаваемую роль из списка продаваемых ролей! Удалённая роль - `{role}`**",
				colour=discord.Color.green(),
			)
			emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
			emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
			await ctx.send(embed=emb)
		elif cl_add != "clear" and cl_add != "add":
			emb = await self.client.utils.create_error_embed(
				ctx, "**Укажите одно из этих действий: add, clear, delete!**",
			)
			await ctx.send(embed=emb)

		sql = (
			"""UPDATE guilds SET shop_list = %s WHERE guild_id = %s AND guild_id = %s"""
		)
		val = (json.dumps(shoplist), ctx.guild.id, ctx.guild.id)

		await self.client.database.execute(sql, val)

	@setting.command(
		hidden=True,
		name="text-channels-category",
		description="**Настройка категории приватных текстовых каналов**",
		usage="setting text-channels-category [Id категории]",
	)
	async def privatetextcategory(self, ctx, category: discord.CategoryChannel):
		sql = """UPDATE guilds SET textchannels_category = %s WHERE guild_id = %s AND guild_id = %s"""
		val = (category.id, ctx.guild.id, ctx.guild.id)

		await self.client.database.execute(sql, val)

		emb = discord.Embed(
			description=f"**Вы успешно настроили категорию для приватних текстовых каналов! Новая категория - {category.name}**",
			colour=discord.Color.green(),
		)
		emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
		emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
		await ctx.send(embed=emb)

	@setting.command(
		hidden=True,
		name="max-warns",
		description="**Настройка максимального количества предупрежденний**",
		usage="setting max-warns [Любое число]",
	)
	async def maxwarns(self, ctx, number: int):
		if number <= 0:
			emb = await self.client.utils.create_error_embed(ctx, "Укажите максимальное количество предупреждений больше 0!")
			await ctx.send(embed=emb)
			return

		if number >= 25:
			emb = discord.Embed(
				title="Ошибка!",
				description=f"**Вы указали слишком большой лимит предупреждений!**",
				colour=discord.Color.green(),
			)
			emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
			emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
			await ctx.send(embed=emb)
			await ctx.message.add_reaction("❌")
			return

		sql = (
			"""UPDATE guilds SET max_warns = %s WHERE guild_id = %s AND guild_id = %s"""
		)
		val = (number, ctx.guild.id, ctx.guild.id)

		await self.client.database.execute(sql, val)

		emb = discord.Embed(
			description=f"**Вы успешно настроили максимальное количество предупрежденний! Новое значения - `{number}`**",
			colour=discord.Color.green(),
		)
		emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
		emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
		await ctx.send(embed=emb)

	@setting.command(
		hidden=True,
		name="anti-flud",
		description="**Настройка анти-флуда(Бета-тест)**",
		usage="setting anti-flud [on/off]",
	)
	async def anti_flud(self, ctx, action: str):
		actions = ["on", "off", "true", "false", "0", "1"]
		if action.lower() not in actions:
			emb = discord.Embed(
				title="Ошибка!",
				description=f"**Вы не правильно указали действие! Укажите из этих вариантов: on(Вкл.), off(Выкл.), true(Вкл.), false(Выкл.), 0(Вкл.), 1(Выкл.)**",
				colour=discord.Color.green(),
			)
			emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
			emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
			await ctx.send(embed=emb)
			await ctx.message.add_reaction("❌")
			return

		data = await self.client.database.sel_guild(guild=ctx.guild)
		emb = discord.Embed(
			description=f"**Настройки анти-флуда успешно обновленны!**",
			colour=discord.Color.green(),
		)
		emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
		emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
		await ctx.send(embed=emb)

		if action.lower() == "on" or action.lower() == "true" or action.lower() == "1":
			action = True
		elif (
			action.lower() == "off"
			or action.lower() == "false"
			or action.lower() == "0"
		):
			action = False

		settings = data["auto_mod"]
		settings.update({"anti_flud": action})

		sql = (
			"""UPDATE guilds SET auto_mod = %s WHERE guild_id = %s AND guild_id = %s"""
		)
		val = (json.dumps(settings), ctx.guild.id, ctx.guild.id)

		await self.client.database.execute(sql, val)

	@setting.command(
		hidden=True,
		name="react-commands",
		description="**Настройка команд по реакциям**",
		usage="setting react-commands [on/off]",
	)
	async def react_commands(self, ctx, action: str):
		actions = ["on", "off", "true", "false", "0", "1"]
		if action.lower() not in actions:
			emb = discord.Embed(
				title="Ошибка!",
				description=f"**Вы не правильно указали действие! Укажите из этих вариантов: on(Вкл.), off(Выкл.), true(Вкл.), false(Выкл.), 0(Вкл.), 1(Выкл.)**",
				colour=discord.Color.green(),
			)
			emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
			emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
			await ctx.send(embed=emb)
			await ctx.message.add_reaction("❌")
			return

		data = await self.client.database.sel_guild(guild=ctx.guild)
		emb = discord.Embed(
			description=f"**Настройки команд по реакциям успешно обновленны!**",
			colour=discord.Color.green(),
		)
		emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
		emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
		await ctx.send(embed=emb)

		if action.lower() == "on" or action.lower() == "true" or action.lower() == "1":
			action = True
		elif (
			action.lower() == "off"
			or action.lower() == "false"
			or action.lower() == "0"
		):
			action = False

		settings = data["auto_mod"]
		settings.update({"react_commands": action})

		sql = (
			"""UPDATE guilds SET auto_mod = %s WHERE guild_id = %s AND guild_id = %s"""
		)
		val = (json.dumps(settings), ctx.guild.id, ctx.guild.id)

		await self.client.database.execute(sql, val)

	@setting.command(
		hidden=True,
		name="idea-channel",
		description="**Настройка канала идей сервера**",
		usage="setting idea-channel [Id канала]",
	)
	async def ideachannel(self, ctx, channel: discord.TextChannel):
		sql = """UPDATE guilds SET idea_channel = %s WHERE guild_id = %s AND guild_id = %s"""
		val = (channel.id, ctx.guild.id, ctx.guild.id)

		await self.client.database.execute(sql, val)

		emb = discord.Embed(
			description=f"**Вы успешно настроили канал идей! Новий канал - {channel.name}**",
			colour=discord.Color.green(),
		)
		emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
		emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
		await ctx.send(embed=emb)

	@setting.command(
		hidden=True,
		name="time-delete-channel",
		description="**Через сколько минут будет удалять приватный текстовый канал**",
		usage="setting time-delete-channel [Любое число]",
	)
	async def timetextchannel(self, ctx, time: int):
		if time <= 0:
			emb = await self.client.create_error_embed(ctx, "Укажите время удаления приватных текстовых каналов больше 0!")
			await ctx.send(embed=emb)
			return

		sql = """UPDATE guilds SET timedelete_textchannel = %s WHERE guild_id = %s AND guild_id = %s"""
		val = (time, ctx.guild.id, ctx.guild.id)

		await self.client.database.execute(sql, val)

		emb = discord.Embed(
			description=f"**Вы успешно изменили значения! Новая длительность на удаления приватного текстового - {time}**",
			colour=discord.Color.green(),
		)
		emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
		emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
		await ctx.send(embed=emb)

	@setting.command(
		hidden=True,
		name="exp-multi",
		aliases=["exp-multiplier"],
		description="**Настройка множителя опыта на сервере**",
		usage="setting exp-multi [Множитель%(Пример - 450%)]",
	)
	async def expform(self, ctx, multiplier: str):
		multi = int(multiplier[:-1])
		if multi > 10000 or multi <= 0:
			emb = discord.Embed(
				title="Ошибка!",
				description="Укажите множитель опыта в диапазоне от 1% до 10000%",
				colour=discord.Color.green(),
			)
			emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
			emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
			await ctx.send(embed=emb)
			await ctx.message.add_reaction("❌")
			return

		form = float(multi / 100)
		sql = (
			"""UPDATE guilds SET exp_multi = %s WHERE guild_id = %s AND guild_id = %s"""
		)
		val = (form, ctx.guild.id, ctx.guild.id)

		await self.client.database.execute(sql, val)

		emb = discord.Embed(
			description=f"**Вы успешно настроили множитель опыта, {multiplier}**",
			colour=discord.Color.green(),
		)
		emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
		emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
		await ctx.send(embed=emb)

	@setting.command(
		hidden=True,
		name="set-audit",
		aliases=["setaudit"],
		description="**Настройка канала аудита**",
		usage="setting logs [on/off] [Категория] [Канал]",
	)
	async def set_audit(self, ctx, action: str, category: str, channel: discord.TextChannel):
		if channel in ("off", "-", "0"):
			sql = """UPDATE guilds SET log_channel = %s WHERE guild_id = %s"""
			val = (0, ctx.guild.id)
			await self.client.database.execute(sql, val)
			await ctx.message.add_reaction("✅")
			return

		sql = """UPDATE guilds SET log_channel = %s WHERE guild_id = %s"""
		val = (channel.id, ctx.guild.id)
		await self.client.database.execute(sql, val)
		await ctx.message.add_reaction("✅")

	@setting.command(
		hidden=True,
		name="auto-reactions",
		aliases=["autoreactions"],
		description="**Настройка авто-реакций**",
		usage="setting auto-reactions [set/off] |Канал| |Эмодзи|",
	)
	async def auto_reactions(self, ctx, action: str, channel: typing.Optional[discord.TextChannel], *, reactions: str = None):
		auto_reactions = (await self.client.database.sel_guild(guild=ctx.guild))["auto_reactions"]
		if action.lower() == "set":
			if reactions is None:
				emb = await self.client.utils.create_error_embed(
					ctx, "Укажите эмодзи!"
				)
				await ctx.send(embed=emb)
				return

			if channel is None:
				channel = ctx.channel

			emojis = [emoji for emoji in reactions.split(" ") if emoji]
			auto_reactions.update({channel.id: emojis})
			await self.client.database.execute(
				"""UPDATE guilds SET auto_reactions = %s WHERE guild_id = %s""",
				(json.dumps(auto_reactions), ctx.guild.id)
			)
			await ctx.message.add_reaction("✅")
			return
		elif action.lower() == "off":
			if channel is None:
				channel = ctx.channel

			try:
				auto_reactions.pop(str(channel.id))
			except KeyError:
				emb = await self.client.utils.create_error_embed(
					ctx, "Для указаного канала авто-реакции не настроены!"
				)
				await ctx.send(embed=emb)
				return

			await self.client.database.execute(
				"""UPDATE guilds SET auto_reactions = %s WHERE guild_id = %s""",
				(json.dumps(auto_reactions), ctx.guild.id)
			)
			await ctx.message.add_reaction("✅")
			return
		else:
			emb = await self.client.utils.create_error_embed(
				ctx, "Укажите одно из этих действий: set, off"
			)
			await ctx.send(embed=emb)

	@setting.command(
		hidden=True,
		name="custom-command",
		aliases=["customcommand", "custom-commands", "customcommands"],
		description="**Настройка кастомных команд**",
		usage="setting custom-command [add/edit/delete/show/list] [Названия команды] |Код команды|",
	)
	async def custom_command(self, ctx, action: str, command_name: str = None, *, command_text: str = None):
		custom_commands = (await self.client.database.sel_guild(guild=ctx.guild))["custom_commands"]
		if action.lower() == "add":
			if command_name is None:
				emb = await self.client.utils.create_error_embed(
					ctx, "Укажите названия команды!"
				)
				await ctx.send(embed=emb)
				return

			if command_name in custom_commands.keys():
				emb = await self.client.utils.create_error_embed(
					ctx, "Указаная команда уже есть в списке команд!"
				)
				await ctx.send(embed=emb)
				return

			if command_text is None:
				emb = await self.client.utils.create_error_embed(
					ctx, "Укажите код к команде!"
				)
				await ctx.send(embed=emb)
				return

			if len(custom_commands.keys()) > 20:
				emb = await self.client.utils.create_error_embed(
					ctx, "Вы достигли ограничения(20 команд)!"
				)
				await ctx.send(embed=emb)
				return

			if len(command_text) > 1000:
				emb = await self.client.utils.create_error_embed(
					ctx, "Указаный код слишком большой(Максимум 1000 символов)!"
				)
				await ctx.send(embed=emb)
				return

			custom_commands.update({command_name: command_text})
			await self.client.database.execute(
				f"""UPDATE guilds SET custom_commands = %s WHERE guild_id = %s""",
				(json.dumps(custom_commands), ctx.guild.id)
			)

			emb = discord.Embed(
				description=f"**Успешно созданна новая команда - `{command_name}`**",
				colour=discord.Color.green(),
			)
			emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
			emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
			await ctx.send(embed=emb)
		elif action.lower() == "show":
			if command_name is None:
				emb = await self.client.utils.create_error_embed(
					ctx, "Укажите названия команды!"
				)
				await ctx.send(embed=emb)
				return

			if command_name not in custom_commands.keys():
				emb = await self.client.utils.create_error_embed(
					ctx, "Указаной команды не существует!"
				)
				await ctx.send(embed=emb)
				return

			emb = discord.Embed(
				title=f"Информация о кастомной команде - `{command_name}`",
				description=f"Код команды:\n```{custom_commands[command_name]}```",
				colour=discord.Color.green(),
			)
			emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
			emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
			await ctx.send(embed=emb)
		elif action.lower() == "delete":
			if command_name is None:
				emb = await self.client.utils.create_error_embed(
					ctx, "Укажите названия команды!"
				)
				await ctx.send(embed=emb)
				return

			if command_name not in custom_commands.keys():
				emb = await self.client.utils.create_error_embed(
					ctx, "Указаной команды не существует!"
				)
				await ctx.send(embed=emb)
				return

			custom_commands.pop(command_name)
			await self.client.database.execute(
				f"""UPDATE guilds SET custom_commands = %s WHERE guild_id = %s""",
				(json.dumps(custom_commands), ctx.guild.id)
			)

			emb = discord.Embed(
				description=f"**Команда - `{command_name}` успешно удаленна**",
				colour=discord.Color.green(),
			)
			emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
			emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
			await ctx.send(embed=emb)
		elif action.lower() == "edit":
			if command_name is None:
				emb = await self.client.utils.create_error_embed(
					ctx, "Укажите названия команды!"
				)
				await ctx.send(embed=emb)
				return

			if command_name not in custom_commands.keys():
				emb = await self.client.utils.create_error_embed(
					ctx, "Указаной команды не существует!"
				)
				await ctx.send(embed=emb)
				return

			if command_text is None:
				emb = await self.client.utils.create_error_embed(
					ctx, "Укажите код к команде!"
				)
				await ctx.send(embed=emb)
				return

			if len(command_text) > 1000:
				emb = await self.client.utils.create_error_embed(
					ctx, "Указаный код слишком большой(Максимум 1000 символов)!"
				)
				await ctx.send(embed=emb)
				return

			if command_text == custom_commands[command_name]:
				emb = await self.client.utils.create_error_embed(
					ctx, "Вы должны указать новый код отличающийся от старого!"
				)
				await ctx.send(embed=emb)
				return

			custom_commands.update({command_name: command_text})
			await self.client.database.execute(
				f"""UPDATE guilds SET custom_commands = %s WHERE guild_id = %s""",
				(json.dumps(custom_commands), ctx.guild.id)
			)

			emb = discord.Embed(
				description=f"**Код к команде - `{command_name}` успешно измененен**",
				colour=discord.Color.green(),
			)
			emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
			emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
			await ctx.send(embed=emb)
		elif action.lower() == "list":
			commands = ("\n".join([f"`{command}`" for command in custom_commands.keys()])
						if custom_commands != {} else "На сервере ещё нет кастомных команд")
			emb = discord.Embed(
				title="Кастомные команды сервера",
				description=commands,
				colour=discord.Color.green(),
			)
			emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
			emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
			await ctx.send(embed=emb)
		else:
			emb = await self.client.utils.create_error_embed(
				ctx, "**Укажите одно из этих действий: add, delete, edit, show, list!**",
			)
			await ctx.send(embed=emb)

	@setting.command(
		hidden=True,
		name="auto-responder",
		aliases=["autoresponder", "auto-responders", "autoresponders"],
		description="**Настройка авто-ответчиков**",
		usage="setting auto-responder [add/edit/delete/show/list] [Названия авто-ответчика] |Текст авто-ответчика|",
	)
	async def auto_responder(self, ctx, action: str, responder_name: str = None, *, text: str = None):
		auto_responders = (await self.client.database.sel_guild(guild=ctx.guild))["autoresponders"]
		if action.lower() == "add":
			if responder_name is None:
				emb = await self.client.utils.create_error_embed(
					ctx, "Укажите названия авто-ответчика!"
				)
				await ctx.send(embed=emb)
				return

			if responder_name in auto_responders.keys():
				emb = await self.client.utils.create_error_embed(
					ctx, "Указаный авто-ответчик уже есть в списке авто-ответчиков!"
				)
				await ctx.send(embed=emb)
				return

			if text is None:
				emb = await self.client.utils.create_error_embed(
					ctx, "Укажите текст к авто-ответчику!"
				)
				await ctx.send(embed=emb)
				return

			if len(auto_responders.keys()) > 15:
				emb = await self.client.utils.create_error_embed(
					ctx, "Вы достигли ограничения(15 авто-ответчиков)!"
				)
				await ctx.send(embed=emb)
				return

			if len(text) > 1500:
				emb = await self.client.utils.create_error_embed(
					ctx, "Указаный текст слишком большой(Максимум 1500 символов)!"
				)
				await ctx.send(embed=emb)
				return

			auto_responders.update({responder_name: text})
			await self.client.database.execute(
				f"""UPDATE guilds SET autoresponders = %s WHERE guild_id = %s""",
				(json.dumps(auto_responders), ctx.guild.id)
			)

			emb = discord.Embed(
				description=f"**Успешно создан новый авто-ответчик - `{responder_name}`**",
				colour=discord.Color.green(),
			)
			emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
			emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
			await ctx.send(embed=emb)
		elif action.lower() == "show":
			if responder_name is None:
				emb = await self.client.utils.create_error_embed(
					ctx, "Укажите названия авто-ответчика!"
				)
				await ctx.send(embed=emb)
				return

			if responder_name not in auto_responders.keys():
				emb = await self.client.utils.create_error_embed(
					ctx, "Указаного авто-ответчика не существует!"
				)
				await ctx.send(embed=emb)
				return

			emb = discord.Embed(
				title=f"Информация о авто-ответчике - `{responder_name}`",
				description=f"Текст авто-ответчика:\n```{auto_responders[responder_name]}```",
				colour=discord.Color.green(),
			)
			emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
			emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
			await ctx.send(embed=emb)
		elif action.lower() == "delete":
			if responder_name is None:
				emb = await self.client.utils.create_error_embed(
					ctx, "Укажите названия авто-ответчика!"
				)
				await ctx.send(embed=emb)
				return

			if responder_name not in auto_responders.keys():
				emb = await self.client.utils.create_error_embed(
					ctx, "Указаного авто-ответчика не существует!"
				)
				await ctx.send(embed=emb)
				return

			auto_responders.pop(responder_name)
			await self.client.database.execute(
				f"""UPDATE guilds SET autoresponders = %s WHERE guild_id = %s""",
				(json.dumps(auto_responders), ctx.guild.id)
			)

			emb = discord.Embed(
				description=f"**Авто-ответчик - `{responder_name}` успешно удален**",
				colour=discord.Color.green(),
			)
			emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
			emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
			await ctx.send(embed=emb)
		elif action.lower() == "edit":
			if responder_name is None:
				emb = await self.client.utils.create_error_embed(
					ctx, "Укажите названия авто-ответчика!"
				)
				await ctx.send(embed=emb)
				return

			if responder_name not in auto_responders.keys():
				emb = await self.client.utils.create_error_embed(
					ctx, "Указаного авто-ответчика не существует!"
				)
				await ctx.send(embed=emb)
				return

			if text is None:
				emb = await self.client.utils.create_error_embed(
					ctx,  "Укажите текст к авто-ответчику!"
				)
				await ctx.send(embed=emb)
				return

			if len(text) > 1500:
				emb = await self.client.utils.create_error_embed(
					ctx, "Указаный текст слишком большой(Максимум 1500 символов)!"
				)
				await ctx.send(embed=emb)
				return

			if text == auto_responders[responder_name]:
				emb = await self.client.utils.create_error_embed(
					ctx, "Вы должны указать новый текст отличающийся от старого!"
				)
				await ctx.send(embed=emb)
				return

			auto_responders.update({responder_name: text})
			await self.client.database.execute(
				f"""UPDATE guilds SET autoresponders = %s WHERE guild_id = %s""",
				(json.dumps(auto_responders), ctx.guild.id)
			)

			emb = discord.Embed(
				description=f"**Текст к авто-ответчику - `{responder_name}` успешно измененен**",
				colour=discord.Color.green(),
			)
			emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
			emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
			await ctx.send(embed=emb)

		elif action.lower() == "list":
			commands = ("\n".join([f"`{command}`" for command in auto_responders.keys()])
						if auto_responders != {} else "На сервере ещё нет авто-ответчиков")
			emb = discord.Embed(
				title="Авто-ответчики сервера",
				description=commands,
				colour=discord.Color.green(),
			)
			emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
			emb.set_footer(text=self.FOOTER, icon_url=self.client.user.avatar_url)
			await ctx.send(embed=emb)
		else:
			emb = await self.client.utils.create_error_embed(
				ctx, "**Укажите одно из этих действий: add, delete, edit, show, list!**",
			)
			await ctx.send(embed=emb)


def setup(client):
	client.add_cog(Settings(client))
