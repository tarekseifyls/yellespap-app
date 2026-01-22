[app]

# (str) Title of your application
title = YellesPaP Store

# (str) Package name
package.name = yellespap

# (str) Package domain
package.domain = org.yellespap

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas,ttf

# (str) Version of your application
version = 1.0

# (list) Application requirements
# REMOVED: 'sqlite3' (built-in), 'androidx' (java only).
# ADDED: 'openssl' is not needed for local, but kept for stability.
requirements = python3==3.10.13,kivy==2.2.1,kivymd==1.1.1,cython==0.29.36,setuptools<70,pillow,reportlab,jnius,sdl2_ttf==2.20.1

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/assets/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/assets/icon.png

# (str) Supported orientation
orientation = portrait

# (list) Permissions
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, USE_BIOMETRIC, USE_FINGERPRINT

# (int) Target Android API
android.api = 33

# (int) Minimum API
android.minapi = 21

# (bool) Use --private data storage
android.private_storage = True

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Skip trying to update the Python-for-Android code
android.skip_update = False

# (list) The Android archs to build for
# CRITICAL FIX: Added 'armeabi-v7a'. This prevents crashes on older/32-bit phones.
android.archs = arm64-v8a, armeabi-v7a

# (bool) Enable AndroidX support.
android.enable_androidx = True

# (list) Gradle dependencies to add
android.gradle_dependencies = androidx.biometric:biometric:1.1.0

# (bool) Automatically accept SDK license agreements
android.accept_sdk_license = True

# (str) python-for-android branch to clone
p4a.branch = master

[buildozer]

# (int) Log level
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1
