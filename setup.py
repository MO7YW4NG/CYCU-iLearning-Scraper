from cx_Freeze import setup, Executable
import sys

base = None

target = Executable(
    script="app.py",
    icon="icon.ico",
    base=base
)

setup(
    name="CYCU-iLearning-Scraper",
    version="1.1",
    description="cycu-ilearning-scarper",
    author="MO7YW4NG",
    options={'bdist_msi': {'initial_target_dir': r'[DesktopFolder]\\CYCU-Auto-Survey'},'bdist_mac': {'initial_target_dir': r'[DesktopFolder]\\CYCU-Auto-Survey'}},
    executables=[target],
)

options={
    'build_exe': {
        'packages': ['aiohttp','json','getpass','os','hashlib','base64','urllib','time','asyncio','Crypto','bs4'],
        'include_files': ['icon.ico']
    }
}