

# LBalance angle measurement app

This is another angle measuring app for android. It is written
in Python using the Kivy framework. It offers a number of different
graphic layouts at users choice.

The app ist open source as of the GNU General Public License (see LICENSE)

# Build

To build an apk file out of this repository, you need a GNU/Linux system
such as Debian, Ubuntu, Fedora, Gentoo or Archlinux.

For more detailed instructions read README.build

# Usage

The app may be used to measure angles or as a level balance.

## Calibration

To calibrate the device to a given plane use the 'calibration' button in the
top bar. More than one value can be recorded. The correction value is
calculated from the average of all recorded values. Best results are obtained
by using 2 values taken before and after rotating the device 180 degrees
parallel to the contacting plane.

To reset calibration long tap onto the 'calibration' button.

## Layouts

To enumerate layouts tap to the button 'layouts' in the top bar. A long tap
displays an overview of all available layouts.

## Angles display

Angles (physical convention polar coords) an sensor values are displayed
in the bottom bar.

# Screenshots

![Screenshot](fastlane/metadata/android/en-US/images/phoneScreenshots/1.png)
![Screenshot](fastlane/metadata/android/en-US/images/phoneScreenshots/4.png)
