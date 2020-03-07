"""Quart development server with automatic restarts."""

# pylint: disable=import-outside-toplevel,broad-except

import os
import time
import traceback


def run():
    while True:
        try:
            from memegen.settings import get_config
            from memegen.factory import create_app
            config = get_config(os.getenv('FLASK_ENV', 'local'))
            app = create_app(config)
        except Exception:
            traceback.print_exc()
            print()
            time.sleep(3)
        else:
            app.run(debug=True)
            break


if __name__ == "__main__":
    run()
