pyinstaller --onefile -w --icon=assets\icon.ico^
  --add-data="assets;assets" ^
  --add-data="assets\colormaps;assets\colormaps" ^
  --add-data="assets\images;assets\images" ^
  --add-data="assets\shadows;assets\shadows" ^
   main.py
del main.exe
move dist\main.exe
del /Q /s build
rmdir /Q /s build
del /Q /s dist
rmdir /Q /s dist
del main.spec
del Editor.exe
ren main.exe Editor.exe
timeout -1