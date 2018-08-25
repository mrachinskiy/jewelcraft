# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2018  Mikhail Rachinskiy
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####


import bpy


_ru = {
    "*": {
        # Interface
        "Asset Manager": "Менеджер ассетов",
        "Asset name from active object": "Использовать имя активного объекта для нового ассета",
        "Display asset name": "Показывать название ассета",
        "Product Report": "Отчёт изделия",
        "Report Language": "Язык отчёта",
        "Report Language:": "Язык отчёта:",
        "Display in a new window": "Отобразить в новом окне",
        "Save to file": "Сохранить в файл",
        "Use custom library folder": "Использовать пользовательский каталог библиотеки",
        "Gems": "Камни",
        "Assets": "Ассеты",
        "Select Gems By...": "Выделить камни по...",
        "Jeweling": "Вставки",
        "Weighting": "Оценка веса",
        "Weighting Set": "Набор материалов",
        "Hide default sets": "Спрятать стандартные наборы",
        "[JewelCraft] Precious": "[JewelCraft] Драгоценные",
        "[JewelCraft] Precious RU (ГОСТ 30649-99)": "[JewelCraft] Драгоценные RU (ГОСТ 30649-99)",
        "[JewelCraft] Base": "[JewelCraft] Недрагоценные",
        "Sizes": "Размеры",
        "Prongs": "Крапана",
        "Cutter": "Выборка",
        "Library Folder Path": "Путь к каталогу библиотеки",
        "Widgets": "Виджеты",
        "Selection only": "Только выделение",
        "Use overrides": "Использовать переопределения",
        "Overrides only": "Только переопределения",
        "Widget Color": "Цвет виджета",
        "Line Width": "Ширина линии",
        "Show composition": "Показать состав",
        "Show density": "Показать плотность",
        "Materials list": "Список материалов",
        "Composition": "Состав",
        # Popup dialogs
        "Asset Name": "Название ассета",
        "Category Name": "Название категории",
        "Set Name": "Название набора",
        "Curvature Scale": "Масштаб кривизны",
        # Operator redo
        "Use Automated Presets": "Использовать автоматические пресеты",
        "Prong Number": "Количество корнеров",
        "Deformations": "Деформации",
        "Detalization": "Детализация",
        "Intersection": "Пересечение",
        "Bump Scale": "Масштаб выпуклости",
        "Diameter": "Диаметр",
        "Size Offset": "Отступ размера",
        "Girdle": "Рундист",
        "Hole": "Отверстие",
        "Top/Culet": "Верх/Калетта",
        "Handle": "Рукоять",
        "Curve Seat": "Изгиб посадочного места",
        "Curve Profile": "Изгиб контура",
        "Bevel Corners": "Фаска углов",
        "Length Offset": "Отступ длины",
        "Width Offset": "Отступ ширины",
        "Position Offset": "Отступ позиции",
        "Start Up": "Начало сверху",
        "Adjust Rotation": "Регулировать вращение",
        "Mirror Axis": "Оси отражения",
        # Tooltips
        "Add gemstone to the scene": "Добавить камень в сцену",
        "Edit selected gems": "Редактировать выделенные камни",
        "Commonly used precious alloys, physical properties taken directly from suppliers": "Распространённые драгоценные сплавы, физические свойства взяты напрямую у поставщиков",
        "Set of precious alloys according to Russian regulations": "Драгоценные сплавы согласно ГОСТ 30649-99",
        "Set of base metal alloys, physical properties taken directly from suppliers": "Сплавы из недрагоценных металлов, физические свойства взяты напрямую у поставщиков",
        "Display product report in new window": "Отобразить отчёт изделия в новом окне",
        "Save product report to file in project folder": "Сохранить отчёт изделия в файл в каталоге проекта",
        "Product report language": "Язык отчёта изделия",
        "Use user preferences language setting": "Использовать язык заданный в настройках пользователя",
        "Object for ring inner diameter reference": "Объект для определения внутреннего диаметра кольца",
        "Object for shank width and height reference": "Объект для определения ширины и толщины шинки",
        "Object for dimensions reference": "Объект для определения габаритов изделия",
        "Object for weight reference": "Объект для определения веса изделия",
        "Save product report to text file": "Сохранить отчёт изделия в текстовый файл",
        "Select gems by trait": "Выделить камни по характеристике",
        "Select duplicated gems (located in the same spot)\nWARNING: it does not work with dupli-faces, objects only": "Выделить дубликаты (находящиеся на одной координате)\nПРЕДУПРЕЖДЕНИЕ: не работает с dupli-faces, только с объектами",
        "Search stone by name": "Искать камень по названию",
        "Search asset by name": "Искать ассет по названию",
        "Scatter selected object along active curve": "Распределить выделенный объект по активной кривой",
        "Redistribute selected objects along curve": "Перераспределить выделенные объекты по кривой",
        "Display weight and volume for selected mesh objects": "Показать вес и объём выделенных mesh объектов",
        "Create dupli-face for selected objects": "Создать dupli-face для выделенных объектов",
        "Create size curve": "Создать размерную кривую",
        "Stretch deformed objects along curve, also works in Edit Mode with selected vertices": "Растянуть деформированный объект по кривой, также работает в режиме редактирования с выделенными вершинами",
        "Display curve length": "Показать длину кривой",
        "Move deformed object over or under the curve": "Переместить деформированные объекты под или над кривой",
        "Mirror selected objects around one or more axes, keeping object data linked": "Отразить выделенные объекты относительно одной или нескольких осей, сохраняя связь данных объекта",
        "Project selected objects onto active object using Lattice": "Проецировать выделенные объекты на активный объект с помощью Lattice",
        "Deform active object profile with Lattice": "Деформировать профиль активного объекта с помощью Lattice",
        "Use automatically generated presets, discards user edits or presets": "Использовать автоматически сгенерированные пресеты, сбрасывает пользовательское редактирование",
        "Create prongs for selected gems": "Создать корнера для выделенных камней",
        "Create cutter for selected gems": "Создать выборку для выделенных камней",
        "Make curve start at the top": "Расположить начало кривой сверху",
        "Density g/cm³": "Плотность г/см³",
        "Set of materials for weighting": "Набор материалов для оценки веса",
        "Create category": "Создать категорию",
        "Rename category": "Переименовать категорию",
        "Refresh asset UI": "Обновить интерфейс ассетов",
        "Add selected objects to asset library": "Добавить выделенные объекты в библиотеку ассетов",
        "Rename asset": "Переименовать ассет",
        "Remove asset from library": "Удалить ассет из библиотеки",
        "Replace current asset with selected objects": "Заменить текущий ассет выделенными объектами",
        "Replace asset preview image": "Заменить превью ассета",
        "Import selected asset": "Импортировать выбранный ассет",
        "Asset category": "Категория ассетов",
        "Set custom asset library folder, if disabled the default library folder will be used": "Указать пользовательский каталог библиотеки ассетов, если отключено, то используется стандартный каталог",
        "Custom library folder path": "Путь к пользовательскому каталогу библиотеки",
        "Display asset name in Tool Shelf": "Показывать название ассета в панели инструментов",
        "Use active object name when creating new asset": "Использовать имя активного объекта при создании нового ассета",
        "Enable widgets drawing": "Активировать отображение виджетов",
        "Draw widgets only for selected objects": "Отображать виджеты только для выделенных объектов",
        "Use object defined widget overrides": "Использовать переопределения виджетов заданные на объектах",
        "Display only object defined widget overrides": "Отображать только виджеты с переопределениями заданными на объектах",
        "Draw widgets in front of objects": "Отображать виджеты поверх объектов",
        "Override widget display properties for selected objects": "Переопределить отображение виджетов для выделенных объектов",
        "Remove widget override properties from selected objects": "Удалить настройки переопределяющие отображение виджетов с выделенных объектов",
        "Add new material to the list": "Добавить новый материал в список",
        "Remove material from the list": "Удалить материал из списка",
        "Display material density in the list": "Отображать в списке плотность материала",
        "Display material composition in the list": "Отображать в списке состав материала",
        "Create weighting set from materials list": "Создать набор материалов из списка материалов",
        "Remove weighting set": "Удалить набор материалов",
        "Rename weighting set": "Переименовать набор материалов",
        "Load weighting set to the materials list by replacing existing materials": "Загрузить набор материалов в список материалов, заменив текущие материалы",
        "Append weighting set at the end of the current materials list": "Присоеденить набор материалов в конец текущего списока материалов",
        "Hide default JewelCraft sets from weighting sets menu": "Скрыть стандартные наборы материалов JewelCraft из меню",
        "Replace selected weighting set with current materials list": "Заменить активный набор материалов текущим списком материалов",
        "Material name": "Название материала",
        "Material composition": "Состав материала",
        "Use one-dimensional lattice for even deformation": "Использовать одномерный Lattice для равномерной деформации",
        "Use two-dimensional lattice for proportional deformation": "Использовать двумерный Lattice для пропорциональной деформации",
        "Scale selected objects to given size": "Масштабировать выделенные объекты в заданный размер",
        "Move each object individually": "Переместить каждый объект по отдельности",
        "Enable material for weighting and product report": "Использовать материал для оценки веса и отчёта изделия",
        "Clear materials list": "Очистить список материалов",
        # Reports
        "WARNING": "ПРЕДУПРЕЖДЕНИЕ",
        "Possible gem dupli-face leftovers": "Возможные остатки Dupli-face камней",
        "Hidden gems (use Show Hidden/Alt H)": "Скрытые камни (используйте Show Hidden/Alt H)",
        "Duplicated gems": "Дублируемые камни",
        "Deprecated gem IDs (use Convert Deprecated Gem IDs from Operator Search menu)": "Устаревшие идентификаторы камней (используйте Convert Deprecated Gem IDs из меню Operator Search)",
        "Unknown gem IDs, carats are not calculated for marked gems (*)": "Неизвестные идентификаторы камней, караты не рассчитываются для отмеченных камней (*)",
        "Curve Length": "Длина кривой",
        "{} duplicates found": "{} дубликатов обнаружено",
        "Text file successfully created in the project folder": "Текстовый файл успешно создан в каталоге проекта",
        "Could not create text file, project folder does not exist": "Не удалось создать текстовый файл, каталог проекта не существует",
        "At least two objects must be selected": "Как минимум два объекта должны быть выделены",
        "At least one gem object must be selected": "Как минимум один объект камня должен быть выделен",
        "At least one mesh object must be selected": "Как минимум один mesh объект должен быть выделен",
        "Active object must be a curve": "Активный объект должен быть кривой",
        "Active object does not have a Follow Path constraint": "Активный объект не имеет ограничение Follow Path",
        "File not found": "Файл не найден",
        "Name must be specified": "Имя должно быть указано",
        # Cuts
        "Round": "Кр-57",
        "Oval": "Овал",
        "Cushion": "Кушон",
        "Pear": "Груша",
        "Marquise": "Маркиз",
        "Princess": "Принцесса",
        "Baguette": "Багет",
        "Square": "Квадрат",
        "Asscher": "Ашер",
        "Radiant": "Радиант",
        "Flanders": "Фландерс",
        "Octagon": "Октагон",
        "Heart": "Сердце",
        "Trillion": "Триллион",
        "Trilliant": "Триллиант",
        "Triangle": "Треугольник",
        # Stones
        "Alexandrite": "Александрит",
        "Amethyst": "Аметист",
        "Aquamarine": "Аквамарин",
        "Citrine": "Цитрин",
        "Cubic Zirconia": "Фианит",
        "Diamond": "Бриллиант",
        "Emerald": "Изумруд",
        "Garnet": "Гранат",
        "Morganite": "Морганит",
        "Peridot": "Хризолит",
        "Quartz": "Кварц",
        "Ruby": "Рубин",
        "Sapphire": "Сапфир",
        "Spinel": "Шпинель",
        "Tanzanite": "Танзанит",
        "Topaz": "Топаз",
        "Tourmaline": "Турмалин",
        "Zircon": "Циркон",
        # Alloys
        "Yellow Gold 24K": "Жёлтое золото 24 кар",
        "Yellow Gold 22K": "Жёлтое золото 22 кар",
        "Yellow Gold 18K": "Жёлтое золото 18 кар",
        "Yellow Gold 14K": "Жёлтое золото 14 кар",
        "Yellow Gold 10K": "Жёлтое золото 10 кар",
        "White Gold 18K Pd": "Белое золото 18 кар Pd",
        "White Gold 18K Ni": "Белое золото 18 кар Ni",
        "White Gold 14K Pd": "Белое золото 14 кар Pd",
        "White Gold 14K Ni": "Белое золото 14 кар Ni",
        "White Gold 10K": "Белое золото 10 кар",
        "Rose Gold 18K": "Красное золото 18 кар",
        "Rose Gold 14K": "Красное золото 14 кар",
        "Rose Gold 10K": "Красное золото 10 кар",
        "Yellow Gold 999": "Жёлтое золото 999",
        "Yellow Gold 958": "Жёлтое золото 958",
        "Yellow Gold 750": "Жёлтое золото 750",
        "Yellow Gold 585": "Жёлтое золото 585",
        "Yellow Gold 375": "Жёлтое золото 375",
        "White Gold 750 Pd": "Белое золото 750 Pd",
        "White Gold 750 Ni": "Белое золото 750 Ni",
        "White Gold 585 Pd": "Белое золото 585 Pd",
        "White Gold 585 Ni": "Белое золото 585 Ni",
        "Red Gold 585": "Красное золото 585",
        "Red Gold 375": "Красное золото 375",
        "Platinum 950": "Платина 950",
        "Platinum 900": "Платина 900",
        "Palladium 950": "Палладий 950",
        "Silver 925": "Серебро 925",
        "Silver Sterling": "Серебро стерлинг",
        "Brass": "Латунь",
        "Bronze": "Бронза",
        "Steel Stainless": "Сталь нержавеющая",
        "Titanium": "Титан",
        # Product report
        "Size": "Размер",
        "Shank": "Шинка",
        "Dimensions": "Габариты",
        "Weight": "Вес",
        "Volume": "Объём",
        "Settings": "Вставки",
        "Gem": "Камень",
        "Cut": "Огранка",
        "Qty": "Количество",
        # Units
        "pcs": "шт.",
        "mm": "мм",
        "mm³": "мм³",
        "g": "г",
        "ct.": "кар",
    },
    "JewelCraft": {
        "Cut": "Огранка",
        "Dimensions": "Габариты",
        "Round": "Кр-57",
    },
    "Dative": {
        "Size": "Размеру",
        "Stone": "Камню",
        "Cut": "Огранке",
    },
    "Operator": {
        "Add Gem": "Создать камень",
        "Doubles": "Дубликаты",
        "Curve Scatter": "Распределить по кривой",
        "Prongs": "Крапана",
        "Cutter": "Выборка",
        "Make Dupli-face": "Создать Dupli-face",
        "Lattice Project": "Lattice проекция",
        "Lattice Profile": "Lattice профиль",
        "Size Curve": "Размерная кривая",
        "Stretch": "Растянуть",
        "Curve Length": "Длина кривой",
        "Product Report": "Отчёт изделия",
        "Open Library Folder": "Открыть каталог библиотеки",
        "Import Asset": "Импортировать ассет",
        "Rename": "Переименовать",
        "Replace Asset": "Заменить ассет",
        "Replace Preview": "Заменить превью",
        "Create Category": "Создать категорию",
        "Rename Category": "Переименовать категорию",
        "Rename Asset": "Переименовать ассет",
        "Remove Asset": "Удалить ассет",
        "Replace Asset Preview": "Заменить превью ассета",
        "Override": "Переопределить",
        "Clear List": "Очистить список",
        "Add New Material": "Добавить новый материал",
        "Create Set": "Создать набор",
        "Replace Set": "Заменить набор",
        "Remove Set": "Удалить набор",
        "Rename Set": "Переименовать набор",
    },
}


# Translation dictionary
# -----------------------------


def translation_dict(x):
    d = {}

    for ctxt, msgs in x.items():

        for msg_key, msg_translation in msgs.items():
            d[(ctxt, msg_key)] = msg_translation

    return d


DICTIONARY = {"ru_RU": translation_dict(_ru)}

del _ru


# Utility
# -----------------------------


def iface_lang():
    system = bpy.context.user_preferences.system

    if system.use_international_fonts and system.use_translate_interface:
        return system.language

    return "DEFAULT"


def gettext_prep(text, ctxt="*"):
    """gettext implementation for Product Report"""

    lang = bpy.context.user_preferences.addons[__package__].preferences.product_report_lang

    if lang == "AUTO":
        lang = bpy.app.translations.locale

    if lang in DICTIONARY:
        return DICTIONARY[lang].get((ctxt, text), text)

    return text
