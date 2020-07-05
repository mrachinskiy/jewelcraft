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
* [Asset Manager v2.6](https://youtu.be/SYMHsImXe_c)

[More videos][playlist_en] | [Больше видео][playlist_ru]


How to install
==========================

1. Download [JewelCraft 2.7.3][v_latest].<sup>1</sup>
2. Make sure you have Blender 2.80 or newer.
3. Open `Preferences` → `Add-ons` category.
4. Use `Install` to install add-on from downloaded zip archive.<sup>2</sup>
5. Check [known issues](#known-issues).

<sup>1</sup> Note for mac users: Safari browser will automatically unpack downloaded zip archive, so in order to install the add-on, you have to pack folder with add-on files back into zip archive. Or use a different browser to download add-on.

<sup>2</sup> If error occurs on add-on activation, it means you are trying to install add-on repository instead of release. Make sure you download add-on release using link provided in step one of this guide.


Установка
==========================

1. Загрузите [JewelCraft 2.7.3][v_latest].<sup>1</sup>
2. Убедитесь, что у вас установлен Blender 2.80 или новее.
3. Откройте `Preferences` → `Add-ons`.
4. Воспользуйтесь `Install` чтобы установить аддон из загруженного архива.<sup>2</sup>
5. Ознакомьтесь с [известными проблемами](#known-issues).

<sup>1</sup> Примечание для пользователей mac: браузер Safari автоматически распаковывает скачиваемые zip архивы, поэтому, чтобы установить аддон, необходимо запаковать папку с файлами аддона обратно в zip архив. Или используйте другой браузер для скачивания аддона.

<sup>2</sup> Если при активации аддона возникает ошибка, значит вы пытаетесь установить репозиторий вместо релиза. Для загрузки релиза используйте ссылку, приведённую в первом шаге данного руководства.


Contributing
==========================

### Did you find a bug?

* Check [known issues](#known-issues).
* Ensure the bug can be reproduced in the latest add-on version.
* [Open new bug report][new_bug_report], be sure to include Blender and add-on versions, and screenshot showing the error message.

### Known issues

* Product Report/Gem Map
  * [[T74368](https://developer.blender.org/T74368)] Gems from hidden collections appear in report, this happens when collection is hidden with  `Hide in Viewport` (eye icon), instead use `Disable in Viewports` (display icon) or `Exclude from View Layer` (checkbox left from collection).
* Assets
  * [[T69001](https://developer.blender.org/T69001)] Asset previews do not load if render engine set to `Workbench`.

### Translations

* Take `.jsonc` translation dictionary from `localization` folder, and use it as an example template for your translation.
* Example:
  ```jsonc
  "Save To File": "Сохранить в файл",
  "{} duplicates found": "{} дубликатов обнаружено",
  "[JewelCraft] Precious": "[JewelCraft] Драгоценные",
  // "Add To Library": "",
  ```
  * On the left is the original English message, with translation on the right, in this case in Russian language.
  * Notice how original message is using Title Case formatting when translation is not, that is the difference between English and Russian UI conventions, to know formatting convention for your language just see how Blender handles it and follow the rule.
  * Not every word has to be translated, for example `JewelCraft` is not translated because it referencing add-on name.
  * Commented out `//` empty entries have not been translated yet, remove double slash after filling in the translation.
* After translation is done submit it back through [issues][new_translation].


[v_latest]: https://github.com/mrachinskiy/jewelcraft/releases/download/2.7.3/jewelcraft-2_7_3.zip
[playlist_en]: https://www.youtube.com/playlist?list=PLCoK1Ao0T01KhfestF7xCic1jf5YjXiVh
[playlist_ru]: https://www.youtube.com/playlist?list=PLCoK1Ao0T01KQ0cobvQLR2q3sYF6fH2lh
[new_bug_report]: https://github.com/mrachinskiy/jewelcraft/issues/new?template=bug_report.md
[new_translation]: https://github.com/mrachinskiy/jewelcraft/issues/new?labels=translation&template=contribute-translation.md
