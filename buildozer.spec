[app]
title = Ironvale Defense
package.name = ironvaledefense
package.domain = org.koteuka404

source.dir = android_src
source.include_exts = py,png,jpg,jpeg,ttf,json,atlas
source.exclude_dirs = __pycache__,.git,.idea,.vscode,venv,.venv,build,bin

version = 0.1.0
requirements = python3,kivy==2.3.1,filetype

orientation = landscape
fullscreen = 1

icon.filename = %(source.dir)s/assets/icon.png

# The game is fully offline and requests no dangerous Android permissions.
android.api = 35
android.minapi = 23
android.ndk = 25b
android.ndk_api = 23
android.archs = arm64-v8a
android.bootstrap = sdl2
android.accept_sdk_license = True
android.private_storage = True
android.allow_backup = True

# Prevent the display from sleeping during a battle.
android.permissions = WAKE_LOCK

android.gradle_options = -Xmx4096m -Dfile.encoding=UTF-8

log_level = 2
warn_on_root = 1

[buildozer]
log_level = 2
warn_on_root = 1
