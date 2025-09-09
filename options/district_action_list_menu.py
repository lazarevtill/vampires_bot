import logging

from aiogram import types
from aiogram.fsm.context import FSMContext

from screens.actions import ActionsScreen
from screens.settings_action import DistrictActionList, SettingsActionScreen
from .registry import option
from db.session import get_session
from db.models import District, User, Action, ActionType, ActionStatus
from sqlalchemy import select
from sqlalchemy.orm import selectinload


async def _apply_politician_bonuses_on_create(session, action):
    """Применяет бонусы от политиков района при создании действия."""
    if not action.district_id:
        return
    
    # Получаем политика района
    from db.models import Politician
    from utils.bonus_system import BonusCalculator, BonusType
    
    pol_res = await session.execute(
        select(Politician).where(Politician.district_id == action.district_id)
    )
    politician = pol_res.scalars().first()
    
    if not politician or not politician.bonuses_penalties:
        return
    
    # Получаем название района
    district_res = await session.execute(
        select(District).where(District.id == action.district_id)
    )
    district = district_res.scalars().first()
    district_name = district.name if district else None
    
    # Вычисляем бонусы для действия
    bonuses = BonusCalculator.calculate_action_bonuses(
        action_kind=action.kind,
        district_id=action.district_id,
        district_name=district_name,
        politician=politician,
        action_type=action.type.value
    )
    
    # Применяем бонусы к ресурсам действия
    for bonus_type, bonus_value in bonuses.items():
        if bonus_value == 0:
            continue
            
        if bonus_type == BonusType.FORCE:
            action.force = max(0, action.force + bonus_value)
        elif bonus_type == BonusType.MONEY:
            action.money = max(0, action.money + bonus_value)
        elif bonus_type == BonusType.INFLUENCE:
            action.influence = max(0, action.influence + bonus_value)
        elif bonus_type == BonusType.INFORMATION:
            action.information = max(0, action.information + bonus_value)
        
        logging.info(f"Применен бонус при создании действия {action.id}: +{bonus_value} {bonus_type.value}")


@option("action_district_menu_back")
async def action_district_menu_back(cb: types.CallbackQuery, state: FSMContext):
    await ActionsScreen().run(message=cb.message, actor=cb.from_user, state=state)
    await cb.answer()


@option("action_district_menu_next")
async def action_district_menu_next(cb: types.CallbackQuery, state: FSMContext, **kwargs):
    action_kind = kwargs.get("action")
    await DistrictActionList().run(message=cb.message, actor=cb.from_user, state=state, move="next", action=action_kind)
    await cb.answer()


@option("action_district_menu_prev")
async def action_district_menu_prev(cb: types.CallbackQuery, state: FSMContext, **kwargs):
    action_kind = kwargs.get("action")
    await DistrictActionList().run(message=cb.message, actor=cb.from_user, state=state, move="prev", action=action_kind)
    await cb.answer()


@option("action_district_menu_pick")
async def action_district_menu_pick(cb: types.CallbackQuery, state: FSMContext, **kwargs):
    action_kind = kwargs.get("action")
    data = await state.get_data()
    idx = int(data.get("district_list_index", 0))
    logging.info("action_district_menu_pick: action_kind=%s, district_list_index=%s", action_kind, idx)
    async with get_session() as session:
        user = await User.get_by_tg_id(session, cb.from_user.id)

        rows = (
            await session.execute(
                select(District)
                .options(selectinload(District.owner))
                .order_by(District.id)
            )
        ).scalars().all()

        if not rows:
            await cb.answer("Нет доступных районов.", show_alert=True)
            return

        # 3) Безопасно нормализуем индекс и берём выбранный район
        idx = idx % len(rows)
        picked = rows[idx]
        district_id = picked.id

        # 4) Лог/действие с выбранным районом
        logging.info("Picked district: id=%s name=%s (idx=%s of %s) for action_kind=%s",
                     district_id, picked.name, idx, len(rows), action_kind)
        
        # Логируем все доступные округа для отладки
        all_districts = [(d.id, d.name) for d in rows]
        logging.info("Available districts: %s", all_districts)

        action_type = ActionType.INDIVIDUAL if action_kind in ["defend", "attack"] else ActionType.SCOUT_DISTRICT
        information = 1 if action_kind in ["scout"] else 0
        action = await Action.create(
            session,
            owner_id=user.id,
            status=ActionStatus.DRAFT,
            kind=action_kind,
            title=f"{str(action_kind)} {picked.name}" if district_id else f"{str(action_type.name).title()} (no district)",
            district_id=district_id,
            type=action_type,
            force=0,
            money=0,
            influence=0,
            information=information
        )
        
        # Применяем бонусы от политиков района при создании действия
        await _apply_politician_bonuses_on_create(session, action)

    await SettingsActionScreen().run(message=cb.message, actor=cb.from_user, state=state, move="prev",
                                     action_id=action.id, action=action)
    await cb.answer()
