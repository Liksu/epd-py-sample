from epd_cal import Display, font22
import logging
import time

try:
    display = Display()

    height = 55
    width = 528 / 2
    y = 0

    for row in range(16):
        display.black.draw.rectangle([0, y, width, y + height], fill=row * 16, outline=0)
        display.red.draw.rectangle([width, y, 528, y + height], fill=row * 16, outline=0)

        x = 2
        text_color = 255 if row < 8 else 0
        display.black.draw.text((x, y + 2), str(row), fill=text_color, font=font22)
        display.red.draw.text((width + x, y + 2), str(row), fill=text_color, font=font22)

        x = 32
        text_color = 0 if row < 8 else 255
        display.black.draw.text((x, y + 2), str(row), fill=text_color, font=font22)
        display.red.draw.text((width + x, y + 2), str(row), fill=text_color, font=font22)
        y += height

    display.update()
    time.sleep(60)

    del display

except IOError as e:
    logging.debug(e)
