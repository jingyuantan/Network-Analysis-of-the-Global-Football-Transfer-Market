#!E:\Users\User\PycharmProjects\Network-Analysis-of-the-Global-Football-Transfer-Market\FT_Analysis\venv\Scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'setuptools==40.8.0','console_scripts','easy_install-3.6'
__requires__ = 'setuptools==40.8.0'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('setuptools==40.8.0', 'console_scripts', 'easy_install-3.6')()
    )
