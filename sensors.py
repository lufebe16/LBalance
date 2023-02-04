
import logging
try:
        import jnius
except ImportError:
        jnius = None

try:
  from android import activity
except ImportError:
  activity = None

import time
from kivy.clock import mainthread

SensorReader = None
#SensorResult = None

if jnius is not None:
    Intent = jnius.autoclass('android.content.Intent')
    Uri = jnius.autoclass('android.net.Uri')
    PythonActivity = jnius.autoclass('org.kivy.android.PythonActivity')
    currentActivity = jnius.cast('android.app.Activity', PythonActivity.mActivity)

    # dafür brauchts androidx.preference dependency angabe:
    # DocumentsContract = jnius.autoclass('android.provider.DocumentsContract')
    # DocumentFile = jnius.autoclass('androidx.documentfile.provider.DocumentFile')

    # Build = jnius.autoclass("android.os.Build")
    # Version = jnius.autoclass("android.os.Build$VERSION")
    # VCodes = jnius.autoclass("android.os.Build$VERSION_CODES")

    SensorReader = jnius.autoclass('org.lufebe16.sensor.SensorReader')
    #SensorResult = jnius.autoclass('org.lufebe16.sensor.SensorResult')
