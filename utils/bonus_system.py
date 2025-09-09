"""
Система бонусов и штрафов для владельцев районов.

Парсит текстовые описания бонусов из поля bonuses_penalties политиков
и применяет их в различных игровых ситуациях.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

log = logging.getLogger(__name__)


class BonusType(Enum):
    """Типы бонусов/штрафов."""
    CONTROL_POINTS = "control_points"  # ОК - очки контроля
    FORCE = "force"  # Сила
    MONEY = "money"  # Деньги
    INFLUENCE = "influence"  # Влияние
    INFORMATION = "information"  # Информация


class BonusCondition(Enum):
    """Условия применения бонуса."""
    DEFENSE_DISTRICT = "defense_district"  # При защите района
    ATTACK_DISTRICT = "attack_district"  # При атаке района
    DEFENSE_ANY = "defense_any"  # При защите любого района
    ATTACK_ANY = "attack_any"  # При атаке любого района
    COOPERATIVE_ACTION = "cooperative_action"  # При кооперативных действиях
    MASS_ACTION = "mass_action"  # При массовых акциях
    IDEOLOGY_THRESHOLD = "ideology_threshold"  # При определенной идеологии района
    CYCLE_DEFENSE = "cycle_defense"  # За защиту района в цикл


@dataclass
class BonusRule:
    """Правило бонуса/штрафа."""
    bonus_type: BonusType
    value: int  # Может быть отрицательным для штрафов
    condition: BonusCondition
    district_name: Optional[str] = None  # Для специфических районов
    ideology_threshold: Optional[int] = None  # Для условий по идеологии
    description: str = ""


class BonusParser:
    """Парсер текстовых описаний бонусов."""
    
    # Регулярные выражения для парсинга
    PATTERNS = {
        # ОК (очки контроля)
        r'\+(\d+)\s*ОК': BonusType.CONTROL_POINTS,
        r'(\d+)\s*ОК': BonusType.CONTROL_POINTS,
        
        # Сила
        r'\+(\d+)\s*Силы': BonusType.FORCE,
        r'(\d+)\s*Силы': BonusType.FORCE,
        r'\+(\d+)\s*силы': BonusType.FORCE,
        r'(\d+)\s*силы': BonusType.FORCE,
        
        # Деньги
        r'\+(\d+)\s*Денег': BonusType.MONEY,
        r'(\d+)\s*Денег': BonusType.MONEY,
        r'\+(\d+)\s*денег': BonusType.MONEY,
        r'(\d+)\s*денег': BonusType.MONEY,
        
        # Влияние
        r'\+(\d+)\s*Влияния': BonusType.INFLUENCE,
        r'(\d+)\s*Влияния': BonusType.INFLUENCE,
        r'\+(\d+)\s*влияния': BonusType.INFLUENCE,
        r'(\d+)\s*влияния': BonusType.INFLUENCE,
        
        # Информация
        r'\+(\d+)\s*Информации': BonusType.INFORMATION,
        r'(\d+)\s*Информации': BonusType.INFORMATION,
        r'\+(\d+)\s*информации': BonusType.INFORMATION,
        r'(\d+)\s*информации': BonusType.INFORMATION,
    }
    
    # Условия применения
    CONDITION_PATTERNS = {
        r'при\s+Защите\s+(\w+)': (BonusCondition.DEFENSE_DISTRICT, 'district'),
        r'при\s+защите\s+(\w+)': (BonusCondition.DEFENSE_DISTRICT, 'district'),
        r'при\s+атаке\s+на\s+(\w+)': (BonusCondition.ATTACK_DISTRICT, 'district'),
        r'при\s+Атаке\s+на\s+(\w+)': (BonusCondition.ATTACK_DISTRICT, 'district'),
        r'при\s+заявках\s+на\s+Защиту': BonusCondition.DEFENSE_ANY,
        r'при\s+заявках\s+на\s+защиту': BonusCondition.DEFENSE_ANY,
        r'при\s+Кооперативных\s+заявках': BonusCondition.COOPERATIVE_ACTION,
        r'при\s+кооперативных\s+заявках': BonusCondition.COOPERATIVE_ACTION,
        r'при\s+массовых\s+акциях': BonusCondition.MASS_ACTION,
        r'при\s+Массовых\s+акциях': BonusCondition.MASS_ACTION,
        r'в\s+районах\s+с\s+(\+?\d+)\s+и\s+больше': (BonusCondition.IDEOLOGY_THRESHOLD, 'threshold'),
        r'за\s+каждую\s+заявку\s+Атака/Защита': BonusCondition.DEFENSE_ANY,  # Упрощение
    }
    
    # Маппинг названий районов для нормализации
    DISTRICT_NAME_MAPPING = {
        'подбары': 'подбара',
        'подбара': 'подбара',
        'подбару': 'подбара',  # Добавляем вариант в винительном падеже
        'stari grad': 'stari grad',
        'liman': 'liman',
        'rotkvar': 'rotkvar',
        'petrovaradin': 'petrovaradin',
        'sajmište': 'sajmište',
        'grbavica': 'grbavica',
    }
    
    @classmethod
    def parse_bonuses(cls, text: str) -> List[BonusRule]:
        """
        Парсит текстовое описание бонусов и возвращает список правил.
        
        Примеры:
        - "+5 ОК за каждую заявку Атака/Защита" -> BonusRule(CONTROL_POINTS, 5, DEFENSE_ANY)
        - "+3 Силы при Защите Подбары" -> BonusRule(FORCE, 3, DEFENSE_DISTRICT, "Подбара")
        - "+5 ОК в районах с +3 и больше" -> BonusRule(CONTROL_POINTS, 5, IDEOLOGY_THRESHOLD, ideology_threshold=3)
        """
        if not text or not text.strip():
            return []
        
        rules = []
        text = text.strip()
        
        # Разбиваем на предложения по запятым
        sentences = re.split(r'[,;]', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Ищем бонусы в предложении
            for pattern, bonus_type in cls.PATTERNS.items():
                match = re.search(pattern, sentence, re.IGNORECASE)
                if match:
                    value = int(match.group(1))
                    
                    # Определяем знак (положительный или отрицательный)
                    if sentence.startswith('-'):
                        value = -value
                    
                    # Ищем условие применения
                    condition = BonusCondition.DEFENSE_ANY  # По умолчанию
                    district_name = None
                    ideology_threshold = None
                    
                    for cond_pattern, cond_info in cls.CONDITION_PATTERNS.items():
                        cond_match = re.search(cond_pattern, sentence, re.IGNORECASE)
                        if cond_match:
                            if isinstance(cond_info, tuple):
                                condition, param_type = cond_info
                                if param_type == 'district':
                                    district_name = cls._normalize_district_name(cond_match.group(1))
                                elif param_type == 'threshold':
                                    ideology_threshold = int(cond_match.group(1))
                            else:
                                condition = cond_info
                            break
                    
                    rule = BonusRule(
                        bonus_type=bonus_type,
                        value=value,
                        condition=condition,
                        district_name=district_name,
                        ideology_threshold=ideology_threshold,
                        description=sentence
                    )
                    rules.append(rule)
                    log.debug(f"Парсинг бонуса: {rule}")
                    break  # Нашли бонус в этом предложении, переходим к следующему
        
        return rules
    
    @classmethod
    def _normalize_district_name(cls, name: str) -> str:
        """Нормализует название района для сравнения."""
        if not name:
            return name
        normalized = name.lower().strip()
        return cls.DISTRICT_NAME_MAPPING.get(normalized, normalized)


class BonusCalculator:
    """Калькулятор бонусов для различных игровых ситуаций."""
    
    @staticmethod
    def calculate_defense_bonuses(
        district_id: int,
        politician: Optional[Any],
        district_name: str,
        district_ideology: int
    ) -> Dict[BonusType, int]:
        """
        Вычисляет бонусы за защиту района в цикл.
        
        Args:
            district_id: ID района
            politician: Объект политика
            district_name: Название района
            district_ideology: Идеология района (если есть)
            
        Returns:
            Словарь с бонусами по типам
        """
        bonuses = {bt: 0 for bt in BonusType}
        
        if not politician or not politician.bonuses_penalties:
            return bonuses
        
        rules = BonusParser.parse_bonuses(politician.bonuses_penalties)
        
        for rule in rules:
            # Бонусы за защиту района в цикл (фиксированные)
            if rule.condition == BonusCondition.DEFENSE_ANY:
                bonuses[rule.bonus_type] += rule.value
                log.debug(f"Бонус за защиту района {district_name}: +{rule.value} {rule.bonus_type.value}")
            elif rule.condition == BonusCondition.IDEOLOGY_THRESHOLD:
                if rule.ideology_threshold and district_ideology >= rule.ideology_threshold:
                    bonuses[rule.bonus_type] += rule.value
                    log.debug(f"Бонус по идеологии района {district_name}: +{rule.value} {rule.bonus_type.value}")
        
        return bonuses
    
    @staticmethod
    def calculate_action_bonuses(
        action_kind: str,
        district_id: Optional[int],
        district_name: Optional[str],
        politician: Optional[Any],
        action_type: str = "individual"
    ) -> Dict[BonusType, int]:
        """
        Вычисляет бонусы для действия.
        
        Args:
            action_kind: Тип действия (attack, defense, etc.)
            district_id: ID района
            district_name: Название района
            politician: Объект политика
            action_type: Тип действия (individual, collective, support)
            
        Returns:
            Словарь с бонусами по типам
        """
        bonuses = {bt: 0 for bt in BonusType}
        
        if not politician or not politician.bonuses_penalties:
            return bonuses
        
        rules = BonusParser.parse_bonuses(politician.bonuses_penalties)
        
        for rule in rules:
            apply_bonus = False
            
            # Проверяем условия применения
            if rule.condition == BonusCondition.DEFENSE_DISTRICT:
                apply_bonus = (action_kind == "defense" and 
                             (not rule.district_name or 
                              BonusParser._normalize_district_name(rule.district_name) == 
                              BonusParser._normalize_district_name(district_name or "")))
            elif rule.condition == BonusCondition.ATTACK_DISTRICT:
                apply_bonus = (action_kind == "attack" and 
                             (not rule.district_name or 
                              BonusParser._normalize_district_name(rule.district_name) == 
                              BonusParser._normalize_district_name(district_name or "")))
            elif rule.condition == BonusCondition.DEFENSE_ANY:
                apply_bonus = action_kind == "defense"
            elif rule.condition == BonusCondition.ATTACK_ANY:
                apply_bonus = action_kind == "attack"
            elif rule.condition == BonusCondition.COOPERATIVE_ACTION:
                apply_bonus = action_type == "collective"
            elif rule.condition == BonusCondition.MASS_ACTION:
                # Упрощение: считаем коллективные действия массовыми
                apply_bonus = action_type == "collective"
            
            if apply_bonus:
                bonuses[rule.bonus_type] += rule.value
                log.debug(f"Бонус для действия {action_kind}: +{rule.value} {rule.bonus_type.value}")
        
        return bonuses


# Предустановленные бонусы из таблицы (для тестирования)
PRESET_BONUSES = {
    "Слободан Милошевич": "+5 ОК за каждую заявку Атака/Защита",
    "Зоран Джинджич": "+5 ОК в районах с +3 и больше",
    "Желько «Аркан» Ражнатович": "+3 Силы при Защите Подбары, -3 Силы при атаке на Подбару",
    "Борислав Милошевич": "Способны вводить санкции, бонус к защите районов",
    "Небойша Павкович": "+5 ОК при заявках на Защиту в любых районах",
    "Миролюб Лабус": "+3 Денег при Кооперативных заявках, -3 Денег при любых Атаках",
    "Чедомир «Чеда»": "+5 ОК при массовых акциях, штраф к силовому контролю"
}
