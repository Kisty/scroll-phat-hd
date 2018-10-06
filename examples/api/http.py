import scrollphathd

import threading
import time
from datetime import datetime

from scrollphathd.fonts import font5x7, font5x5

from argparse import ArgumentParser

try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty

from .action import Action
from .stoppablethread import StoppableThread

try:
    import http.client as http_status
except ImportError:
    import httplib as http_status

from flask import Blueprint, render_template, abort, request, jsonify, Flask

scrollphathd_blueprint = Blueprint('scrollhat', __name__)
api_queue = Queue()


class AutoScroll():
    _is_enabled = False
    _interval = 0.1

    def config(self, is_enabled="False", interval=0.1):
        self._interval = interval

        if is_enabled == "True":
            if self._is_enabled is False:
                self._is_enabled = True
                self.run()
        else:
            self._is_enabled = False

    def run(self):
        if self._is_enabled is True:
            # Start a timer
            threading.Timer(self._interval, self.run).start()
            # Scroll the buffer content
            scrollphathd.scroll()
            # Show the buffer
            scrollphathd.show()


@scrollphathd_blueprint.route('/autoscroll', methods=["POST"])
def autoscroll():
    response = {"result": "success"}
    status_code = http_status.OK

    data = request.get_json()
    if data is None:
        data = request.form
    try:
        api_queue.put(Action("autoscroll", (data["is_enabled"], float(data["interval"]))))
    except KeyError:
        response = {"result": "KeyError", "error": "keys is_enabled and interval not posted."}
        status_code = http_status.UNPROCESSABLE_ENTITY
    except ValueError:
        response = {"result": "ValueError", "error": "invalid data type(s)."}
        status_code = http_status.UNPROCESSABLE_ENTITY

    return jsonify(response), status_code


@scrollphathd_blueprint.route('/start', methods=["POST"])
def scroll():
    response = {"result": "success"}
    status_code = http_status.OK

    data = request.get_json()
    if data is None:
        data = request.form
    try:
        api_queue.put(Action("start", {}))
    except ValueError:
        response = {"result": "ValueError", "error": "invalid integer."}
        status_code = http_status.UNPROCESSABLE_ENTITY

    return jsonify(response), status_code


@scrollphathd_blueprint.route('/show', methods=["POST"])
def show():
    response = {"result": "success"}
    status_code = http_status.OK

    data = request.get_json()
    if data is None:
        data = request.form
    try:
        api_queue.put(Action("write", data["text"]))
    except KeyError:
        response = {"result": "KeyError", "error": "key 'text' not set"}
        status_code = http_status.UNPROCESSABLE_ENTITY

    return jsonify(response), status_code


@scrollphathd_blueprint.route('/clear', methods=["POST"])
def clear():
    response = {"result": "success"}
    status_code = http_status.OK

    api_queue.put(Action("clear", {}))
    return jsonify(response), status_code




def cleanup():
    # Reset the autoscroll
    autoscroll.config()
    # Clear the buffer before writing new text
    scrollphathd.clear()
    
# Brightness of the seconds bar and text
BRIGHTNESS = 0.3

def run():

    start = 0
    end = 0
    countdown_running = False
    finish_countdown = False

    while True:
        if (api_queue.qsize() > 0):
            action = api_queue.get(block=True)

            if action.action_type == "start":
                cleanup()

                # Uncomment the below if your display is upside down
                #   (e.g. if you're using it in a Pimoroni Scroll Bot)
                scrollphathd.rotate(degrees=180)
                
                start = time.time()
                end=start + 1 + 10 #25 * 60
                countdown_running = True
                finish_countdown = False

            if action.action_type == "clear":
                cleanup()
                countdown_running = False
                finish_countdown = False

        if countdown_running:
            if end>time.time():
                now=time.time()
                delta_t=end-now
                secs=int(delta_t)
                
                text=datetime.fromtimestamp(delta_t).strftime("%M:%S")
                scrollphathd.clear()
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
            else:
                countdown_running = False
                finish_countdown = True
                scrollphathd.clear()
                scrollphathd.show()
                scrollphathd.write_string(
                    "Time's up! ",
                    x=0, # Align to the left of the buffer
                    y=0, # Align to the top of the buffer
                    font=font5x7, # Use the font5x5 font we imported above
                    brightness=BRIGHTNESS # Use our global brightness value
                )
           
            if finish_countdown:
                scrollphathd.scroll()
                scrollphathd.show()
                time.sleep(0.1)

        scrollphathd.show()
        time.sleep(0.1)


def start_background_thread():
    api_thread = StoppableThread(target=run)
    api_thread.start()


scrollphathd_blueprint.before_app_first_request(start_background_thread)


# Autoscroll handling
autoscroll = AutoScroll()


def main():
    # Parser handling
    parser = ArgumentParser()
    parser.add_argument("-p", "--port", type=int, help="HTTP port.", default=8080)
    parser.add_argument("-H", "--host", type=str, help="HTTP host.", default="0.0.0.0")
    args = parser.parse_args()

    # TODO Check
    scrollphathd.set_clear_on_exit(True)
    scrollphathd.write_string(str(args.port), x=0, y=0, brightness=0.1)
    scrollphathd.show()

    # Flash usage
    app = Flask(__name__)
    app.register_blueprint(scrollphathd_blueprint, url_prefix="/scrollphathd")
    app.run(port=args.port, host=args.host)


if __name__ == '__main__':
    main()
