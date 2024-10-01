from cx_Freeze import setup, Executable

base = None

target = Executable(
    script="app.py",
    icon="icon.png",
    base=base
)

setup(
    name="CYCU-iLearning-Scraper",
    version="1.3",
    description="cycu-ilearning-scarper",
    author="MO7YW4NG, Joe Liao",
    options={'build_exe': {
        'packages': ['aiohttp','json','getpass','os','hashlib','base64','re','aiodns','time','asyncio','Crypto','bs4','rich'],
        'include_files': ['icon.ico','icon.png']
    }, 'bdist_msi': {'initial_target_dir': r'[DesktopFolder]\\CYCU-iLearning-Scraper'}},
    executables=[target],
)