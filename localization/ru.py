# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2019  Mikhail Rachinskiy
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


dictionary = {
    "*": {
        # Interface
        "Asset Manager": "Менеджер ассетов",
        "Display Asset Name": "Показывать название ассета",
        "Product Report": "Отчёт изделия",
        "Report Language": "Язык отчёта",
        "Save To File": "Сохранить в файл",
        "Use Custom Library Folder": "Использовать пользовательский каталог библиотеки",
        "Gems": "Камни",
        "Assets": "Ассеты",
        "Select Gems By...": "Выделить камни по...",
        "Jeweling": "Вставки",
        "Weighting": "Оценка веса",
        "Weighting Set": "Набор материалов",
        "Hide Default Sets": "Спрятать стандартные наборы",
        "[JewelCraft] Precious": "[JewelCraft] Драгоценные",
        "[JewelCraft] Precious RU (ГОСТ 30649-99)": "[JewelCraft] Драгоценные RU (ГОСТ 30649-99)",
        "[JewelCraft] Base": "[JewelCraft] Недрагоценные",
        "Prongs": "Крапана",
        "Cutter": "Выборка",
        "Library Folder Path": "Путь к каталогу библиотеки",
        "Widgets": "Виджеты",
        "Use Overrides": "Использовать переопределения",
        "Widget Color": "Цвет виджета",
        "Line Width": "Ширина линии",
        "Show Composition": "Показать состав",
        "Show Density": "Показать плотность",
        "Materials list": "Список материалов",
        "Composition": "Состав",
        "Warnings": "Предупреждения",
        "Hidden Gems": "Скрытые камни",
        "Show All": "Показать все",
        "Scene scale is not optimal": "Масштаб сцены не оптимален",
        "Unsupported unit system": "Неподдерживаемая система единиц измерения",
        "Overlapping Gems": "Пересекающиеся камни",
        "Limit By Selection": "Ограничить выделением",
        "Save To Image": "Сохранить в изображение",
        "Gem Map": "Карта камней",
        "Gem Table": "Таблица камней",
        "Gem Size": "Размер камня",
        "Viewport Text Size": "Размер текста вьюпорта",
        "Weight": "Вес",
        # Operator popup
        "Asset Name": "Название ассета",
        "Category Name": "Название категории",
        "Set Name": "Название набора",
        "Curvature Scale": "Масштаб кривизны",
        "Prong Number": "Количество корнеров",
        "Detalization": "Детализация",
        "Intersection": "Пересечение",
        "Bump Scale": "Масштаб выпуклости",
        "Diameter": "Диаметр",
        "Size Offset": "Отступ размера",
        "Girdle": "Рундист",
        "Hole": "Отверстие",
        "Culet": "Калетта",
        "Handle": "Рукоять",
        "Curve Seat": "Изгиб посадочного места",
        "Curve Profile": "Изгиб контура",
        "Bevel Corners": "Фаска углов",
        "Length Offset": "Отступ длины",
        "Width Offset": "Отступ ширины",
        "Position Offset": "Отступ позиции",
        "Start Up": "Начало сверху",
        "Mirror Axis": "Оси отражения",
        "Select Children": "Выделить потомков",
        "Parent to selected": "Привязать к выделению",
        "Use 3D Cursor": "Использовать 3D курсор",
        "Collection Name": "Имя коллекции",
        "Ring Size": "Размер кольца",
        "USA": "США",
        "Britain": "Британия",
        "Swiss": "Швейцария",
        "Japan": "Япония",
        "Circumference": "Окружность",
        "Scatter (%)": "Распределение (%)",
        # Tooltips
        "Add gemstone to the scene": "Добавить камень в сцену",
        "Edit selected gems": "Редактировать выделенные камни",

        "Commonly used precious alloys, physical properties taken directly from suppliers":
            "Распространённые драгоценные сплавы, физические свойства взяты напрямую у поставщиков",

        "Set of precious alloys according to Russian regulations": "Драгоценные сплавы согласно ГОСТ 30649-99",

        "Set of base metal alloys, physical properties taken directly from suppliers":
            "Сплавы из недрагоценных металлов, физические свойства взяты напрямую у поставщиков",

        "Save product report to file in project folder": "Сохранить отчёт изделия в файл в каталоге проекта",
        "Product report language": "Язык отчёта изделия",
        "Use user preferences language setting": "Использовать язык заданный в настройках пользователя",
        "Select gems by trait": "Выделить камни по характеристике",
        "Search stone by name": "Искать камень по названию",
        "Search asset by name": "Искать ассет по названию",
        "Scatter selected object along active curve": "Распределить выделенный объект по активной кривой",
        "Redistribute selected objects along curve": "Перераспределить выделенные объекты по кривой",

        "Display weight and volume for selected mesh objects":
            "Показать вес и объём выделенных mesh объектов",

        "Create instance face for selected objects": "Создать instance face для выделенных объектов",
        "Create size curve": "Создать размерную кривую",

        (
            "Stretch deformed objects along curve on X axis, "
            "also works in Edit Mode with selected vertices"
        ): (
            "Растянуть деформированный объект вдоль кривой по оси X, "
            "также работает в режиме редактирования с выделенными вершинами"
        ),

        "Display curve length": "Показать длину кривой",

        "Move deformed object over or under the curve":
            "Переместить деформированные объекты под или над кривой",

        "Mirror selected objects around one or more axes, keeping object data linked":
            "Отразить выделенные объекты относительно одной или нескольких осей, сохраняя связь данных объекта",

        "Project selected objects onto active object using Lattice":
            "Проецировать выделенные объекты на активный объект с помощью Lattice",

        "Deform active object profile with Lattice":
            "Деформировать профиль активного объекта с помощью Lattice",

        "Create prongs for selected gems\n"
        "(Shortcut: hold Ctrl when using the tool to avoid properties reset)":
            "Создать корнера для выделенных камней\n"
            "(Горячая клавиша: удерживайте Ctrl при использовании инструмента, чтобы избежать сброса параметров)",

        "Create cutter for selected gems\n"
        "(Shortcut: hold Ctrl when using the tool to avoid properties reset)":
            "Создать выборку для выделенных камней\n"
            "(Горячая клавиша: удерживайте Ctrl при использовании инструмента, чтобы избежать сброса параметров)",

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

        "Set custom asset library folder, if disabled the default library folder will be used": (
            "Указать пользовательский каталог библиотеки ассетов, если отключено, "
            "то используется стандартный каталог"
        ),

        "Custom library folder path": "Путь к пользовательскому каталогу библиотеки",
        "Display asset name in Tool Shelf": "Показывать название ассета в панели инструментов",
        "Enable widgets drawing": "Активировать отображение виджетов",
        "Use object defined widget overrides": "Использовать переопределения виджетов заданные на объектах",

        "Draw widgets in front of objects": "Отображать виджеты поверх объектов",

        "Override widget display properties for selected objects":
            "Переопределить отображение виджетов для выделенных объектов",

        "Remove widget override properties from selected objects":
            "Удалить настройки переопределяющие отображение виджетов с выделенных объектов",

        "Add new material to the list": "Добавить новый материал в список",
        "Display material density in the list": "Отображать в списке плотность материала",
        "Display material composition in the list": "Отображать в списке состав материала",
        "Create weighting set from materials list": "Создать набор материалов из списка материалов",
        "Remove weighting set": "Удалить набор материалов",
        "Rename weighting set": "Переименовать набор материалов",

        "Load weighting set to the materials list by replacing existing materials":
            "Загрузить набор материалов в список материалов, заменив текущие материалы",

        "Append weighting set at the end of the current materials list":
            "Присоеденить набор материалов в конец текущего списока материалов",

        "Hide default JewelCraft sets from weighting sets menu":
            "Скрыть стандартные наборы материалов JewelCraft из меню",

        "Replace selected weighting set with current materials list":
            "Заменить активный набор материалов текущим списком материалов",

        "Material name": "Название материала",
        "Material composition": "Состав материала",

        "Use one-dimensional lattice for even deformation":
            "Использовать одномерный Lattice для равномерной деформации",

        "Use two-dimensional lattice for proportional deformation":
            "Использовать двумерный Lattice для пропорциональной деформации",

        "Scale selected objects to given size": "Масштабировать выделенные объекты в заданный размер",
        "Move each object individually": "Переместить каждый объект по отдельности",

        "Enable material for weighting and product report":
            "Использовать материал для оценки веса и отчёта изделия",

        "Parent imported asset to selected objects (Shortcut: hold Alt when using the tool)": (
            "Привязать импортированный ассет к выделенным объектам "
            "(Горячая клавиша: удерживайте Alt при использовании инструмента)"
        ),

        "Select gems that are less than 0.1 mm distance from each other or overlapping":
            "Выделить перекрывающиеся камни или расположенные на расстоянии менее 0.1 мм друг от друга",

        "Display spacing widget for all visible gems": "Отображать виджет расстояния для всех видимых камней",

        "Set optimal unit settings for jewelry modelling":
            "Задать оптимальные настройки единиц измерения для моделирования ювелирных изделий",

        "Enable or disable given warning": "Включить или отключить данное предупреждение",

        "Compose gem table and map it to gems in the scene":
            "Составить таблицу камней и сопоставить её с камнями в сцене",

        "Present summary information about the product, including gems, sizes and weight":
            "Предоставить суммарную информацию об изделии, включая камни, размеры и вес",

        "Add a new measurement": "Добавить новый замер",
        "Remove selected item": "Удалить выбранный элемент",
        "Remove all list items": "Удалить все элементы списка",
        "Move selected item up/down in the list": "Переместить выбранный элемент вверх/вниз по списку",
        "Measured object": "Измеряемый объект",
        "Measurement type": "Тип замера",
        "Select material": "Выбрать материал",

        "Make collection instances in radial order\n"
        "(Shortcut: hold Alt when using the tool to use existing collection)":
            "Создать экземпляры коллекции в радиальном порядке\n"
            "(Горячая клавиша: удерживайте клавишу Alt при использовании инструмента "
            "для использования существующей коллекции)",

        "Include or exclude given column": "Включить или исключить данную колонку",

        # Reports
        "WARNING": "ПРЕДУПРЕЖДЕНИЕ",
        "Possible gem instance face leftovers": "Возможные остатки instance face камней",
        "Hidden gems": "Скрытые камни",

        "Deprecated gem IDs (use Convert Deprecated Gem IDs from Operator Search menu)":
            "Устаревшие идентификаторы камней (используйте Convert Deprecated Gem IDs из меню Operator Search)",

        "Unknown gem IDs, carats are not calculated for marked gems (*)":
            "Неизвестные идентификаторы камней, караты не рассчитываются для отмеченных камней (*)",

        "Curve Length": "Длина кривой",

        "At least two objects must be selected": "Как минимум два объекта должны быть выделены",
        "At least one gem object must be selected": "Как минимум один объект камня должен быть выделен",
        "At least one mesh object must be selected": "Как минимум один mesh объект должен быть выделен",
        "Active object must be a curve": "Активный объект должен быть кривой",

        "Selected objects do not have Follow Path constraint":
            "Выделенные объекты не имеют ограничение Follow Path",

        "File not found": "Файл не найден",
        "Name must be specified": "Имя должно быть указано",
        "Overlapping gems": "Пересекающиеся камни",
        "{} overlaps found": "{} пересечений обнаружено",
        "Optimal unit settings are in use": "Используются оптимальные настройки единиц измерения",
        "Volume": "Объём",
        "Settings": "Вставки",
        "Gem": "Камень",
        "Cut": "Огранка",
        "Qty": "Кол.",
        "Total (ct.)": "Всего (кар)",
        "Carats": "Караты",
        "Materials": "Материалы",
        "Additional Notes": "Дополнительные примечания",
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
        # Units
        "mm": "мм",
        "mm³": "мм³",
        "g": "г",
        "ct.": "кар",
        "pcs": "шт.",
    },
    "JewelCraft": {
        "Cut": "Огранка",
        "Round": "Кр-57",
        "Spacing": "Расстояние",
    },
    "Dative": {
        "Size": "Размеру",
        "Stone": "Камню",
        "Cut": "Огранке",
    },
    "Operator": {
        "Add Gem": "Создать камень",
        "Curve Scatter": "Распределить по кривой",
        "Prongs": "Крапана",
        "Cutter": "Выборка",
        "Make Instance Face": "Создать Instance Face",
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
        "Overlapping": "Пересекающиеся",
        "Set Units": "Задать единицы измерения",
        "Gem Map": "Карта Камней",
        "Append": "Добавить",
        "Add New Measurement": "Добавить новый замер",
        "Save To Preferences": "Сохранить в настройках",
        "Load From Preferences": "Загрузить из настроек",
    },
}
