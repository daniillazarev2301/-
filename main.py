# coding: utf8
#
# version: 2020-05-09.10-30
#
# Создатель Permyak_Logy#8606
# По заказу от Daniillazarev#0202 685355179570233344

import discord
from datetime import datetime
import json
import random
import re

config_file_name = 'config.json'


class Obj:
    pass


class FastEmoji:
    yes = discord.PartialEmoji(animated=False, name='✅', id=None)
    not_ = discord.PartialEmoji(animated=False, name='❌', id=None)
    close = discord.PartialEmoji(animated=False, name='⏹️', id=None)


class FrostyBot(discord.Client):
    config_data = {}

    async def on_ready(self):
        guild_list_name = "\n".join([f"\t{guild}" for guild in self.guilds])
        message = (
            f'```python\n'
            f'{datetime.now()} Бот {self.user.mention} класса {self.__class__.__name__}'
            f' бы авторизован и готов к работе\n'
            f'Подключённые сервера:\n{guild_list_name}\n'
            f'```'
        )
        print(message)
        await self.load_config()
        await self.get_user(685355179570233344).send(message)

    async def load_config(self):
        data = self.config_data
        try:
            with open(config_file_name, encoding='utf8') as file:
                self.config_data = json.load(file)
        except Exception as E:
            print(E)
            self.config_data = data
            await self.logout()
        else:
            # Просматриваемая гильдия
            self.checked_guild: discord.Guild = self.get_guild(
                self.config_data['checked_guild']
            )
            self.log_channel: discord.TextChannel = self.get_channel(
                self.config_data['log_channel']
            )
            if not self.checked_guild or not self.log_channel:
                print(self.checked_guild, self.log_channel)
                await self.logout()

    async def save_config(self):
        with open(config_file_name, encoding='utf8') as file:
            data = file.read()
        try:
            with open(config_file_name, mode='w', encoding='utf8') as file:
                file.write(
                    str(self.config_data
                        ).replace("'", '"'
                                  ).replace('None', 'null'
                                            ).replace('True', 'true'
                                                      ).replace('False', 'false')
                )
        except Exception as E:
            print(E)
            with open(config_file_name, mode='w', encoding='utf8') as file:
                file.write(data)

    async def on_message(self, message: discord.Message):
        if self.user == message.author:
            return
        if await self.application_processor_on_message(message):
            return True

    async def application_processor_on_message(self, message: discord.Message):
        channel_applications = self.get_channel(self.config_data.get('channel_applications', 0))
        channel_moderation_applications = self.get_channel(self.config_data.get('channel_moderation_applications', 0))
        if not channel_applications or not channel_moderation_applications:
            return False

        if message.channel.id == channel_applications.id:
            delay = 10
            if len(message.content) <= 20:
                embed = discord.Embed(
                    title="**ОТКАЗАНО В ОБРАБОТКЕ**",
                    colour=discord.Colour.from_rgb(255, 78, 78),

                    description=(
                        'Ваше сообщение слишком короткое\n'
                        'Не стесняйтесь, распишите заявку по полной!'
                    )
                )
                message_bot: discord.Message = await channel_applications.send(embed=embed)

                await message_bot.delete(delay=delay)
                await message.delete(delay=delay)
                return True

            if len(message.content) >= 1500:
                embed = discord.Embed(
                    title="**ОТКАЗАНО В ОБРАБОТКЕ**",
                    colour=discord.Colour.from_rgb(255, 78, 78),
                    description=(
                        'Ваше сообщение слишком большое\n'
                        'Постарайтесь сократить сообщение!'
                    )
                )
                message_bot: discord.Message = await channel_applications.send(embed=embed)
                await message_bot.delete(delay=delay)
                await message.delete(delay=delay)
                return True

            if re.search(r'https://[^(vk.com/)]', message.content.lower()):
                embed = discord.Embed(
                    title="**ОТКАЗАНО В ОБРАБОТКЕ**",
                    colour=discord.Colour.from_rgb(255, 78, 78),
                    description=(
                        'Имеется запрещённая ссылка'
                    )
                )
                message_bot: discord.Message = await channel_applications.send(embed=embed)
                await message_bot.delete(delay=delay)
                await message.delete(delay=delay)
                return True

            if not re.search(r'1\..*\n2\..*\n3\..*\n4\..*\n5\..*\n6\..*', message.content):
                embed = discord.Embed(
                    title="**ОТКАЗАНО В ОБРАБОТКЕ**",
                    colour=discord.Colour.from_rgb(255, 78, 78),
                    description=(
                        'Вы написали заявку не по форме\n'
                        'Прочитайте закрепленное сообщение, что посмотреть форму заявки!\n'
                        'Соблюдайте каждый знак, возможно вы написали пункты 1,2,3 без точки!'

                    )
                )
                message_bot: discord.Message = await channel_applications.send(embed=embed)
                await message_bot.delete(delay=delay)
                await message.delete(delay=delay)
                return True

            author: discord.Member = message.author

            # Сообщение о заявке
            changed_message_user = message.content.replace('\n', '\n> ')
            embed = discord.Embed(
                title="**НОВАЯ ЗАЯВКА НА ПОСТ АДМИНИСТРАЦИИ**",
                colour=discord.Colour.from_rgb(117, 117, 255),
                timestamp=datetime.now(),
                description=(
                    ''
                )
            )
            embed.add_field(name='Автор',
                            value=f'{author.mention}', inline=True)
            embed.add_field(name='ID Автора',
                            value=f'{author.id}', inline=True)
            embed.add_field(name='Дата регистрации',
                            value=f'{author.created_at.date()}', inline=True)
            embed.add_field(name='Дата присоединения на сервер',
                            value=f'{author.joined_at.date()}')
            embed.add_field(name='Время с момента присоединения на сервер',
                            value=f'{(datetime.now() - author.joined_at).days} days')
            embed.add_field(name='Выберите действие',
                            value=':white_check_mark: Принять \n:x: Отклонить \n:stop_button: Закрыть')
            embed.add_field(name='**Текст сообщения**',
                            value=f'> {changed_message_user}')

            message_bot: discord.Message = await channel_moderation_applications.send(embed=embed)

            # Добавление реакций
            await message_bot.add_reaction(FastEmoji.yes)
            await message_bot.add_reaction(FastEmoji.not_)
            await message_bot.add_reaction(FastEmoji.close)

            # Формирование заявки
            application = dict()
            application['id'] = random.randint(0, 2 ** 64)
            application['author'] = message.author.id
            application['message_id'] = message_bot.id

            # Занесение заявки в память
            if not self.config_data.get('applications'):
                self.config_data['applications'] = []
            self.config_data['applications'].append(application)

            # Ответ автору заявки
            embed = discord.Embed(
                title=f'**Уведомление**',
                colour=discord.Colour.from_rgb(117, 117, 255),
                description=(
                    f'{author.mention} Ваша заявка отправлена на расмотрение, ожидайте ответа!'
                )
            )
            response = await channel_applications.send(embed=embed)
            await response.delete(delay=delay)
            await message.delete()

            # Сохранение данных конфигурации
            await self.save_config()
            return True

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        try:
            channel: discord.TextChannel = self.get_channel(payload.channel_id)
            reaction = Obj()
            reaction.message = await channel.fetch_message(payload.message_id)
            reaction.emoji = payload.emoji
            user = self.get_user(payload.user_id)
            await self._on_reaction_add(reaction, user)
        except discord.errors.NotFound as E:
            print(E)

    async def _on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        if self.user == user:
            return
        if await self.application_processor_on_reaction_add(reaction, user):
            return True

    async def application_processor_on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        channel_applications = self.get_channel(self.config_data.get('channel_applications', 0))
        channel_moderation_applications = self.get_channel(self.config_data.get('channel_moderation_applications', 0))
        if not channel_applications or not channel_moderation_applications:
            return False

        if any(map(lambda x: x['message_id'] == reaction.message.id, self.config_data.get('applications', []))):
            application = list(filter(lambda x: x['message_id'] == reaction.message.id,
                                      self.config_data['applications']))[0]

            author: discord.Member = self.checked_guild.get_member(application['author'])

            delay = 6 * 60 * 60
            # Обработка реакций
            if reaction.emoji.name == FastEmoji.yes.name:
                issued_role1 = self.checked_guild.get_role(self.config_data.get('issued_role'))
                if issued_role1:
                    await author.add_roles(issued_role1)
                try:
                    await author.edit(nick=f'[7] {author.display_name}')
                except discord.errors.Forbidden:
                    pass
                embed = discord.Embed(
                    title='**Уведомление**',
                    timestamp=datetime.now(),
                    colour=discord.Colour.from_rgb(100, 255, 100),
                    description=(
                        f'{author.mention}**, ваша заявка одобрена!**\n'
                        f'Теперь вы являетесь администратором сервера!\n'
                        f'Обязательно прочтите правила для начала работы!\n'
                    )
                )
                embed.add_field(name='Рассматривал:', value=f'{user.mention}')
                embed.add_field(name='Примечание:', value='Cообщение удалится через несколько часов!')
                act = '**Одобрена**'
                message_bot = await channel_applications.send(embed=embed)
                await message_bot.delete(delay=delay)

            elif reaction.emoji.name == FastEmoji.not_.name:
                embed = discord.Embed(
                    title='**Уведомление**',
                    timestamp=datetime.now(),
                    colour=discord.Colour.from_rgb(255, 78, 78),
                    description=(
                        f'{author.mention}**, ваша заявка не прошла проверку!**\n'
                        f'Возможно, вы не прошли по критериям, почитайте правила подачи заявки.'
                    )
                )
                embed.add_field(name='Рассматривал:', value=f'{user.mention}')
                embed.add_field(name='Примечание:', value='Cообщение удалится через несколько часов!')
                act = '**Отклонена**'
                message_bot = await channel_applications.send(embed=embed)
                await message_bot.delete(delay=6 * 60 * 60)

            elif reaction.emoji.name == FastEmoji.close.name:
                act = '**Закрыта**'
            else:
                return False

            # Логирование
            embed = discord.Embed(
                title='**ЛОГ ЗАЯВОК**',
                timestamp=datetime.now(),
                colour=discord.Colour.from_rgb(117, 117, 255),
                description=(
                    f'Была расмотренна новая заявка.'
                )
            )
            embed.add_field(name='Автор:', value=f'{author.mention}', inline=True)
            embed.add_field(name='Рассмотрел:', value=f'{user.mention}', inline=True)
            embed.add_field(name='Вердикт:', value=act, inline=True)
            await self.log_channel.send(embed=embed)

            # Очистка заявки
            # await reaction.message.delete()

            # Очистка заявки из памяти
            self.config_data['applications'].remove(application)

            # Сохранение данных конфигурации
            await self.save_config()

            # Сообщение об успехе
            message_bot: discord.Message = await channel_moderation_applications.send(embed=discord.Embed(
                title='**Уведомление**', timestamp=datetime.now(), colour=discord.Colour.from_rgb(100, 255, 100),
                description='Успешно!'
            ))
            await message_bot.delete(delay=5)

            return True


if __name__ == '__main__':
    FrostyBot().run(open('token.txt').read())
