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
  * ![96%](https://geps.dev/progress/96) Traditional Chinese
  * ![95%](https://geps.dev/progress/95) Spanish
  * ![88%](https://geps.dev/progress/88) Simplified Chinese
  * ![81%](https://geps.dev/progress/81) French
  * ![80%](https://geps.dev/progress/80) Arabic
  * ![70%](https://geps.dev/progress/70) Italian
  * Your language is missing or incomplete? [Contribute translation](#translations).


How to install
==========================

### [Drag and Drop this link into Blender][download_latest]

<sub>Or download and drag zip file into Blender</sub>

<details>
  <summary>For Blender 4.1 or older</summary>

  1. Download [JewelCraft 2.17.4][download_v2_17_4]
  2. Make sure you have Blender 3.5 or newer.
  3. Open `Preferences` → `Add-ons` category.
  4. Use `Install` to install add-on from downloaded zip archive.
</details>

> [!NOTE]
> For mac users: Safari browser will automatically unpack downloaded zip archive, to prevent that go `Safari` → `Preferences` → `General` and uncheck `Open "safe" files after downloading` option.

> [!WARNING]
> If error occurs on add-on activation, it means you are trying to install add-on repository instead of release. Make sure you download add-on release using link provided in step one of this guide.


Установка
==========================

### [Перетащите эту ссылку в Blender][download_latest]

<sub>Или скачайте и перетащите zip-файл в Blender</sub>

<details>
  <summary>Для Blender 4.1 или старше</summary>

  1. Загрузите [JewelCraft 2.17.4][download_v2_17_4]
  2. Убедитесь, что у вас установлен Blender 3.5 или новее.
  3. Откройте `Preferences` → `Add-ons`
  4. Воспользуйтесь `Install` чтобы установить аддон из загруженного архива.
</details>

> [!NOTE]
> Примечание для пользователей mac: браузер Safari автоматически распаковывает скачиваемые zip архивы, чтобы это предотвратить в настройках `Safari` → `Preferences` → `General` отключите опцию `Open "safe" files after downloading`.

> [!WARNING]
> Если при активации аддона возникает ошибка, значит вы пытаетесь установить репозиторий вместо релиза. Для загрузки релиза используйте ссылку, приведённую в первом шаге данного руководства.


Contributing
==========================

### Did you find a bug?

* Ensure the bug can be reproduced in the latest add-on version.
* [Open new bug report][issues_url], be sure to include Blender and add-on versions, and screenshot showing the error message.

### Translations

* It is advised that you use a dedicated `.po` editor like [Poedit](https://poedit.net).
  * To create new transltation in Poedit use `File` → `New from POT/PO file`, then pick `.po` file from add-on `localization` folder (doesn't matter which one).
  * To complete existing transltation in Poedit use `File` → `Open`, then pick `.po` file for specific language from add-on `localization` folder.
* After translation is done submit it back through [issues][issues_url].

> [!TIP]
> * The UI convention for English language is to use Title Case formatting for property names and button titles, to know formatting convention for your language just see how Blender handles it and follow the rule.
> * Preserve empty braces `{}` in translation, they used as placeholders for additional information and will not appear in UI.
> * Look out for appropriate context, `Base` for example is used in the context of materials as `Base Metal`, which in other words means `Non-Presious Metal` and should not be translated as `Basis` or `Foundation`.


[download_latest]: https://github.com/mrachinskiy/jewelcraft/releases/download/v2.18.0-blender4.2.0/jewelcraft-2_18_0.zip?repository=https://mrachinskiy.github.io/api/v1/extensions.json&blender_version_min=4.2.0
[download_v2_17_4]: https://github.com/mrachinskiy/jewelcraft/releases/download/v2.17.4-blender3.5.0/jewelcraft-2_17_4.zip
[issues_url]: https://github.com/mrachinskiy/jewelcraft/issues
