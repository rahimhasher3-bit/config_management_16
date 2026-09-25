@echo off
cd /d "%~dp0.."
python src\emulator.py --vfs test_vfs.zip --script scripts\startup_test.txt