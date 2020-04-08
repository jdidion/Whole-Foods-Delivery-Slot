from abc import ABCMeta, abstractmethod
import json
import sys
import time
from typing import Sequence

import bs4
from selenium import webdriver
import toml


NOTIFIERS = {}
NEGATIVE_PATTERN = "No delivery windows available"
POSITIVE_PATTERN = "Select"


class NotifierMeta(ABCMeta):
    def __new__(mcls, name, bases, namespace, **kwargs):
        cls = super().__new__(mcls, name, bases, namespace, **kwargs)
        NOTIFIERS[getattr(cls, "name")()] = cls
        return cls


class Notifier(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def name(cls) -> str:
        pass

    @abstractmethod
    def notify(self, text: str):
        pass


class PyncNotifier(Notifier, metaclass=NotifierMeta):
    @classmethod
    def name(cls) -> str:
        return "pync"

    def __init__(self, _):
        import pync
        self.mod = pync

    def notify(self, text: str):
        self.mod.notify(text)


class SlackNotifier(Notifier, metaclass=NotifierMeta):
    @classmethod
    def name(cls) -> str:
        return "slack"

    def __init__(self, conf):
        from urllib import request
        self.request = request
        self.url = conf["url"]

    def notify(self, text: str):
        try:
            post = {"text": text}
            req = self.request.Request(
                self.url,
                data=json.dumps(post).encode("ascii"),
                headers={"Content-Type": "application/json"}
            )
            self.request.urlopen(req)
        except Exception as e:
            print(f"Error sending message to slack {e}")


def get_wf_slot(amazon_conf, notifiers: Sequence[Notifier]):
    def notify(text: str):
        for notifier in notifiers:
            notifier.notify(text)

    driver = webdriver.Chrome()
    driver.get(amazon_conf["url"])
    time.sleep(amazon_conf["wait_setup"])

    print("Trying forever to get you a delivery slot...hit Ctrl-C to exit")

    while True:
        driver.refresh()
        html = driver.page_source
        soup = bs4.BeautifulSoup(html, features="html.parser")

        try:
            alerts = soup.find_all("h4", class_="a-alert-heading")
            for alert in alerts:
                if NEGATIVE_PATTERN in alert.contents[0]:
                    print("no delivery windows :(")
                    time.sleep(amazon_conf["wait_fail"])
                    break
                elif POSITIVE_PATTERN in alert.contents[0]:
                    print("got delivery windows!")
                    notify("Slots for delivery opened!")
                    time.sleep(amazon_conf["wait_success"])
                    break
            else:
                print("unrecognized page")
                notify("Unrecognized page!")
                time.sleep(amazon_conf("wait_error"))
        except AttributeError:
            continue


def main(conf):
    amazon_conf = conf.pop("amazon")
    notifiers = [
        NOTIFIERS[plugin_name](conf.get(plugin_name, {}))
        for plugin_name in conf.pop("notifiers")
    ]
    get_wf_slot(amazon_conf, notifiers)


if __name__ == "__main__":
    config_file = sys.argv[1] if len(sys.argv) > 1 else "config.toml"
    with open(config_file, "r") as inp:
        config = toml.load(inp)

    main(config)
