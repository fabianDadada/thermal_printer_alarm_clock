"""This module contains all the actual logic of the project.

The main method is run when the microcontroller starts and afer each sleep cycle.
"""

import logging
import machine
import network
import ntptime
import os
import sdcard
import ujson
import urequests
import utime
from Adafruit_Thermal import Adafruit_Thermal


RELAY_PIN = 5
SECS_TO_SLEEP = 4 * 60
UNIX_TIMESTAMP_2000 = 946684800

HOST = "http://s3.eu-central-1.amazonaws.com"
ALARM_PATH = "/xxx"
MENU_PATH = "/xxx"

# The logger writes logs to the serial interface.
logger = logging.getLogger("Logger")
printer = Adafruit_Thermal(baudrate=19200)
relay_pin = machine.Pin(RELAY_PIN, machine.Pin.OUT)


def mount_sd():
    logger.info("mounting sd...")
    try:
        sd = sdcard.SDCard(machine.SPI(1), machine.Pin(15))
        os.mount(sd, "/sd")
    except Exception as e:
        logger.exc(e, "sd could not be mounted.")
        failed_mounts_count = increment_counter("failed_mounts")
        if failed_mounts_count == 1:
            print_error_msg("SD-Karte konnte nicht gelesen werden! Sag besser mal Fabian bescheid!")
    else:
        reset_counter("failed_mounts")

def connect_wifi():
    logger.info("reading wifi config...")
    with open("/sd/wifi.json") as json_file:
        wifi_conf = ujson.load(json_file)

    logger.info("connecting to wifi...")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(wifi_conf["ssid"], wifi_conf["password"])

    for _ in range(10):
        if sta_if.isconnected():
            logger.info("wifi is connected.")
            reset_counter("failed_connections")
            return
        
        utime.sleep(1)

    logger.warning("Could not connect to wifi.")

    failed_connection_count = increment_counter("failed_connections")
    if failed_connection_count == 50:
        print_error_msg("WLAN-Verbindung fehlgeschlagen!")

def increment_counter(counter_name):
    logger.info("incrementing counter '{}'...".format(counter_name))

    file = "/{}".format(counter_name)

    try:
        with open(file, "r") as infile:
            count = int(infile.read())
    except Exception as e:
        logger.exc(e, "Could not read counter.")
        count = 0

    logger.info("old value: {}.".format(count))
    count += 1
    logger.info("new value: {}.".format(count))

    try:
        with open(file, "w") as outfile:
            outfile.write(str(count))
    except Exception as e:
        logger.exc(e, "Could not write counter.")

    return count

def reset_counter(counter_name):
    logger.info("resetting counter '{}'...".format(counter_name))

    file = "/{}".format(counter_name)
    try:
        with open(file, "w") as outfile:
            outfile.write("0")
    except Exception as e:
        logger.exc(e, "Could not reset counter.")

def print_error_msg(msg):
    turn_printer_on()

    printer.feed(2)
    printer.println(msg)
    printer.feed(2)

    utime.sleep(2)
    turn_printer_off()

def get_alarm_time():
    try:
        logger.info("requesting alarm config from server...")
        re = urequests.get(HOST + ALARM_PATH)
        alarm_data = re.json()
        alarm_time = alarm_data["time"] if alarm_data["active"] else 0

        logger.info("caching alarm time...")
        try:
            with open("/alarm_time", "w") as alarm_file:
                alarm_file.write(str(alarm_time))
        except Exception:
            logger.warning("Could not cache alarm time.")

        return alarm_time
    except Exception:
        logger.info("using cached alarm time instead...")

        try:
            with open("/alarm_time") as alarm_file:
                alarm_time = alarm_file.read()
                return int(alarm_time)
        except Exception:
            logger.warning("Could not read cached alarm time.")
            return 0

def should_print():
    alarm_time = get_alarm_time()
    def time_delta():
        # For Micropython timestamp is number of seconds since Jan 1, 2000.
        local_time = utime.time() + UNIX_TIMESTAMP_2000
        logger.info("local_time={}, alarm_time={}".format(local_time, alarm_time))
        return alarm_time - local_time

    logger.info("comparing local time with alarm time...")
    max_delta = 3 * SECS_TO_SLEEP
    if  0 <= time_delta() < max_delta:
        logger.info("Alarm is triggered.")

        while time_delta() > 1:
            logger.info("waiting for exact alarm time...")
            utime.sleep(1)

        return True
    else:
        logger.info("Alarm is not triggered.")
        return False

def turn_printer_on():
    logger.info("turning printer on...")
    relay_pin.on()
    utime.sleep(3)

def turn_printer_off():
    logger.info("turning printer off...")
    relay_pin.off()

def print_comic_strip():
    logger.info("printing comic strip...")
    with open("/sd/current_comic_id.json", "r+") as json_file:
        current_comic_id = ujson.load(json_file)
        logger.info("current_comic_id={}".format(current_comic_id))
        comic_strip_count = sum(1 for _ in os.ilistdir("/sd/comic_strips"))
        logger.info("comic_strip_count={}".format(comic_strip_count))
        if current_comic_id >= comic_strip_count:
            current_comic_id = 0
        else:
            current_comic_id += 1

        json_file.seek(0)
        json_file.write(ujson.dumps(current_comic_id))

    printer.feed()
    printer.printBMPImage("/sd/comic_strips/{}.bmp".format(current_comic_id), True)
    printer.feed(4)

def print_mensa_menu():
    logger.info("printing mensa menu...")
    try:
        re = urequests.get(HOST + MENU_PATH)

        if re.content == "":
            return

        printer.justify("C")
        printer.setSize("L")
        printer.println("Heute")
        printer.println("in der Mensa")
        printer.setSize("S")
        printer.justify("L")

        for char in re.content:
            if char == ord("\n"):
                printer.underlineOff()
            if char == ord("#"):
                printer.underlineOn()
                char = ord("\n")

            printer.writeBytes(char)
        
        for _ in range(4):
            printer.feed()
    except Exception as e:
        logger.exc(e, "Could not print mensa menu.")

def deep_sleep():
    logger.info("going into deep sleep...")
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    rtc.alarm(rtc.ALARM0, SECS_TO_SLEEP * 1000)
    machine.deepsleep()

def main():
    try:
        mount_sd()
        connect_wifi()

        try:
            ntptime.settime()
        except Exception:
            pass
    
        if should_print():
            turn_printer_on()
            print_comic_strip()
            print_mensa_menu()
            utime.sleep(SECS_TO_SLEEP)
            turn_printer_off()
    except Exception as e:
        logger.exc(e, "Error in main function.")

    deep_sleep()
