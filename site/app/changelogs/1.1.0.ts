const changelog = `## :fire: Update 1.1.0 is out

### What’s changed
- :sparkles: Refactored Epic avatar upload with a proper callback and improved error handling  
- :frame_photo: Added option **“Load default avatars”** to load a default image if the avatar is not found
- :globe_with_meridians: Added support for **“Load default avatars” via URL query params** in the backend  
- :information_source: Added descriptive **tooltips** for UI elements  
- :open_file_folder: Added support for selecting **.jpg, .jpeg** images in the file dialog  
- :art: Updated constants, colors, and tooltips  
- :tools: Improved logging and overall robustness in avatar management  
- Update internal SDK to match Rocket League's new version
### How to install
- The auto updater should update automatically  
- If not, you can download the latest release at :point_right: https://rlpfp.borgox.tech/  

:heart: Please note: backend has been more stable in this version, but if you find issues, let me know so I can patch them quickly.  Also a minor bug was fixed but should up the request count by 1 for each time you set an avatar (so 1+1 = 2)`;

export default changelog;