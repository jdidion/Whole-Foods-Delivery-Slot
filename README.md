# Setup

* Install [chromedriver](https://chromedriver.chromium.org/)
* Install [terminal-notifier](https://github.com/julienXX/terminal-notifier) if you want to be notified via OSX notifications
* `pip install -r requirements.txt`

# Configuration

Copy `config-template.toml` to `config.toml` and modify it to your preferences.

# Usage

1. `python get_groceries.py`
2. Login to Amazon on the Chrome window that pops up
3. Checkout your Whole Foods shopping cart and navigate to the "Schedule your Order" window. Leave the script running.
4. Once a slot opens the script will notify you via your method of choice.
5. Proceed to checkout once you select a time slot. Stay Safe!