import asyncio
import logging

from src.telegram import bot, dp
from src.database import create_db_and_tables, sessionmanager, get_db_session
# from src.database import RoleRepository
# from src.database.constant import RoleEnum, PermissionsEnum
from config import configuration
# from src.database.repository.team_repository import TeamRepository


async def main():
    # async with sessionmanager.session() as session:
    #     role_repository = RoleRepository(session)
    #     admin_role = await role_repository.get_by_name(RoleEnum.GUEST.value)
    #     print(await role_repository.check_permission(admin_role, PermissionsEnum.send_suggestions))
    # while True:
    #     await asyncio.sleep(1)
    await create_db_and_tables()

    # async with sessionmanager.session() as session:
    #     team_repo = TeamRepository(session)
    #     team = await team_repo.get_by_entry(123)
    #     await team_repo.set_pick(team, 3, 4)
    #     await session.commit()
    #     print(await team_repo.get_pick(team, 3))


    # await bot.delete_webhook(drop_pending_updates=True)
    # await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        logging.info("Starting bot")
        asyncio.run(main())
        print(configuration)
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped")
        if sessionmanager._engine is not None:
            asyncio.run(sessionmanager.close())