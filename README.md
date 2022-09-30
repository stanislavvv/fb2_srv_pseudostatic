# fb2_srv pseudostatic

NIH-проект

Сиё есть сервер opds для кучи fb2 в нескольких zip. Предназначено для запуска на одноплатниках.

Поскольку предыдущий проект на Orange PI 3 LTS оказался очень медленным (неудивительно, вобщем-то),
решил, что вместо БД проще сделать статическую структуру, которую и отдавать.

ВНИМАНИЕ: структура `.zip.lists` не совместима с fb2_srv!

## структура каталогов псевдостатики

"псевдо" — потому что один и тот же файл будет использован как для opds, так и для html

- `/index.json` - главная страница
- `/(authorindex|sequenceindex|genres)/index.json` - страницы соответствующих разделов
- `/(authorindex|sequenceindex)/(.|...)/index.json`, `/genres/.+/index.json` и `/genres/.+/[0-9]+.json` - страницы соответствующих подразделов
- `/sequence/<SeqCut>/<SeqCut2>/<SequenceID>/index.json` - страница книжной серии

Страницы автора:
- `/author/<AuthorCut>/<AuthorCut2>/<AuthorID>/index.json` - все книги автора
- `/author/<AuthorCut>/<AuthorCut2>/<AuthorID>/sequences.json` - серии
- `/author/<AuthorCut>/<AuthorCut2>/<AuthorID>/sequenceless.json` - вне серий
- `/author/<AuthorCut>/<AuthorCut2>/<AuthorID>/<SequenceID>.json` - книги автора в серии

AuthorCut и SeqCut - первые 2 символа от соответствующих ID,
AuthorCut2 и SeqCut2 - вторые 2 символа. Используется для уменьшения числа файлов в каталоге.
