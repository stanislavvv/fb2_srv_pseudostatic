# fb2_srv pseudostatic

NIH-проект

Сиё есть сервер opds для кучи fb2 в нескольких zip. Предназначено для запуска на одноплатниках.

Поскольку предыдущий проект (fb2_srv) на Orange PI 3 LTS оказался очень медленным (неудивительно, вобщем-то), решил, что вместо БД проще сделать статическую структуру, которую и отдавать.

ВНИМАНИЕ: структура `.zip.lists` не совместима с fb2_srv!

## структура каталогов псевдостатики

"псевдо" — потому что один и тот же файл будет использован как для opds, так и для html и перед отправкой преобразуется в нужный формат.

- `/index.json` — главная страница
- `/(authorindex|sequenceindex|genres)/index.json` — страницы соответствующих разделов
- `/(authorindex|sequenceindex)/(.|...)/index.json`, `/genres/.+/index.json` и `/genres/.+/[0-9]+.json` — страницы соответствующих подразделов
- `/sequence/<SeqCut>/<SeqCut2>/<SequenceID>.json` — данные серии в `{"data": ...}`
- `/author/<AuthorCut>/<AuthorCut2>/<AuthorID>.json` — данные автора в `{"data": ...}`

AuthorCut и SeqCut — первые 2 символа от соответствующих ID,
AuthorCut2 и SeqCut2 — вторые 2 символа. Используется для уменьшения числа файлов в каталоге.

## процедура подготовки данных

Общая процедура:

```
datachew.py new_lists  # или lists, если требуется обновить все файлы .list
datachew.py stage1
datachew.py stage2
datachew.py stage3
datachew.py stage4
```

Параметры `datachew.py`:

- `lists` — пройтись по всем `.zip` и создать соответствующие `.zip.list`
- `new_lists` — пройтись по `.zip` и создать только те `.zip.list`, которые либо отсутствуют, либо старше `.zip`
- `stage1` — глобальные индексы в корне (книги, авторы, серии, жанры)
- `stage2` — индивидуальные индексы по авторам + дополнительная структура для вывода по буквам
- `stage3` — индивидуальные индексы по сериям + …
- `stage4` — индивидуальные индексы по жанрам + …

Процесс создания индексов разбит на стадии `stage1` — `stage4` вместо единой команды для уменьшения пикового потребления памяти на микрокомпьютере (вместо почти 2ГБ - не более 0.5ГБ)
