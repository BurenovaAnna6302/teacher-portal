@echo off
echo Копирование файлов для согласования с путями из базы данных...

rem ---- НОВОСТИ ----
if exist "news\static\news\images\news_photos" (
    mkdir "news\static\news\photos" 2>nul
    copy "news\static\news\images\news_photos\*" "news\static\news\photos\" >nul
    echo [OK] news
) else (
    echo [WARN] Папка news\static\news\images\news_photos не найдена
)

rem ---- СОБЫТИЯ ----
if exist "events\static\events\images\event_photos" (
    mkdir "events\static\events\photos" 2>nul
    copy "events\static\events\images\event_photos\*" "events\static\events\photos\" >nul
    echo [OK] events
) else (
    echo [WARN] Папка events\static\events\images\event_photos не найдена
)

rem ---- МАТЕРИАЛЫ (PDF) ----
if exist "materials\static\materials\files" (
    mkdir "materials\static\materials" 2>nul
    copy "materials\static\materials\files\*" "materials\static\materials\" >nul
    echo [OK] materials
) else (
    echo [WARN] Папка materials\static\materials\files не найдена
)

rem ---- ДОКУМЕНТЫ (PDF) ----
if exist "documents\static\documents\files" (
    mkdir "documents\static\documents" 2>nul
    copy "documents\static\documents\files\*" "documents\static\documents\" >nul
    echo [OK] documents
) else (
    echo [WARN] Папка documents\static\documents\files не найдена
)

rem ---- УСПЕШНЫЕ ПРАКТИКИ ----
rem В дампе путь "practices/files/...", поэтому создаём success_practices\static\practices\files
if exist "success_practices\static\success_practices\files" (
    mkdir "success_practices\static\practices\files" 2>nul
    copy "success_practices\static\success_practices\files\*" "success_practices\static\practices\files\" >nul
    echo [OK] success_practices (files)
) else (
    echo [WARN] Папка success_practices\static\success_practices\files не найдена
)
rem Также если есть файлы в success_practices/static/success_practices/ (без подпапки files) – скопируем их в practices/files
if exist "success_practices\static\success_practices\*.*" (
    mkdir "success_practices\static\practices\files" 2>nul
    copy "success_practices\static\success_practices\*.*" "success_practices\static\practices\files\" >nul
    echo [OK] success_practices (root files)
)

rem ---- ФОТО УЧИТЕЛЕЙ ----
rem По вашей структуре учителя используют static/auth/images
if exist "teachers\static\auth\images" (
    mkdir "teachers\static\teachers" 2>nul
    copy "teachers\static\auth\images\*" "teachers\static\teachers\" >nul
    echo [OK] teachers (from auth/images)
) else if exist "teachers\static\teachers\images" (
    mkdir "teachers\static\teachers" 2>nul
    copy "teachers\static\teachers\images\*" "teachers\static\teachers\" >nul
    echo [OK] teachers (from teachers/images)
) else (
    echo [WARN] Фото учителей не найдены (искал в teachers/static/auth/images и teachers/static/teachers/images)
)

echo.
echo ===== КОПИРОВАНИЕ ЗАВЕРШЕНО =====
echo Запустите команды:
echo   git add .
echo   git commit -m "Скопированы файлы в ожидаемые папки статики"
echo   git push origin main
echo.
pause