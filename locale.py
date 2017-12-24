import bpy


lc_main = {
	# Interface
	'Asset Manager': 'Менеджер ассетов',
	'New asset name from active object': 'Использовать имя активного объекта для нового ассета',
	'Display asset name': 'Показывать название ассета',
	'Alloys Set': 'Набор сплавов',
	'Alloys Set:': 'Набор сплавов:',
	'Product Report': 'Отчёт изделия',
	'Report Language': 'Язык отчёта',
	'Report Language:': 'Язык отчёта:',
	'Common': 'Распространённые',
	'Display in a new window': 'Отобразить в новом окне',
	'Save to file': 'Сохранить в файл',
	'Use custom library folder': 'Использовать пользовательский каталог библиотеки',
	'Gems': 'Камни',
	'Assets': 'Ассеты',
	'Select Gems By...': 'Выделить камни по...',
	'Jeweling': 'Вставки',
	'Weighting': 'Оценка веса',
	'Custom Density': 'Произвольная плотность',
	'Sizes': 'Размеры',
	'Custom Material': 'Произвольный материал',
	'Replace:': 'Заменить:',
	'Report:': 'Отчёт:',
	'Prongs': 'Крапана',
	'Cutter': 'Выборка',
	'Library Folder Path': 'Путь к каталогу библиотеки',

	# Popup dialogs
	'Asset Name': 'Имя ассета',
	'Category Name': 'Имя категории',

	# Operator redo
	'Use Automated Presets': 'Использовать автоматические пресеты',
	'Prong Number': 'Количество корнеров',
	'Deformations': 'Деформации',
	'Detalization': 'Детализация',
	'Intersection': 'Пересечение',
	'Bump Scale': 'Масштаб выпуклости',
	'Diameter': 'Диаметр',
	'Size Offset': 'Отступ размера',
	'Girdle': 'Рундист',
	'Hole': 'Отверстие',
	'Top/Culet': 'Верх/Калетта',
	'Handle': 'Рукоять',
	'Curve Seat': 'Изгиб посадочного места',
	'Curve Profile': 'Изгиб контура',
	'Bevel Corners': 'Фаска углов',
	'Length Offset': 'Отступ длины',
	'Width Offset': 'Отступ ширины',
	'Position Offset': 'Отступ позиции',
	'Start Up': 'Начало сверху',
	'Adjust Rotation': 'Регулировать вращение',
	'Mirror Axis': 'Оси отражения',

	# Tooltips
	'Create set gemstone': 'Создать заданный камень',
	'List of alloys for weighting': 'Перечень сплавов для оценки веса',
	'Common alloys, physical properties taken directly from suppliers': 'Распространённые сплавы, физические свойства взяты напрямую у поставщиков',
	'Russian regulations for precious alloys': 'Российские стандарты драгоценных сплавов',
	'Display product report in new window': 'Отобразить отчёт изделия в новом окне',
	'Save product report to file in project folder': 'Сохранить отчёт изделия в файл в каталоге проекта',
	'Product report language': 'Язык отчёта изделия',
	'Use user preferences language setting': 'Использовать язык заданный в настройках пользователя',
	'Object for ring inner diameter reference': 'Объект для определения внутреннего диаметра кольца',
	'Object for shank width and height reference': 'Объект для определения ширины и толщины шинки',
	'Object for dimensions reference': 'Объект для определения габаритов изделия',
	'Object for weight reference': 'Объект для определения веса изделия',
	'Save product report to text file': 'Сохранить отчёт изделия в текстовый файл',
	'Replace stone for selected gems': 'Заменить тип камня для выделенных камней',
	'Replace cut for selected gems': 'Заменить огранку для выделенных камней',
	'Select gems by trait': 'Выделить камни по характеристике',
	'Select duplicated gems (located in the same spot)\n'
	'WARNING: it does not work with dupli-faces, objects only': 'Выделить дубликаты (находящиеся на одной координате)\n'
	                                                            'ПРЕДУПРЕЖДЕНИЕ: не работает с dupli-faces, только с объектами',
	'Search stone by name': 'Искать камень по имени',
	'Search alloy by name': 'Искать сплав по имени',
	'Search asset by name': 'Искать ассет по имени',
	'Scatter selected object along active curve': 'Распределить выделенный объект по активной кривой',
	'Redistribute scattering for selected objects': 'Перераспределить выделенные объекты',
	'Display weight or volume for active mesh object': 'Показать вес или объём для активного mesh объекта',
	'Create dupli-face for selected objects\n'
	'WARNING: Select Doubles do not work with dupli-faces, objects only': 'Создать dupli-face для выделенных объектов\n'
	                                                                      'ПРЕДУПРЕЖДЕНИЕ: Выделение Дубликатов не работает с dupli-faces, только объекты',
	'Create distance helper for selected gems': 'Показать указанное расстояние от камня',
	'Create size curve': 'Создать размерную кривую',
	'Stretch deformed objects along curve\n'
	'IMPORTANT: Also works in Edit Mode with selected vertices': 'Растянуть деформированный объект по кривой\n'
	                                                             'ВАЖНО: Также работает в режиме редактирования с выделенными вершинами',
	'Display curve length': 'Показать длину кривой',
	'Move deformed object over or under the curve': 'Переместить деформированные объекты под или над кривой',
	'Mirror selected objects': 'Отразить выделенные объекты',
	'Project selected objects onto active object using Lattice': 'Проецировать выделенные объекты на активный объект с помощью Lattice',
	'Deform active object profile with Lattice': 'Деформировать профиль активного объекта с помощью Lattice',
	'Use automatically generated presets, discards user edits or presets': 'Использовать автоматически сгенерированные пресеты, сбрасывает пользовательское редактирование',
	'Create prongs for selected gems': 'Создать корнера для выделенных камней',
	'Create cutter for selected gems': 'Создать выборку для выделенных камней',
	'Make curve start at the top': 'Расположить начало кривой сверху',
	'Define custom material': 'Задать произвольный материал',
	'Name for the custom material': 'Название произвольного материала',
	'Density g/cm³': 'Плотность г/см³',
	'Open asset library folder': 'Открыть каталог библиотеки ассетов',
	'Create category': 'Создать категорию',
	'Rename category': 'Переименовать категорию',
	'Refresh asset UI': 'Обновить интерфейс ассетов',
	'Add selected objects to asset library': 'Добавить выделенные объекты в библиотеку ассетов',
	'Rename asset': 'Переименовать ассет',
	'Remove asset from library': 'Удалить ассет из библиотеки',
	'Replace current asset with selected objects': 'Заменить текущий ассет выделенными объектами',
	'Replace asset preview image': 'Заменить превью ассета',
	'Import selected asset': 'Импортировать выбранный ассет',
	'Asset category': 'Категория ассетов',
	'Category tools': 'Инструменты категорий',
	'Asset tools': 'Инструменты ассетов',
	'Set custom asset library folder, if disabled the default library folder will be used': 'Указать пользовательский каталог библиотеки ассетов, если отключено, то используется стандартный каталог',
	'Custom library folder path': 'Путь к пользовательскому каталогу библиотеки',
	'Display asset name in Tool Shelf': 'Показывать название ассета в панели инструментов',
	'Use active object name when creating new asset': 'Использовать имя активного объекта при создании нового ассета',

	# Reports
	'WARNING': 'ПРЕДУПРЕЖДЕНИЕ',
	'Curve Length': 'Длина кривой',
	'Found {} duplicates': 'Обнаружено {} дубликатов',
	'No duplicates found': 'Дубликаты не обнаружены',
	'Text file successfully created in the project folder': 'Текстовый файл успешно создан в каталоге проекта',
	'Gem size cannot be 0 mm': 'Размер камня не может быть 0 мм',
	'First save your blend file': 'Сначала сохраните ваш blend файл',
	'Discovered possible gem Dupli-face leftovers': 'Обнаружены возможные остатки Dupli-face камней',
	'Discovered hidden gems in the scene (use Show Hidden/Alt H)': 'Обнаружены скрытые камни (используйте Show Hidden/Alt H)',
	'Discovered duplicated gems': 'Обнаружены дублируемые камни',

	# Cuts
	'Round': 'Кр-57',
	'Oval': 'Овал',
	'Cushion': 'Кушон',
	'Pear': 'Груша',
	'Marquise': 'Маркиз',
	'Princess': 'Принцесса',
	'Baguette': 'Багет',
	'Square': 'Квадрат',
	'Asscher': 'Ашер',
	'Radiant': 'Радиант',
	'Flanders': 'Фландерс',
	'Octagon': 'Октагон',
	'Heart': 'Сердце',
	'Trillion': 'Триллион',
	'Trilliant': 'Триллиант',
	'Triangle': 'Треугольник',

	# Stones
	'Alexandrite': 'Александрит',
	'Amethyst': 'Аметист',
	'Aquamarine': 'Аквамарин',
	'Citrine': 'Цитрин',
	'Cubic Zirconia': 'Фианит',
	'Diamond': 'Бриллиант',
	'Emerald': 'Изумруд',
	'Garnet': 'Гранат',
	'Morganite': 'Морганит',
	'Peridot': 'Хризолит',
	'Quartz': 'Кварц',
	'Ruby': 'Рубин',
	'Sapphire': 'Сапфир',
	'Spinel': 'Шпинель',
	'Tanzanite': 'Танзанит',
	'Topaz': 'Топаз',
	'Tourmaline': 'Турмалин',
	'Zircon': 'Циркон',

	# Alloys
	'Yellow Gold 24K': 'Жёлтое золото 24 кар',
	'Yellow Gold 22K': 'Жёлтое золото 22 кар',
	'Yellow Gold 18K': 'Жёлтое золото 18 кар',
	'Yellow Gold 14K': 'Жёлтое золото 14 кар',
	'Yellow Gold 10K': 'Жёлтое золото 10 кар',
	'White Gold 18K Pd': 'Белое золото 18 кар Pd',
	'White Gold 18K Ni': 'Белое золото 18 кар Ni',
	'White Gold 14K Pd': 'Белое золото 14 кар Pd',
	'White Gold 14K Ni': 'Белое золото 14 кар Ni',
	'White Gold 10K': 'Белое золото 10 кар',
	'Rose Gold 18K': 'Красное золото 18 кар',
	'Rose Gold 14K': 'Красное золото 14 кар',
	'Rose Gold 10K': 'Красное золото 10 кар',

	'Yellow Gold 999': 'Жёлтое золото 999',
	'Yellow Gold 958': 'Жёлтое золото 958',
	'Yellow Gold 750': 'Жёлтое золото 750',
	'Yellow Gold 585': 'Жёлтое золото 585',
	'Yellow Gold 375': 'Жёлтое золото 375',
	'White Gold 750 Pd': 'Белое золото 750 Pd',
	'White Gold 750 Ni': 'Белое золото 750 Ni',
	'White Gold 585 Pd': 'Белое золото 585 Pd',
	'White Gold 585 Ni': 'Белое золото 585 Ni',
	'Red Gold 585': 'Красное золото 585',
	'Red Gold 375': 'Красное золото 375',

	'Platinum 950': 'Платина 950',
	'Platinum 900': 'Платина 900',

	'Palladium 950': 'Палладий 950',

	'Silver 925': 'Серебро 925',
	'Silver Sterling': 'Серебро стерлинг',
	'Silver Argentium': 'Серебро argentium',

	'Brass': 'Латунь',

	# Product report
	'Size': 'Размер',
	'Shank': 'Шинка',
	'Dimensions': 'Габариты',
	'Weight': 'Вес',

	'Settings': 'Вставки',
	'Gem': 'Камень',
	'Cut': 'Огранка',
	'Qty': 'Количество',

	'items': 'шт.',
	'mm': 'мм',
	'mm³': 'мм³',
	'g': 'г',
	'ct.': 'кар',
	}


lc_dative = {
	'Size': 'Размеру',
	'Stone': 'Камню',
	'Cut': 'Огранке',
	}


lc_btn = {
	'Stone': 'Камень',
	'Make Gem': 'Создать камень',
	'Doubles': 'Дубликаты',
	'Scatter Along Curve': 'Распределить по кривой',
	'Prongs': 'Крапана',
	'Cutter': 'Выборка',
	'Make Dupli-face': 'Создать Dupli-face',
	'Mirror Objects': 'Отразить объекты',
	'Lattice Project': 'Lattice проекция',
	'Lattice Profile': 'Lattice профиль',
	'Size Curve': 'Размерная кривая',
	'Over': 'Над',
	'Under': 'Под',
	'Stretch': 'Растянуть',
	'Curve Length': 'Длина кривой',
	'Product Report': 'Отчёт изделия',
	'Open Library Folder': 'Открыть каталог библиотеки',
	'Import Asset': 'Импортировать ассет',
	'Rename': 'Переименовать',
	'Replace Asset': 'Заменить ассет',
	'Replace Preview': 'Заменить превью',
	'Create Category': 'Создать категорию',
	'Distance Helper': 'Показать расстояние',
	'Remove Asset': 'Удалить ассет',
	'Replace Asset Preview': 'Заменить превью ассета',
	}


lc_jewel = {
	'Cut': 'Огранка',
	'Dimensions': 'Габариты',
	}


lc_ru = {}

for k, v in lc_main.items():
	lc_ru[('*', k)] = v

for k, v in lc_dative.items():
	lc_ru[('Dative', k)] = v

for k, v in lc_btn.items():
	lc_ru[('Operator', k)] = v

for k, v in lc_jewel.items():
	lc_ru[('JewelCraft', k)] = v


lc_reg = {'ru_RU': lc_ru}

# Do not remove lc_main, needed for getreporttext
del lc_dative
del lc_btn
del lc_jewel


def iface_lang():
	system = bpy.context.user_preferences.system
	lang = system.language if system.use_international_fonts and system.use_translate_interface else 'DEFAULT'

	return lang


def getreporttext(text):
	product_report_lang = bpy.context.user_preferences.addons[__package__].preferences.product_report_lang

	if product_report_lang == 'AUTO':
		lang = bpy.app.translations.locale
	else:
		lang = product_report_lang

	if lang == 'ru_RU':
		text = lc_main.get(text, text)

	return text
