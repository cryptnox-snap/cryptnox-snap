#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import sys

from PyInstaller import __main__

from cryptnoxcard.main import __version__

CURRENT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")

if os.path.isdir(CURRENT_DIR):
    print("Contents of dist folder will be deleted.")
    choice = input("Enter y to proceed:")
    if choice == "y":
        shutil.rmtree(CURRENT_DIR)
    else:
        sys.exit()
OS_VERSION = "all"
REVISION = "1"
ISSUER = "cryptnox"
APP_NAME = "cryptnoxcard"

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
SPEC_LOCATION = os.path.join(FILE_DIR, "cryptnoxcard_deb.spec")
ICON_LOCATION = os.path.join(FILE_DIR, "cryptnoxcard.ico")
CONTROL_CONTENT = f"Package: {APP_NAME.lower()}\n" \
               f"Version: {__version__}\n" \
               f"Architecture: all\n" \
               f"Maintainer: Internal Pointers <info@internalpointers.com>\n" \
               f"Description: Program for using Cryptnox cards\n"
DESKTOP_CONTENT = f"[Desktop Entry]\n" \
                  f"Version={__version__}\n" \
                  f"Name={APP_NAME.lower()}\n" \
                  f"GenericName={APP_NAME.upper()}\n" \
                  f"Comment={APP_NAME.capitalize()} client application\n" \
                  f"Exec=/usr/bin/{APP_NAME.lower()}\n" \
                  f"TryExec=/usr/bin/{APP_NAME.lower()}\n" \
                  f"Icon=/usr/share/icons/{os.path.basename(ICON_LOCATION)}\n" \
                  f"Terminal=true\n" \
                  f"Type=Application\n" \
                  f"Categories=Utility;\n" \
                  f"Keywords=Backup;\n"
BASH_SCRIPT = f"#!/usr/bin/env bash\n" \
              f"cd /usr/bin/{ISSUER.lower()}\n" \
              f"./{APP_NAME.lower()}\n"


os.makedirs(CURRENT_DIR, exist_ok=True)
os.chdir(CURRENT_DIR)
deb_name = f"{APP_NAME.lower()}_{__version__}-{REVISION}_{OS_VERSION}"
deb_dir = f"{CURRENT_DIR}/{deb_name}"
usr_bin_dir = f"{CURRENT_DIR}/{deb_name}/usr/bin"
debian_dir = f"{deb_dir}/DEBIAN"
share_dir = f"{deb_dir}/usr/share"
app_dir = f"{share_dir}/applications"
icons_dir = f"{share_dir}/icons"


os.makedirs(usr_bin_dir, exist_ok=True)
os.chdir(os.path.dirname(SPEC_LOCATION))
__main__.run(['--distpath', usr_bin_dir, SPEC_LOCATION])
os.chdir(CURRENT_DIR)
os.makedirs(debian_dir, exist_ok=True)
with open(os.path.join(debian_dir, "control"), "w") as file:
    file.write(CONTROL_CONTENT)
os.makedirs(icons_dir, exist_ok=True)
os.makedirs(app_dir, exist_ok=True)
with open(os.path.join(app_dir, f"{APP_NAME.lower()}.desktop"), "w") as file:
    file.write(DESKTOP_CONTENT)
shutil.copy(ICON_LOCATION, icons_dir)
os.system(f"dpkg-deb --build --root-owner-group {deb_name}")

