#!/usr/bin/env python

import time
from datetime import datetime

import scrollphathd
from scrollphathd.fonts import font5x7, font5x5

print("""
Scroll pHAT HD: Clock

Displays hours and minutes in text

Press Ctrl+C to exit!

""")

# Brightness of the seconds bar and text
BRIGHTNESS = 0.3

# Uncomment the below if your display is upside down
#   (e.g. if you're using it in a Pimoroni Scroll Bot)
scrollphathd.rotate(degrees=180)

start = time.time()
end=start + 1 + 3 #25 * 60

while end>time.time():
    scrollphathd.clear()
    now=time.time()
    delta_t=end-now
    secs=int(delta_t)
    
    text=datetime.fromtimestamp(delta_t).strftime("%M:%S")
    # Display the time (HH:MM) in a 5x5 pixel font
    scrollphathd.write_string(
        text,
        x=0, # Align to the left of the buffer
        y=0, # Align to the top of the buffer
        font=font5x5, # Use the font5x5 font we imported above
        brightness=BRIGHTNESS # Use our global brightness value
    )

    # int(time.time()) % 2 will tick between 0 and 1 every second.
    # We can use this fact to clear the ":" and cause it to blink on/off
    # every other second, like a digital clock.
    # To do this we clear a rectangle 8 pixels along, 0 down,
    # that's 1 pixel wide and 5 pixels tall.
    if int(time.time()) % 2 == 0:
        scrollphathd.clear_rect(8, 0, 1, 5)

    # Display our time and sleep a bit. Using 1 second in time.sleep
    # is not recommended, since you might get quite far out of phase
    # with the passing of real wall-time seconds and it'll look weird!
    #
    # 1/10th of a second is accurate enough for a simple clock though :D
    scrollphathd.show()
    time.sleep(0.1)

scrollphathd.clear()
scrollphathd.show()
scrollphathd.write_string(
    "Times up! ",
    x=0, # Align to the left of the buffer
    y=0, # Align to the top of the buffer
    font=font5x7, # Use the font5x5 font we imported above
    brightness=BRIGHTNESS # Use our global brightness value
)

while True:
    scrollphathd.scroll()
    scrollphathd.show()
    time.sleep(0.1)
