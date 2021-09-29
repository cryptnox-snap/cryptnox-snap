# Create dmg installation file

To follow this tutorial you will need to run version of MacOS.

## Generate .app file

`pyinstaller cryptnoxcard_mac_os.spec`

## Create folder with .app file

Create empty folder and copy .app file from cryptnoxcli/dist floder into it.

## Create dmg file

[How to create dmg file](https://kb.parallels.com/123895)

To convert .APP file to .DMG format follow the steps below:

1. Create a new folder on Mac and copy *.APP file to the new folder.

2. Open Disk Utility > File > New Image > Blank Image.

3. Edit name and size fields if necessary.

4. Specify the name of the DMG file and the path where the file should be created and click Save button.

## Optional

To make more conventional looking dmg installer
[this tutorial](https://www.youtube.com/watch?v=Cal9l-ajWrE) can be 
followed.

1. Create a link/shortcut to /Applications folder by right-clicking on the Applications folder and selecting Make Alias then drag it into the dmg folder
2. Arrange icons as needed.
Press `CMD+J` to show the View Options window and adjust view settings as needed.
From `Background`: section choose `Picture` then Drag and drop the image you want to use as the background where it says Drag image here.

## Compress and convert to Read-only

1. From Disk Utility right-click on cryptnoxcard.dmg disk image and select Image from "cryptnoxcard.dmg".

2. In the Save As field enter a new name for the file like cryptnoxcardfinal.dmg.

3. From the Image Format drop-down select read-only then click Save or from Terminal:

`hdiutil convert -format UDZO -o cryptnoxcardfinal.dmg cryptnoxcard.dmg`
