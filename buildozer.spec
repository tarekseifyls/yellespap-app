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

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
# CRITICAL: jnius and androidx are needed for the fingerprint code
requirements = python3,kivy==2.2.1,kivymd==1.1.1,sdl2_ttf==2.0.15,pillow,reportlab,sqlite3,jnius,androidx

# (str) Custom source folders for requirements
# Sets custom source for any requirements with recipes
# requirements.source.kivymd = ../../kivymd

# (str) Presplash of the application
# (Uncomment these if you add these images to your assets folder)
#presplash.filename = %(source.dir)s/assets/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/assets/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) Permissions
# CRITICAL: USE_BIOMETRIC needed for login
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

# (bool) Process some other custom gradle tasks
#android.gradle_tasks = assembleDebug

# (list) The Android archs to build for
# arm64-v8a is for modern phones, armeabi-v7a is for older ones
android.archs = arm64-v8a, armeabi-v7a

# (bool) Enable AndroidX support. Enable when 'android.api' >= 28.
# CRITICAL: Must be True for Biometrics
android.enable_androidx = True

# (list) Gradle dependencies to add
# CRITICAL: This downloads the Java code for the fingerprint scanner
android.gradle_dependencies = androidx.biometric:biometric:1.1.0

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
