@echo off
echo Добавляем переименованные фото в Git...
git add news/static/news/photos/
git add events/static/events/photos/
git commit -m "Фото с длинными именами для совместимости с БД"
git push origin main
echo Готово! Теперь перезапустите деплой на Timeweb.
pause
