import sys

import const
from vkbottle.user import User
from vkbottle.api import UserApi
from objects import Database
from commands import commands_bp
import argparse
import os


parser = argparse.ArgumentParser(
    description='LP модуль позволяет работать приемнику сигналов «IDM multi» работать в любых чатах.\n'
                'Так же он добавляет игнор, глоигнор, мут и алиасы.'
)

parser.add_argument(
    '--config_path',
    type=str,
    dest="config_path",
    default="config.json",
    help='Путь до файла с конфингом'
)

parser.add_argument(
    '--use_app_data',
    dest="use_app_data",
    action="store_const",
    const=True,
    help='Использовать папку AppData/IDM (Windows).\n'
         'При использовании этой настройки AppData/IDM и config_path складываются'
)


async def lp_startup():
    api = UserApi.get_current()
    await api.messages.send(
        peer_id=await api.user_id,
        random_id=0,
        message=f'IDM multi LP v{const.__version__} запущен'
    )


async def lp_shutdown():
    api = UserApi.get_current()
    await api.messages.send(
        peer_id=await api.user_id,
        random_id=0,
        message=f'IDM multi LP v{const.__version__} остановлен'
    )

if __name__ == '__main__':
    args = parser.parse_args()

    const.CONFIG_PATH = args.config_path
    const.USE_APP_DATA = args.use_app_data if args.use_app_data else False

    sys.stdout.write(
        f"Запуск с параметрами:\n"
        f"    Путь до файла с конфингом         -> {const.CONFIG_PATH}\n"
        f"    Использовать папку AppData/IDM    -> {const.USE_APP_DATA}\n"
    )

    try:
        db = Database.load()
    except Database.DatabaseError as ex:
        sys.stdout.write(f'При запуске произошла ошибка [{ex.__class__.__name__}] {ex}\n')
        exit(-1)
    except Exception as ex:
        sys.stdout.write(f'При запуске произошла ошибка [{ex.__class__.__name__}] {ex}\n')
        exit(-1)
    else:
        from validators import *
        user = User(
            tokens=db.tokens,
            debug='ERROR'
        )
        user.set_blueprints(
            *commands_bp
        )
        user.run_polling(
            auto_reload=False,
            on_startup=lp_startup,
            on_shutdown=lp_shutdown
        )
        sys.stdout.write(f'Пуллинг запущен\n')