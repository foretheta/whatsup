from typing import Optional, List, Tuple
from chalice import Chalice, Rate
from collections import namedtuple
from urllib.parse import urlparse, urlsplit
import requests
import yaml
import boto3
import logging


app = Chalice(app_name="whatsup")
app.log.setLevel(logging.DEBUG)

WebsiteStatus = namedtuple("WebsiteStatus", ["url", "status_code", "reason"])
Notification = namedtuple(
    "Notification", ["type", "message_down", "message_up", "icon_url", "webhook"]
)


# TODO: load config should validate configuration
def load_config(filepath="config.yaml") -> Tuple[List[dict], List[dict]]:
    with open(filepath) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    notifications = [Notification(**args) for args in config.get("notification", [])]
        
    return config.get("endpoints", []), notifications


def get_parameter_name(website):
    parsed = urlsplit(website)
    host = parsed.netloc
    return f"/Lambda/whatsup.sh/{host}"


def get_parameter_value(website):
    ssm = boto3.client("ssm")
    parameter_name = get_parameter_name(website)
    try:
        parameter = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
    except ssm.exceptions.ParameterNotFound:
        return None
    return parameter["Parameter"]["Value"]


def is_status_changed(website, website_status):
    parameter_value = get_parameter_value(website)
    return parameter_value != str(website_status.status_code)


def save_status(website, website_status):
    if is_status_changed(website, website_status):
        app.log.debug(f"New status code reported: {website_status}")
        ssm = boto3.client("ssm")
        parameter_name = get_parameter_name(website)

        parameter = ssm.put_parameter(
            Name=parameter_name,
            Value=str(website_status.status_code),
            Type="String",
            Overwrite=True,
        )
        return True
    return False


def push_notification(notification, website, website_status):
    if notification.webhook:
        if(website_status.status_code == 200):
            notification_message = notification.message_up
        else:
            notification_message = notification.message_down

        response = requests.post(
            notification.webhook,
            json={
                "text": f"{notification_message} - {website}",
                "icon_url": notification.icon_url,
            },
        )
        # TODO: check if response succeeds


def report_status_if_changed(notifications, website, website_status):
    changed = save_status(website, website_status)
    app.log.debug(website_status)

    if changed:
        for n in notifications:
            push_notification(n, website, website_status)


def check_endpoint_status(endpoint, cookie) -> WebsiteStatus:
    try:
        response = requests.get(endpoint, timeout=5,
                                allow_redirects=True, cookies=cookie)
        status_code = response.status_code
        reason = response.reason
    except requests.exceptions.ConnectionError:
        # TODO check if this is the only exception we need to handle (or BaseException)
        status_code = None
        reason = "ConnectionError"

    app.log.debug(reason)
    website_status = WebsiteStatus(endpoint, status_code, reason)
    return website_status


# idea: a function on an Endpoint dataclass
def get_url_with_port(url, port):
    endpoint = urlparse(url)
    endpoint._replace(netloc="{}:{}".format(endpoint.hostname, port))
    if not all([endpoint.scheme, endpoint.netloc]):
        raise ValueError
    return endpoint.geturl()


def check_status(endpoints, notifications):
    for endpoint in endpoints:
        cookie = endpoint.get("cookies", None)
        url = get_url_with_port(endpoint["url"], endpoint.get("port", "80")) # Check if port should be int
        status = check_endpoint_status(url, cookie)
        # TODO url is already included in status, no need to pass both around
        report_status_if_changed(notifications, url, status)


def run():
    endpoints, notifications = load_config()
    check_status(endpoints, notifications)


# Automatically runs every 5 minutes
@app.schedule(Rate(5, unit=Rate.MINUTES))
def scheduled_run(event={}):
    run()


# run on console with python app.py
if __name__ == "__main__":
    run()
