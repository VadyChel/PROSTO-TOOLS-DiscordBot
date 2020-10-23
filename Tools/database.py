import mysql.connector
import os
import datetime
import json
import time
import discord


class DB:

	def __init__(self):
		self.conn = mysql.connector.connect(user = 'root', password = os.environ['DB_PASSWORD'], host = 'localhost', database = 'data')
		self.cursor = self.conn.cursor(buffered = True)

	def set_reminder(self, member: discord.Member, time: str, text: str):
		pass

	
	def get_reminder(self, member: discord.Member = None):
		pass

	
	def del_reminder(self, reminder_id: int):
		pass


	def set_warn(self, **kwargs):
		self.cursor.execute(("""SELECT id FROM warns WHERE guild_id = %s AND guild_id = %s"""), (kwargs['target'].guild.id, kwargs['target'].guild.id))
		db_ids = self.cursor.fetchall()
		ids = [str(stat[0]) for stat in db_ids]
		ids.reverse()
		try:
			new_id = int(ids[0])+1
		except:
			new_id = 1

		self.cursor.execute(("""SELECT num FROM warns WHERE user_id = %s AND guild_id = %s"""), (kwargs['target'].id, kwargs['target'].guild.id))
		db_nums = self.cursor.fetchall()
		nums = [num[0] for num in db_nums]
		nums.reverse()
		try:
			new_num = nums[0]+1
		except:
			new_num = 1

		sql = ("""INSERT INTO warns VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""")
		val = (new_id, kwargs['target'].id, kwargs['target'].guild.id, kwargs['reason'], 'True', str(datetime.datetime.today()), kwargs['author'], new_num) 

		self.cursor.execute(sql, val)
		self.conn.commit()

		return new_id


	def del_warn(self, guild_id, warn_id):
		try:
			self.cursor.execute(("""UPDATE warns SET state = %s WHERE id = %s"""), ('False', warn_id))
			self.conn.commit()

			self.cursor.execute(("""SELECT user_id FROM warns WHERE id = %s AND id = %s"""), (warn_id, warn_id))
			return self.cursor.fetchone()
		except:
			return False


	def set_mute(self, **kwargs):
		self.cursor.execute(("""SELECT id FROM mutes WHERE guild_id = %s AND guild_id = %s"""), (kwargs['target'].guild.id, kwargs['target'].guild.id))
		db_ids = self.cursor.fetchall()
		ids = [str(stat[0]) for stat in db_ids]
		ids.reverse()
		try:
			new_id = int(ids[0])+1
		except:
			new_id = 1

		sql = ("""INSERT INTO mutes VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""")
		val = (new_id, kwargs['target'].id, kwargs['target'].guild.id, kwargs['reason'], 'True', str(datetime.datetime.fromtimestamp(kwargs['timestamp'])), str(datetime.datetime.today()), kwargs['author'])

		self.cursor.execute(sql, val)
		self.conn.commit()


	def del_mute(self, member_id, guild_id):
		try:
			self.cursor.execute(("""DELETE FROM mutes WHERE user_id = %s AND guild_id = %s"""), (member_id, guild_id))
			self.conn.commit()

			return True
		except:
			return False


	def set_punishment(self, type_punishment: str, time: float, member: discord.Member, role_id: int = 0, **kwargs):
		self.cursor.execute("""SELECT * FROM punishments WHERE member_id = %s AND guild_id = %s""", (member.id, member.guild.id))
		data = self.cursor.fetchone()

		if type_punishment == 'mute':
			self.set_mute(timestamp=time, target=member, reason=kwargs['reason'], author=kwargs['author'])

		if not data:
			sql = ("""INSERT INTO punishments VALUES (%s, %s, %s, %s, %s)""")
			val = (member.id, member.guild.id, time, type_punishment, role_id)
			
			self.cursor.execute(sql, val)
			self.conn.commit()
		else:
			sql = ("""UPDATE punishments SET time = %s WHERE member_id = %s AND guild_id = %s""")
			val = (time, member.id, member.guild.id)

			self.cursor.execute(sql, val)
			self.conn.commit()


	def get_punishment(self, member: discord.Member = None):
		if member:
			sql = ("""SELECT * FROM punishments WHERE member = %s AND member = %s""")
			val = (member.id)

			self.cursor.execute(sql, val)
			data = self.cursor.fetchone()
		else:
			self.cursor.execute(f"""SELECT * FROM punishments WHERE time < {float(time.time())}""")
			data = self.cursor.fetchall()

		return data

	
	def del_punishment(self, member: discord.Member, guild_id: int, type_punishment: str):
		if type_punishment == 'mute':
			self.del_mute(member.id, member.guild.id)

		self.cursor.execute(("""DELETE FROM punishments WHERE member_id = %s AND guild_id = %s AND type = %s"""), (member.id, guild_id, type_punishment))
		self.conn.commit()


	def sel_user(self, target, check = True):
		sql_1 = ("""SELECT * FROM users WHERE user_id = %s AND guild_id = %s""")
		val_1 = (target.id, target.guild.id)
		sql_2 = ("""INSERT INTO users (user_id, guild_id, prison, profile, items, pets, warns, clans, messages, transantions, bio) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""")
		val_2 = (target.id, target.guild.id, 'False', 'lime', json.dumps([]), json.dumps([]), json.dumps([]), json.dumps([]), json.dumps([0, 0, None]), json.dumps([]), '')
		sql_3 = ("""SELECT bio FROM users WHERE user_id = %s AND user_id = %s""")
		val_3 = (target.id, target.id)
		sql_4 = ("""SELECT * FROM warns WHERE user_id = %s AND guild_id = %s""")
		val_4 = (target.id, target.guild.id)

		self.cursor.execute(sql_1, val_1)
		data = self.cursor.fetchone()
		self.cursor.execute(sql_3, val_3)
		bio = self.cursor.fetchone()
		self.cursor.execute(sql_4, val_4)
		db_warns = self.cursor.fetchall()

		if check:
			if not data:
				self.cursor.execute(sql_2, val_2)
				self.conn.commit()

		self.cursor.execute(sql_1, val_1)
		data = self.cursor.fetchone()
		self.cursor.execute(sql_3, val_3)
		bio = self.cursor.fetchone()

		if data:
			prison = data[8]
			if prison == 'True':
				prison = True
			elif prison == 'False':
				prison = False

			warns = []
			for warn in db_warns:
				if warn[4] == 'True':
					state = True
				elif warn[4] == 'False':
					state = False
				warns.append({'id': warn[0], 'time': warn[5], 'reason': warn[3], 'author': warn[6], 'num_warn': warn[7], 'state': state, 'guild_id': warn[2]})

			dict_data = {
				'user_id': int(data[0]),
				'guild_id': int(data[1]),
				'lvl': int(data[2]),
				'exp': int(data[3]),
				'money': int(data[4]),
				'coins': int(data[5]),
				'text_channels': int(data[6]),
				'reputation': int(data[7]),
				'prison': prison,
				'profile': str(data[9]),
				'items': json.loads(data[11]),
				'pets': json.loads(data[12]),
				'warns': warns,
				'clans': json.loads(data[13]),
				'messages': json.loads(data[14]),
				'transantions': json.loads(data[15]),
				'bio': bio[0]
			}

			return dict_data


	def sel_guild(self, guild):
		sql_1 = ("""SELECT * FROM guilds WHERE guild_id = %s AND guild_id = %s""")
		val_1 = (guild.id, guild.id)
		sql_2 = ("""INSERT INTO guilds (guild_id, donate, prefix, shop_list, ignored_channels, auto_mod, clans, server_stats, voice_channel, moderators, react_channels, welcome, auto_roles) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""")
		val_2 = (guild.id, "False", "*", json.dumps([]), json.dumps([]), json.dumps({"anti_flud": False, "auto_anti_rade_mode": False, "react_coomands": True}), json.dumps([]), json.dumps({}), json.dumps({}), json.dumps([]), json.dumps([]), json.dumps({}), json.dumps({}))
		
		self.cursor.execute(sql_1, val_1)
		data = self.cursor.fetchone()

		if not data:
			self.cursor.execute(sql_2, val_2)
			self.conn.commit()

		self.cursor.execute(sql_1, val_1)
		data = self.cursor.fetchone()

		donate = data[8]
		if donate == 'True':
			donate = True
		elif donate == 'False':
			donate = False

		dict_data = {
			'guild_id': int(data[0]),
			'purge': int(data[1]),
			'all_message': int(data[2]),
			'textchannels_category': int(data[3]),
			'max_warns': int(data[4]),
			'exp_multi': float(data[5]),
			'idea_channel': int(data[6]),
			'timedelete_textchannel': int(data[7]),
			'donate': donate,
			'prefix': str(data[9]),
			'server_stats': json.loads(data[10]),
			'voice_channel': json.loads(data[11]),
			'shop_list': json.loads(data[12]),
			'ignored_channels': json.loads(data[13]),
			'auto_mod': json.loads(data[14]),
			'clans': json.loads(data[15]),
			'moder_roles': json.loads(data[16]),
			'react_channels': json.loads(data[17]),
			'welcome': json.loads(data[18]),
			'auto_roles': json.loads(data[19])
		}

		return dict_data

	def add_amout_command(self, entity: str = 'all commands', add_counter = None):
		try:
			self.cursor.execute(f"""SELECT * FROM bot_stats WHERE entity = '{entity}'""")
			data = self.cursor.fetchall()
		except:
			data = [(0, 0)]

		self.cursor.execute(f"""SELECT * FROM bot_stats WHERE entity = 'all commands'""")
		main_data = self.cursor.fetchall()

		self.cursor.execute(f"""SELECT id FROM bot_stats""")
		global_data = self.cursor.fetchall()

		stat_ids = [str(stat[0]) for stat in global_data]
		stat_ids.reverse()
		try:
			new_id = int(stat_ids[0])+1
		except:
			new_id = 0

		counter = [str(stat[1]) for stat in data]
		counter.reverse()
		try:
			new_count = int(counter[0])+1
		except:
			new_count = 1

		main_counter = [str(stat[1]) for stat in main_data]
		main_counter.reverse()
		try:
			new_main_count = int(main_counter[0])+1
		except:
			new_main_count = 1

		if add_counter is not None:
			new_count = add_counter
		
		if add_counter is None:
			sql = ("""INSERT INTO bot_stats(id, count, timestamp, entity) VALUES(%s, %s, %s, %s)""")
			val = (new_id, new_main_count, datetime.datetime.now(), 'all commands')

			self.cursor.execute(sql, val)
			self.conn.commit()

		sql = ("""INSERT INTO bot_stats(id, count, timestamp, entity) VALUES(%s, %s, %s, %s)""")
		val = (new_id+1, new_count, datetime.datetime.now(), entity)

		self.cursor.execute(sql, val)
		self.conn.commit()

