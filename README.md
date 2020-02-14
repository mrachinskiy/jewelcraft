JewelCraft—jewelry design toolkit add-on for Blender.

Features:

* Create and customize gems, prongs and cutters.
* Organize library of components using in add-on asset manager.
* Manage distances between gems to create compact setting.
* Calculate weight in a variety of precious alloys.
* Generate color-coded gem map.
* Present summary information about your design.
* Support multiple languages:
  * English
  * Spanish
  * French
  * Italian
  * Russian
  * Simplified Chinese
  * Your language is missing? [Contribute translation](#translations).

Video:

* [Demo v1.0](https://youtu.be/XZ6uIdNnrHk)
* [Prongs & Cutters v2.0](https://youtu.be/AZlCFg8bDSg)
* [Widgets v2.3](https://youtu.be/9VN_-seau3k)
* [Gem Map v2.3](https://youtu.be/aQ__ec0BAbE)

[More videos][playlist_en] | [Больше видео][playlist_ru]


How to install
==========================

1. Download the add-on:<sup>1</sup>
    * [**Blender 2.80** JewelCraft v2.5.0][v_latest]
    * [**Blender 2.79** JewelCraft v2.2.1][v_legacy]
2. Open `Preferences` → `Add-ons` category.
3. Use `Install` to install add-on from downloaded zip archive.
4. Check [known issues](#known-issues).

<sup>1</sup> Note for mac users: Safari browser will automatically unpack downloaded zip archive, so in order to install the add-on, you have to pack folder with add-on files back into zip archive. Or use a different browser to download add-on.


Установка
==========================

1. Загрузите аддон:<sup>1</sup>
    * [**Blender 2.80** JewelCraft v2.5.0][v_latest]
    * [**Blender 2.79** JewelCraft v2.2.1][v_legacy]
2. Откройте `Preferences` → `Add-ons`.
3. Воспользуйтесь `Install` чтобы установить аддон из загруженного архива.
4. Ознакомьтесь с [известными проблемами](#known-issues).

<sup>1</sup> Примечание для пользователей mac: браузер Safari автоматически распаковывает скачиваемые zip архивы, поэтому, чтобы установить аддон, необходимо запаковать папку с файлами аддона обратно в zip архив. Или используйте другой браузер для скачивания аддона.


Contributing
==========================

### Did you find a bug?

* Check [known issues](#known-issues).
* Ensure the bug can be reproduced in the latest add-on version.
* [Open new bug report][new_bug_report], be sure to include Blender and add-on versions, and screenshot showing the error message.

### Known issues

* If error occurs on add-on installation or activation you probably trying to install add-on repository instead of release, check [how to install](#how-to-install) guide for proper installation process.
* Product Report gem table is misaligned when using Chinese as report language, use Gem Map as a workaround.
* If Chinese characters are not displaying, enable `Preferences` → `Interface` → `Translation` property.

### Translations

* Get `localization/ru.py` translation dictionary from repository and use it as an example template for your translation.
* Example:
  ```
  "Save to file": "Сохранить в файл",
  "{} duplicates found": "{} дубликатов обнаружено",
  "[JewelCraft] Precious": "[JewelCraft] Драгоценные",
  ```
  * On the left is the original English message, on the right is the Russian translation of that message.
  * Not every word has to be translated, in this example `JewelCraft` is not translated because it referencing add-on name.
* After translation is done submit it back through [issues][new_translation].


[v_latest]: https://github.com/mrachinskiy/jewelcraft/releases/download/v2.5.0/jewelcraft-2_5_0.zip
[v_legacy]: https://github.com/mrachinskiy/jewelcraft/releases/download/v2.2.1/jewelcraft-2_2_1.zip
[playlist_en]: https://www.youtube.com/playlist?list=PLCoK1Ao0T01KhfestF7xCic1jf5YjXiVh
[playlist_ru]: https://www.youtube.com/playlist?list=PLCoK1Ao0T01KQ0cobvQLR2q3sYF6fH2lh
[new_bug_report]: https://github.com/mrachinskiy/jewelcraft/issues/new?template=bug_report.md
[new_translation]: https://github.com/mrachinskiy/jewelcraft/issues/new?labels=translation&template=contribute-translation.md
