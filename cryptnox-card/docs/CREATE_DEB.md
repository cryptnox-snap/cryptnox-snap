# Instructions for creating DEB file
To do the following steps you must use debian based operating system.
## Create deb file using script:
Delete cryptnoxcli/dist directory if it exists.
To create deb file you can run provided script `create_deb.py` inside 
pipenv environment.

Deb file will be located inside cryptnoxcli/dist directory.

## Create binaries using pyinstaller:

Run following command inside cryptnoxcli directory:

  `pyinstaller cryptnoxcard.spec --onefile`

After that dist and build directories should be created inside the cryptnoxcli/dist
directory.

## Create the working directory:

Directory name should follow the naming convention described in the following line.

  `<name>_<version>-<revision>_<architecture>`
  
To reproduce our deb files name use:

  `mkdir cryptnox_1.0-1_all`
  
## Create bin directory:

  `mkdir -p cryptnox_1.0-1_all/usr/local/bin`
  
## Copy binaries and dependencies

Copy contents of the dist folder into the bin directory.

## Create the control file

  `mkdir cryptnox_1.0-1_all/DEBIAN`

  `touch cryptnox_1.0-1_all/DEBIAN/control`

## Fill in the control file

Populate the control file with information about the app:

<pre><code>Package: cryptnoxcard
Version: 1.0
Architecture: all
Maintainer: Internal Pointers &lt;info@internalpointers.com&gt
Description: Program for using Cryptnox cards
</code></pre>

## Create icons and applications folder

Inside the `touch cryptnox_1.0-1_all` directory
run:

  `mkdir -p usr/share/applications`

  `mkdir -p usr/share/icons`

## Copy icon:

Copy an icon for the app into the `usr/share/icons` folder.

## Create .desktop file:

When inside the `usr/share/applications` folder run:

  `touch cryptnox.desktop`

## Populate the .desktop file:

Example for populating .desktop file:

<pre><code>[Desktop Entry]
Version=1.0
Name=cryptnox
GenericName=CRYPTNOX
Comment=Cryptnox client application
Exec=/usr/local/bin/cryptnox/cryptnoxcard
TryExec=/usr/local/bin/cryptnox/cryptnoxcard
Icon=/usr/share/icons/cryptnoxcard.ico
Terminal=true
Type=Application
Categories=Utility;
Keywords=Backup;</code></pre>

## Create .deb file:

In `cryptnox_1.0-1_all` directory run:

  `dpkg-deb --build --root-owner-group cryptnox_1.0-1_all`
