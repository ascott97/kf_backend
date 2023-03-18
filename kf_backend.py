import logging, os, json
from datetime import datetime
from urllib3.util.retry import Retry

import requests, dateutil.parser
from requests.adapters import HTTPAdapter



class KFBackend:
    def __init__(self, base_url: str, api_key: str):
        """Setup requests.Session with retries and x-api-key header set for all http requests"""
        self.base_url = base_url
        self.session = requests.Session()
        retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[429, 500])
        self.session.mount("https://", HTTPAdapter(max_retries=retries))
        self.session.headers.update({"x-api-key": api_key})

    def handler(self, site_id: str, after: str):
        outages = self._get_outages()
        site_info = self._get_site_info(site_id)
        filtered_outages = self._filter_outages(
            outages=outages, site_info=site_info, after=dateutil.parser.parse(after)
        )
        self._post_site_outages(site_id=site_id, outages=filtered_outages)

    def _get_outages(self) -> list:
        """Get all outages from the /outages endpoint and return it as a list of dicts."""
        logging.info(f"getting outages from: {self.base_url}/outages")
        response = self.session.get(f"{self.base_url}/outages")
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"unable to get outages received error:  {response.text}")
            exit(1)

    def _get_site_info(self, site_id: str) -> dict:
        """Get site info from the /site-info/{siteId} endpoint and return it as a dict."""
        logging.info(f"getting site info with from {self.base_url}/site-info/{site_id}")
        response = self.session.get(f"{self.base_url}/site-info/{site_id}")
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(
                f"unable to get site info for id: {site_id} received error: {response.text}"
            )
            exit(1)

    def _post_site_outages(self, site_id: str, outages: list) -> None:
        """Post a list of outages(dict) to the /site-outages/{siteId} endpoint."""
        response = self.session.post(
            f"{self.base_url}/site-outages/{site_id}", data=json.dumps(outages)
        )
        if response.status_code == 200:
            logging.info(
                f"received 200 response from {self.base_url}/site-outages/{site_id}"
            )
        else:
            logging.error(
                f"failed to post site outages received status code: {response.text}"
            )
            exit(1)

    def _filter_outages(self, outages: list, site_info: dict, after: datetime) -> list:
        """Filters out any outages that began before the passed in date or don't have an ID that is in the list of
        devices in the site info and sets the device name in outage dict"""
        filtered = []
        devices = site_info.get("devices")
        for outage in outages:
            device = next((x for x in devices if x.get("id") == outage.get("id")), None)
            if device and dateutil.parser.parse(outage.get("begin")) >= after:
                outage["name"] = device.get("name")
                filtered.append(outage)

        return filtered


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    api_key = os.environ.get("KF_API_KEY")
    if not api_key:
        logging.warning("environment variable needed: KF_API_KEY")
        exit(1)
    KFBackend(
        "https://api.krakenflex.systems/interview-tests-mock-api/v1", api_key
    ).handler(site_id="norwich-pear-tree", after="2022-01-01T00:00:00.000Z")
