git add *
@echo off
:: 获取当前日期和时间
for /f "tokens=2 delims==" %%i in ('wmic os get localdatetime /value') do set datetime=%%i

:: 提取并格式化日期和时间
set year=%datetime:~0,4%
set month=%datetime:~4,2%
set day=%datetime:~6,2%
set hour=%datetime:~8,2%
set minute=%datetime:~10,2%
set second=%datetime:~12,2%

:: 拼接为 yyyy-MM-dd HH:mm:ss 格式
set formatted_time=%year%-%month%-%day% %hour%:%minute%:%second%

git commit -m "%formatted_time%"
git push origin
git push github