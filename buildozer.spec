[app]

# (str) Title of your application
title = YellesPaP Store

# (str) Package name
package.name = yellespap

# (str) Package domain (needed for android/ios packaging)
package.domain = org.yellespap

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttf

# (str) Version of your application
version = 1.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.2.1,kivymd==1.1.1,sdl2_ttf==2.0.15,pillow,reportlab,sqlite3,jnius,androidx

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/assets/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/assets/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) Permissions
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET, USE_BIOMETRIC, USE_FINGERPRINT

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Skip trying to update the Python-for-Android code
android.skip_update = False

# (list) The Android archs to build for
android.archs = arm64-v8a

# (bool) Enable AndroidX support. Enable when 'android.api' >= 28.
android.enable_androidx = True

# (list) Gradle dependencies to add
android.gradle_dependencies = androidx.biometric:biometric:1.1.0

# (bool) Automatically accept SDK license agreements
android.accept_sdk_license = True

# (str) python-for-android branch to clone
# CRITICAL: 'develop' branch handles AndroidX/Biometrics much better than master
p4a.branch = develop

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
