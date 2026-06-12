@echo off
cd /d C:\Users\yu\Desktop\earbuds-review
git add -A >nul 2>&1
git diff --cached --quiet
if %errorlevel% equ 0 exit /b
git commit -m "auto: update content [%date% %time%]"
git push
