# screens/communicate_screen.py
import logging
from aiogram import types
from aiogram.fsm.context import FSMContext

from screens.base import BaseScreen
from states.communicate import Communicate
from keyboards.presets import communicate_kb
from db.session import get_session
from db.models import User


class CommunicateScreen(BaseScreen):
    """
    Просит прислать текст новости для предложения.
    Ставит FSM в Communicate.waiting_news.
    """
    async def _pre_render(
        self,
        message: types.Message,
        actor: types.User | None = None,
        state: FSMContext | None = None,
        error_text: str | None = None,
        **kwargs
    ):
        tg_user = actor or message.from_user
        tg_id = tg_user.id
        logging.info("CommunicateScreen for tg_id=%s", tg_id)

        # Load user from database to get current information points
        async with get_session() as session:
            db_user = await User.get_by_tg_id(session, tg_id)
            if not db_user:
                db_user = await User.create(
                    session=session,
                    tg_id=tg_id,
                    username=tg_user.username,
                    first_name=tg_user.first_name,
                    last_name=tg_user.last_name,
                    language_code=tg_user.language_code,
                )

        if state:
            await state.set_state(Communicate.waiting_news)

        ctx = {
            "title": "🗞️ Предложить новость",
            "lines": [
                "Пришлите текст новости одним сообщением.",
                "Эта заявка создаст действие «communicate» (без района).",
                "Текст будет записан в поле action.text и после этого вы попадёте в экран настройки заявки.",
                f"💡 У вас доступно: {db_user.information} 🧠 информации",
            ],
            "hint": "Отправьте новость (от 1 до 600 символов):",
            "error_text": error_text,   # опционально показываем ошибку
        }

        return {
            "communicate": ctx,
            "keyboard": communicate_kb()
        }
