JewelCraft—jewelry design toolkit add-on for Blender.

Features:

* Create and customize gems, prongs and cutters.
* Organize library of components using in add-on asset manager.
* Manage distances between gems to create compact setting.
* Calculate weight in a variety of precious alloys.
* Generate color-coded gem map.
* Present summary information about your design.
* Translated to multiple languages:
  * English ![100%](https://progress-bar.dev/100)
  * Russian ![100%](https://progress-bar.dev/100)
  * Arabic ![95%](https://progress-bar.dev/95)
  * Italian ![80%](https://progress-bar.dev/80)
  * French ![72%](https://progress-bar.dev/72)
  * Spanish ![65%](https://progress-bar.dev/65)
  * Simplified Chinese ![57%](https://progress-bar.dev/57)
  * Your language is missing or incomplete? [Contribute translation](#translations).

Video:

* [Prongs & Cutters v2.0](https://youtu.be/AZlCFg8bDSg)
* [Widgets v2.3](https://youtu.be/9VN_-seau3k)
* [Gem Map v2.3](https://youtu.be/aQ__ec0BAbE)
* [Asset Manager v2.6](https://youtu.be/SYMHsImXe_c)
* [Distribute on Curve v2.8](https://youtu.be/h4-emum2orE)
* [Design Report v2.8](https://youtu.be/6UxJAw_t5R0)
* [Recover Gem v2.8](https://youtu.be/dn1XBbslgEw)

[More videos][playlist_en] | [Больше видео][playlist_ru]


How to install
==========================

1. Download [JewelCraft 2.12][download_latest].<sup>1</sup>
2. Make sure you have Blender 3 or newer.
3. Open `Preferences` → `Add-ons` category.
4. Use `Install` to install add-on from downloaded zip archive.<sup>2</sup>
5. Check [known issues](#known-issues).

<sup>1</sup> Note for mac users: Safari browser will automatically unpack downloaded zip archive, so in order to install the add-on, you have to pack folder with add-on files back into zip archive. Or use a different browser to download add-on.

<sup>2</sup> If error occurs on add-on activation, it means you are trying to install add-on repository instead of release. Make sure you download add-on release using link provided in step one of this guide.


Установка
==========================

1. Загрузите [JewelCraft 2.12][download_latest].<sup>1</sup>
2. Убедитесь, что у вас установлен Blender 3 или новее.
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
* [Open new bug report][report_bug], be sure to include Blender and add-on versions, and screenshot showing the error message.

### Known issues

* Design Report/Gem Map/Spacing Overlay
  * [[T74368](https://developer.blender.org/T74368)] Gems from hidden collections appear in report/Spacing Overlay, this happens when collection is hidden with  `Hide in Viewport` (eye icon), instead use `Disable in Viewports` (display icon) or `Exclude from View Layer` (checkbox).

### Translations

* It is advised that you use a dedicated `.po` editor like [Poedit](https://poedit.net).
* To create new transltation in Poedit use `File` → `New from POT/PO file`, then pick `.po` file from add-on `localization` folder (doesn't matter which one).
* Translating tips:
  * The UI convention for English language is to use Title Case formatting for property names and button titles, to know formatting convention for your language just see how Blender handles it and follow the rule.
  * Preserve empty braces `{}` in translation, they used as placeholders for additional information and will not appear in UI.
  * Look out for appropriate context, `Base` for example is used in the context of materials as `Base Metal`, which in other words means `Non-Presious Metal` and should not be translated as `Basis` or `Foundation`.
  * If you have limited amount of time to work on translation, then make sure to prioritize in the following order:
    * Essentials: add-on sidebar UI, gem names and cuts.
    * Good to have: tool popups and modal UI, add-on preferences, precious alloys, error messages.
    * The rest: tooltips and other UI messages.
* After translation is done submit it back through [issues][submit_translation].


[download_latest]: https://github.com/mrachinskiy/jewelcraft/releases/download/v2.12.0-blender3.0.0/jewelcraft-2_12_0.zip
[report_bug]: https://github.com/mrachinskiy/jewelcraft/issues/new?template=bug_report.md
[submit_translation]: https://github.com/mrachinskiy/jewelcraft/issues/new?labels=translation&template=contribute-translation.md
[playlist_en]: https://www.youtube.com/playlist?list=PLCoK1Ao0T01KhfestF7xCic1jf5YjXiVh
[playlist_ru]: https://www.youtube.com/playlist?list=PLCoK1Ao0T01KQ0cobvQLR2q3sYF6fH2lh
