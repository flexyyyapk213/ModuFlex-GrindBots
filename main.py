import loads
from pyrogram import filters, types
from pyrogram.client import Client
from pyrogram.utils import zero_datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.job import Job
import re
from datetime import datetime, timedelta
from pyrogram.errors import PeerIdInvalid, MessageIdInvalid
from pyrogram import enums
from typing import Any, Optional
import traceback

class GrindBots(loads.Module):
    def __init__(self):
        self.timer = AsyncIOScheduler(
            job_defaults={
                'coalesce': False,
                'max_instances': 3,
                'misfire_grace_time': None
            })
        
        default_config = {
            "iris_farma": {
                "activated": False,
                "next_request_date": zero_datetime().strftime('%Y %m %d %H %M %S')
            },
            "skrework_promo": {
                "activated": False,
                "next_request_date": zero_datetime().strftime('%Y %m %d %H %M %S'),
                "msg_id": -1
            },
            "bfg_promo": {
                "activated": False
            }
        }

        loads.Data.get_config(__file__).setdefault(default_config)

        self.timer.start()

        self._config = loads.Data.get_config(__file__)
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        for param in args:
            if isinstance(param, Client):
                if self._config['iris_farma']['activated']:
                    self.timer.add_job(self.__send_farma_iris__, trigger=DateTrigger(datetime.strptime(self._config['iris_farma']['next_request_date'], '%Y %m %d %H %M %S')), args=(param,), id='iris_farma')

    @loads.func(filters.command('irisfarma', ['/', '.', '!']) & filters.me, description='фарм i¢ у @iris_moon_bot')
    async def iris_farma(self, app: Client, message: types.Message):
        if not self._config['iris_farma']['activated']:
            try:
                await app.send_message('@iris_moon_bot', 'Фарма')
            except PeerIdInvalid:
                return await app.send_message('me', '```GrindBots\nНе возможно написать боту @iris_moon_bot\nНачните с ним диалог и снова вызовите эту команду.```', parse_mode=enums.ParseMode.MARKDOWN)
            
            self._config['iris_farma']['activated'] = True

            _job: Job = self.timer.get_job('iris_farma')

            if _job is not None:
                _job.reschedule(DateTrigger(datetime.strptime(self._config['iris_farma']['next_request_date'], '%Y %m %d %H %M %S')))
                _job.resume()
            
            return await message.edit_text('Фарминг начался.')
        else:
            self._config['iris_farma']['activated'] = False

            _job: Job = self.timer.get_job('iris_farma')

            if _job is not None:
                self._config['iris_farma']['next_request_date'] = _job.trigger.run_date.strftime('%Y %m %d %H %M %S')
                _job.pause()
            
            return await message.edit_text('Фарминг закончился.')
    
    @loads.func(filters.user('@iris_moon_bot') & filters.private)
    async def parse_messages_from_iris(self, app: Client, message: types.Message):
        if message.text.startswith('❌ НЕЗАЧЁТ! Фармить можно раз в '):
            hours = int(re.search('(\d) часа', message.text.replace('❌ НЕЗАЧЁТ! Фармить можно раз в ', '')).group(1))
            minutes = int(re.search('(\d) мин', message.text.replace('❌ НЕЗАЧЁТ! Фармить можно раз в ', '')).group(1))

            total_seconds = (hours * 3600) + (minutes * 60) + 10

            self._config['iris_farma']['next_request_date'] = (datetime.now() + timedelta(seconds=total_seconds)).strftime('%Y %m %d %H %M %S')

            _job: Job = self.timer.get_job('iris_farma')

            if _job is None:
                self.timer.add_job(self.__send_farma_iris__, DateTrigger(datetime.now() + timedelta(seconds=total_seconds)), id='iris_farma', args=(app,))
            else:
                _job.reschedule(DateTrigger(datetime.now() + timedelta(seconds=total_seconds)))
    
    async def __send_farma_iris__(self, app: Client):
        _job: Job = self.timer.get_job('iris_farma')
        
        try:
            await app.send_message('@iris_moon_bot', 'Фарма')
        except PeerIdInvalid:
            if _job is not None:
                _job.pause()
            
            self._config['iris_farma']['activated'] = False

            return await app.send_message('me', '```GrindBots\nНе возможно написать боту @iris_moon_bot\nНачните с ним диалог и вызовите команду /irisfarma.```', parse_mode=enums.ParseMode.MARKDOWN)

        new_date = datetime.now() + timedelta(hours=4)

        self._config['iris_farma']['next_request_date'] = new_date.strftime('%Y %m %d %H %M %S')

        _job.reschedule(DateTrigger(datetime.now() + timedelta(hours=4)))
        _job.resume()

    async def __get_msg_id_sk__(self, app: Client, msg_id: int=-1) -> Optional[types.Message]:
        if msg_id != -1:
            try:
                await app.get_messages('@ReworkStarsBot', msg_id)

                return msg_id
            except MessageIdInvalid:
                pass
        
        async for history in app.get_chat_history('@ReworkStarsBot'):
            if history.reply_markup is not None:
                return history
        
        return None
    
    @loads.func(filters.command('skpromo', ['/', '.', '!']) & filters.me, description='фарм промокодов у @ReworkStarsBot')
    async def sk_farming_promo(self, app: Client, message: types.Message):
        if not self._config['skrework_promo']['activated']:
            msg = await self.__get_msg_id_sk__(app, self._config['skrework_promo']['msg_id'])

            try:
                await msg.click()
            except Exception:
                traceback.print_exc()
                return await message.edit_text('```GrindBots\nНе возможно нажать на кнопку, отправьте боту @ReworkStarsBot /start\n```')
            
            self._config['skrework_promo']['activated'] = True

            _job: Job = self.timer.get_job('skrework_promo')

            if _job is not None:
                _job.reschedule(DateTrigger(datetime.strptime(self._config['skrework_promo']['next_request_date'], '%Y %m %d %H %M %S')))
                _job.resume()
            
            return await message.edit_text('Фарминг начался.')
        else:
            self._config['skrework_promo']['activated'] = False

            _job: Job = self.timer.get_job('skrework_promo')

            if _job is not None:
                self._config['skrework_promo']['next_request_date'] = _job.trigger.run_date.strftime('%Y %m %d %H %M %S')
                _job.pause()
            
            return await message.edit_text('Фарминг закончился.')
    
    async def __send_parse_sk__(self, app: Client):
        msg = await self.__get_msg_id_sk__(app, self._config['skrework_promo']['msg_id'])

        try:
            await msg.click()
        except Exception:
            traceback.print_exc()
            return await app.send_message('me', '```GrindBots\nНе возможно нажать на кнопку, отправьте боту @ReworkStarsBot /start\n```')
        
        dtime = datetime.now() + timedelta(minutes=5)

        self._config['skrework_promo']['next_request_date'] = dtime.strftime('%Y %m %d %H %M %S')
            
        _job: Job = self.timer.get_job('skrework_promo')
        
        _job.reschedule(DateTrigger(dtime))
        _job.resume()
    
    @loads.func(filters.user('@ReworkStarsBot') & filters.private & filters.chat())
    async def parse_message_from_sk(self, app: Client, message: types.Message):
        if message.text.startswith('⛔️ Промокод уже получен.\n⏱️ Следующий будет доступен через: '):
            hours = re.search(r'(\d+)ч', message.text)
            minutes = re.search(r'(\d+)м', message.text)
            seconds = re.search(fr'(\d+)с', message.text)

            total_seconds = 0

            if hours is not None:
                total_seconds += int(hours.group(1)) * 3600
            
            if minutes is not None:
                total_seconds += int(minutes.group(1)) * 60
            
            if seconds is not None:
                total_seconds += int(seconds.group(1))
            
            dtime = datetime.now() + timedelta(seconds=total_seconds)

            self._config['skrework_promo']['next_request_date'] = dtime.strftime('%Y %m %d %H %M %S')
            
            _job: Job = self.timer.get_job('skrework_promo')
            
            if _job is not None:
                _job.reschedule(DateTrigger(datetime.strptime(self._config['skrework_promo']['next_request_date'], '%Y %m %d %H %M %S')))
                _job.resume()
            else:
                self.timer.add_job(self.__send_parse_sk__, DateTrigger(dtime), (app,), id='skrework_promo')
        elif message.text.startswith('✅ Сгенерирован промокод: '):
            dtime = datetime.now() + timedelta(minutes=5)

            self._config['skrework_promo']['next_request_date'] = dtime.strftime('%Y %m %d %H %M %S')
            
            _job: Job = self.timer.get_job('skrework_promo')
            
            if _job is not None:
                _job.reschedule(DateTrigger(datetime.strptime(self._config['skrework_promo']['next_request_date'], '%Y %m %d %H %M %S')))
                _job.resume()
            else:
                self.timer.add_job(self.__send_parse_sk__, DateTrigger(dtime), (app,), id='skrework_promo')
    
    @loads.func(filters.command('bfgpromo', ['/', '.', '!']) & filters.me, description='фарм промокодов у @bfgproject')
    async def bfg_farming_promo(self, _: Client, message: types.Message):
        if self._config['bfg_promo']['activated']:
            self._config['bfg_promo']['activated'] = False

            await message.edit_text('Фарминг закончился.')
        else:
            self._config['bfg_promo']['activated'] = True

            await message.edit_text('Фарминг начался.')
    
    @loads.func(filters.chat(1524574130))
    async def parse_message_bfg(self, app: Client, message: types.Message):
        if self._config['bfg_promo']['activated']:
            promo = re.search(r'промо #[\w_]+', message.text.lower())

            if promo is not None:
                try:
                    await app.send_message('@bfgproject', promo.group(1).capitalize())
                except:
                    await app.send_message('me', '```GrindBots\nНе возможно написать боту @bfgproject, отправьте боту /start\n```')