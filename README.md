# Thermal Printer Alarm Clock

This is the source code for my Thermal Printer Alarm Clock. You can find a more detailed description here:

https://hackaday.io/project/169436-thermal-printer-alarm-clock

## Project Structure

* The `aws lambda` directory contains two handlers for AWS Lambda: One to parse the university canteen's XML feed and one to set the alarm configuration via a HTTP request.
* The `micropython` directory contains all the code that runs on the esp8266 microcontroller. The following tools might come in handy if you work with the code: `mpy-cross`, `rshell`.
* The `mobile_app` directory contains the code for the mobile app. The mobile app is a Progressive Web App created with React. To work with the code install `yarn` and check the folder's README file.

## Miscellaneous

I cleaned the source code of all actual URLs. I did not implement any authentication mechanisms and I do not want you to set my alarm ;-).