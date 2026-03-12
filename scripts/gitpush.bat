@echo off
REM Git 推送快捷命令
REM 用法: gitpush "注释内容"

if "%1"=="" (
    echo 用法: gitpush "注释内容"
    exit /b 1
)

git add .
git commit -m "%1"
git push
