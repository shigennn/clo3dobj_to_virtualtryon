@echo off
cd /D %~dp0

echo Please enter the parent directory of "Clothes" and "Coord".
SET /P PARENT_DIR=

cd scripts
..\resources\blender-3.3.2-windows-x64\blender --background --python clo3dobj_to_vtryon.py %PARENT_DIR%

pause
exit