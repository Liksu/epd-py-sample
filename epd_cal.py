#!/usr/bin/python3
# -*- coding:utf-8 -*-
import sys
import logging
import time
from PIL import Image, ImageDraw, ImageFont
from gcal import get_events as get_google_events
from gandr import get_events as get_gandr_events
import datetime
import traceback
import pprint

sys.path.append('./lib')
from waveshare_epd import epd7in5b_HD

logging.basicConfig(level=logging.INFO)

font_path = './fonts/calibri.ttf'
font_bold_path = './fonts/calibrib.ttf'
font28 = ImageFont.truetype(font_path, 28, encoding='unic')
font28_bold = ImageFont.truetype(font_bold_path, 28, encoding='unic')
font26 = ImageFont.truetype(font_path, 26, encoding='unic')
font26_bold = ImageFont.truetype(font_bold_path, 26, encoding='unic')
font24 = ImageFont.truetype(font_path, 24, encoding='unic')
font22 = ImageFont.truetype(font_path, 22, encoding='unic')
font20 = ImageFont.truetype(font_path, 20, encoding='unic')
font18 = ImageFont.truetype(font_path, 18, encoding='unic')
texts = []
google_red = False


class Text:
    draw = None

    def write(self, hide=False):
        logging.debug('Text.write')
        fill = 255 if hide else 0
        self.draw.text((self.x, self.y), self.text, font=self.font, fill=fill)

    def __init__(self, layer, x, y, text, font=font20):
        logging.debug('Text.init: ' + text)
        self.draw = layer.draw
        self.x = x
        self.y = y
        self.text = text
        self.font = font

        self.write()

    def __del__(self):
        logging.debug('Text.del')
        self.write(True)


class Layer:
    image = None
    draw = None

    def __init__(self):
        self.image = Image.new('1', (528, 880), 255)  # 255: clear the frame
        self.draw = ImageDraw.Draw(self.image)


class Display:
    black = Layer()
    red = Layer()

    def __init__(self, do_nothing=False):
        logging.debug('Display.init')
        self.do_nothing = do_nothing
        if self.do_nothing:
            return
        self.epd = epd7in5b_HD.EPD()
        logging.info('Init')
        self.epd.init()
        logging.info('Clear')
        self.epd.Clear()

    def update(self):
        logging.debug('Display.update')
        if self.do_nothing:
            return
        self.epd.display(self.epd.getbuffer(self.black.image), self.epd.getbuffer(self.red.image))

    def __del__(self):
        logging.debug('Display.del')
        if self.do_nothing:
            return
        self.epd.Clear()
        self.epd.sleep()


def get_now(show_seconds=False):
    time_format = '%H:%M' + (':%S' if show_seconds else '')
    return datetime.datetime.now().strftime(time_format)


def get_today():
    localtime = time.localtime()
    month_name = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][localtime.tm_mon - 1]
    weekday_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][localtime.tm_wday]

    return weekday_name + ', ' + ' '.join([str(localtime.tm_mday), month_name, str(localtime.tm_year)])


def output(display, google_events, gandr_events):
    now = get_now()
    y = 2

    for text in texts:
        text.__del__()

    today = get_today()
    font = font28_bold
    width, height = font.getsize(today)
    texts.append(Text(display.black, 2, y, today, font))
    y += height + 12

    for index, event in enumerate(gandr_events):
        font = font22
        width, height = font.getsize(event)
        texts.append(Text(display.black, 2, y, event, font))
        y += height + 8

    if len(gandr_events):
        y += 10

    for index, event in enumerate(google_events):
        start = event['start']
        layer = display.black
        font = font24
        if event['current']:
            layer = display.red

        time_range = start + ' - ' + event['end']
        width, height = font.getsize(time_range)

        texts.append(Text(layer, 2, y, time_range, font))
        texts.append(Text(layer, 16 + width, y, event['summary'], font))

        y += height + 8

    logging.info('Output to display')
    display.update()


def check_google():
    events = get_google_events()
    new_events_ids = []
    new_current_ids = []
    now = get_now()
    for e in events:
        new_events_ids.append(e['id'] + '=' + e['updated'])
        e['current'] = e['start'] <= now <= e['end']
        if e['current']:
            new_current_ids.append(e['id'])

    pprint.pprint(events)
    return events, '/'.join(new_events_ids), '/'.join(new_current_ids)


def check_gandr():
    return get_gandr_events()


def main():
    events_ids = ''
    current_ids = ''

    try:
        logging.info('Start')
        display = Display()

        output(display, [], [])

        while True:
            now = get_now(show_seconds=True)
            logging.info(now + ' Get events')
            google_events, google_new_events_ids, google_new_current_ids = check_google()
            gandr_events = check_gandr()
            pprint.pprint(gandr_events)

            if google_new_events_ids != events_ids or google_new_current_ids != current_ids:
                events_ids = google_new_events_ids
                current_ids = google_new_current_ids

                logging.info('Create texts')
                output(display, google_events, gandr_events)

            logging.info('Pause')
            time.sleep(300)

        logging.info('Finish')
        del display

    except IOError as e:
        logging.debug(e)

    except KeyboardInterrupt:
        logging.info("Interrupt by Ctrl+C")
        del display
        epd7in5b_HD.epdconfig.module_exit()
        exit()


if __name__ == '__main__':
    main()
