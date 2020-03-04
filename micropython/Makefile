SHELL = bash

deploy: build upload
build: clean copy crosscompile

connect:
	rshell -p /dev/ttyUSB0

clean:
	rm -rf build
	mkdir build
	mkdir build/lib

copy:
	cp src/main.py build/
	cp src/boot.py build/

crosscompile:
	mpy-cross -o build/lib/logging.mpy src/lib/logging.py
	mpy-cross -o build/thermal_printer_alarm.mpy src/thermal_printer_alarm.py
	mpy-cross -o build/lib/Adafruit_Thermal.mpy src/lib/Adafruit_Thermal.py
	mpy-cross -o build/lib/sdcard.mpy src/lib/sdcard.py
	mpy-cross -o build/lib/urequests.mpy src/lib/urequests.py

upload:
	rshell -p /dev/ttyUSB0 rsync -m build /pyboard

get_alarm: 
	curl -s "https://xxx.s3.eu-central-1.amazonaws.com/xxx" | jq

set_alarm:
	curl -d "{\"time\": $$(($$(date +%s)+60)), \"active\": true}" -H "Content-Type: application/json" -X POST https://xxx.execute-api.eu-central-1.amazonaws.com/xxx

unset_alarm:
	curl -d "{\"active\": false}" -H "Content-Type: application/json" -X POST https://xxx.execute-api.eu-central-1.amazonaws.com/xxx

get_menu:
	curl "https://xxx.s3.eu-central-1.amazonaws.com/xxx"