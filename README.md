JewelCraft—jewelry design toolkit add-on for Blender.

Features:

* Create and customize gems, prongs and cutters. [[▸]](https://youtu.be/h4-emum2orE)
* Organize library of components using in add-on asset manager. [[▸]](https://youtu.be/SYMHsImXe_c)
* Manage distances between gems to create compact setting. [[▸]](https://youtu.be/9VN_-seau3k)
* Calculate weight in a variety of precious alloys.
* Generate color-coded gem map. [[▸]](https://youtu.be/aQ__ec0BAbE)
* Present summary information about your design. [[▸]](https://youtu.be/6UxJAw_t5R0)
* Translated to multiple languages:
  * ![100%](https://geps.dev/progress/100) English
  * ![100%](https://geps.dev/progress/100) Russian
  * ![100%](https://geps.dev/progress/100) Traditional Chinese
  * ![93%](https://geps.dev/progress/93) Simplified Chinese
  * ![89%](https://geps.dev/progress/88) Spanish
  * ![85%](https://geps.dev/progress/85) Arabic
  * ![74%](https://geps.dev/progress/74) Italian
  * ![66%](https://geps.dev/progress/66) French
  * Your language is missing or incomplete? [Contribute translation](#translations).


How to install
==========================

### For Blender 4.2 or newer

### [Drag and Drop this link into Blender][download_latest]

<sub>Or download and drag zip file into Blender<sup>1</sup></sub>

---

### For Blender 4.1 or older

1. Download [JewelCraft 2.17.2][download_latest]<sup>1</sup>
2. Make sure you have Blender 3.5 or newer.
3. Open `Preferences` → `Add-ons` category.
4. Use `Install` to install add-on from downloaded zip archive.<sup>2</sup>

<sup>1</sup> Note for mac users: Safari browser will automatically unpack downloaded zip archive, to prevent that go `Safari` → `Preferences` → `General` and uncheck `Open "safe" files after downloading` option.

<sup>2</sup> If error occurs on add-on activation, it means you are trying to install add-on repository instead of release. Make sure you download add-on release using link provided in step one of this guide.


Установка
==========================

### Для Blender 4.2 или новее

### [Перетащите эту ссылку в Blender][download_latest]

<sub>Или скачайте и перетащите zip-файл в Blender<sup>1</sup></sub>

---

### Для Blender 4.1 или старше

1. Загрузите [JewelCraft 2.17.2][download_latest]<sup>1</sup>
2. Убедитесь, что у вас установлен Blender 3.5 или новее.
3. Откройте `Preferences` → `Add-ons`
4. Воспользуйтесь `Install` чтобы установить аддон из загруженного архива.<sup>2</sup>

<sup>1</sup> Примечание для пользователей mac: браузер Safari автоматически распаковывает скачиваемые zip архивы, чтобы это предотвратить в настройках `Safari` → `Preferences` → `General` отключите опцию `Open "safe" files after downloading`.

<sup>2</sup> Если при активации аддона возникает ошибка, значит вы пытаетесь установить репозиторий вместо релиза. Для загрузки релиза используйте ссылку, приведённую в первом шаге данного руководства.


Contributing
==========================

### Did you find a bug?

* Ensure the bug can be reproduced in the latest add-on version.
* [Open new bug report][report_bug], be sure to include Blender and add-on versions, and screenshot showing the error message.

### Translations

* It is advised that you use a dedicated `.po` editor like [Poedit](https://poedit.net).
  * To create new transltation in Poedit use `File` → `New from POT/PO file`, then pick `.po` file from add-on `localization` folder (doesn't matter which one).
  * To complete existing transltation in Poedit use `File` → `Open`, then pick `.po` file for specific language from add-on `localization` folder.
* Translating tips:
  * The UI convention for English language is to use Title Case formatting for property names and button titles, to know formatting convention for your language just see how Blender handles it and follow the rule.
  * Preserve empty braces `{}` in translation, they used as placeholders for additional information and will not appear in UI.
  * Look out for appropriate context, `Base` for example is used in the context of materials as `Base Metal`, which in other words means `Non-Presious Metal` and should not be translated as `Basis` or `Foundation`.
  * If you have limited amount of time to work on translation, then make sure to prioritize in the following order:
    * Essentials: add-on sidebar UI, gem names and cuts.
    * Good to have: tool popups and modal UI, add-on preferences, precious alloys, error messages.
    * The rest: tooltips and other UI messages.
* After translation is done submit it back through [issues][submit_translation].


[download_latest]: https://github.com/mrachinskiy/jewelcraft/releases/latest/download/jewelcraft-2_17_2.zip?repository=https://mrachinskiy.github.io/api/v1/extensions.json&blender_version_min=4.2.0
[report_bug]: https://github.com/mrachinskiy/jewelcraft/issues/new?template=bug_report.md
[submit_translation]: https://github.com/mrachinskiy/jewelcraft/issues/new?labels=translation&template=contribute-translation.md
