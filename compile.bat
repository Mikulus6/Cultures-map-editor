pyinstaller --onefile -w --icon=assets\icon.ico^
  --add-data="assets;assets" ^
  --add-data="assets\colormaps;assets\colormaps" ^
  --add-data="assets\images;assets\images" ^
  --add-data="assets\shadows;assets\shadows" ^
   main.py
pyinstaller --onefile -w --icon=assets\icon_converters.ico --add-data="assets;assets" converters.py
del main.exe
del converters.exe
move dist\main.exe
move dist\converters.exe
del /Q /s build
rmdir /Q /s build
del /Q /s dist
rmdir /Q /s dist
del main.spec
del converters.spec
del Editor.exe
ren main.exe Editor.exe
ren converters.exe Converters.exe
timeout -1