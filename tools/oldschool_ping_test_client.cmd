@echo off
:LoopStart
set /p world="Enter the world number: "
ping oldschool%world%.runescape.com
set /p goagain="Try another? Y/N: "
if /I "%goagain%" == "Y" (GoTo LoopStart) else (timeout /t -1)