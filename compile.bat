pyinstaller --onefile -w --icon=assets\icon.ico main.py
del main.exe
move dist\main.exe
del /Q /s build
rmdir /Q /s build
del /Q /s dist
rmdir /Q /s dist
del main.spec
ren main.exe Editor.exe
timeout -1