import base64
import json
import time

import requests
from colr import color
import os

from src.logs import Logging


class Requests:
    lastEndpoint = ""
    def __init__(self):
        self.headers = {}
        self.Logging = Logging()
        self.log = self.Logging.log

        self.region = self.get_region()
        self.pd_url = f"https://pd.{self.region[0]}.a.pvp.net"
        self.glz_url = f"https://glz-{self.region[1][0]}.{self.region[1][1]}.a.pvp.net"
        self.log(f"Api urls: pd_url: '{self.pd_url}', glz_url: '{self.glz_url}'")
        self.region = self.region[0]
        self.lockfile = self.get_lockfile()

        self.puuid = ''
        #fetch puuid so its avaible outsite
        self.get_headers()
            
    def fetch(self, url_type: str, endpoint: str, method: str, rate_limit_seconds=5):
        try:
            if url_type == "glz":
                response = requests.request(method, self.glz_url + endpoint, headers=self.get_headers(), verify=False)
                self.log(f"fetch: url: '{url_type}', endpoint: {endpoint}, method: {method},"
                    f" response code: {response.status_code}")

                if not response.ok:
                    self.log("response not ok glz endpoint")
                    time.sleep(rate_limit_seconds+5)
                    self.headers = {}
                    self.fetch(url_type, endpoint, method)

                self.lastEndpoint = endpoint
                return response.json()

            elif url_type == "pd":
                response = requests.request(method, self.pd_url + endpoint, headers=self.get_headers(), verify=False)
                self.log(
                    f"fetch: url: '{url_type}', endpoint: {endpoint}, method: {method},"
                    f" response code: {response.status_code}")

                if response.status_code == 404:
                    return response

                if not response.ok:
                    self.log(f"response not ok pd endpoint, {response.text}")
                    time.sleep(rate_limit_seconds+5)
                    self.headers = {}
                    return self.fetch(url_type, endpoint, method, rate_limit_seconds=rate_limit_seconds+5)
                    
                self.lastEndpoint = endpoint
                return response

            elif url_type == "local":
                local_headers = {'Authorization': 'Basic ' + base64.b64encode(
                    ('riot:' + self.lockfile['password']).encode()).decode()}
                response = requests.request(method, f"https://127.0.0.1:{self.lockfile['port']}{endpoint}",
                                            headers=local_headers,
                                            verify=False)

                if self.lastEndpoint != "/chat/v4/presences":
                    self.log(
                        f"fetch: url: '{url_type}', endpoint: {endpoint}, method: {method},"
                        f" response code: {response.status_code}")

                self.lastEndpoint = endpoint
                return response.json()

            elif url_type == "custom":
                response = requests.request(method, f"{endpoint}", headers=self.get_headers(), verify=False)
                self.log(
                    f"fetch: url: '{url_type}', endpoint: {endpoint}, method: {method},"
                    f" response code: {response.status_code}")
                if not response.ok: self.headers = {}
                self.lastEndpoint = endpoint
                return response.json()

            
                
        except json.decoder.JSONDecodeError:
            self.log(f"JSONDecodeError in fetch function, resp.code: {response.status_code}, resp_text: '{response.text}")
            print(response)
            print(response.text)

    def get_region(self):
        path = os.path.join(os.getenv('LOCALAPPDATA'), R'VALORANT\Saved\Logs\ShooterGame.log')
        with open(path, "r", encoding="utf8") as file:
            while True:
                line = file.readline()
                if '.a.pvp.net/account-xp/v1/' in line:
                    pd_url = line.split('.a.pvp.net/account-xp/v1/')[0].split('.')[-1]
                elif 'https://glz' in line:
                    glz_url = [(line.split('https://glz-')[1].split(".")[0]),
                               (line.split('https://glz-')[1].split(".")[1])]
                if "pd_url" in locals().keys() and "glz_url" in locals().keys():
                    return [pd_url, glz_url]

    def get_current_version(self):
        path = os.path.join(os.getenv('LOCALAPPDATA'), R'VALORANT\Saved\Logs\ShooterGame.log')
        with open(path, "r", encoding="utf8") as file:
            while True:
                line = file.readline()
                if 'CI server version:' in line:
                    version_without_shipping = line.split('CI server version: ')[1].strip()
                    version = version_without_shipping.split("-")
                    version.insert(2, "shipping")
                    version = "-".join(version)
                    self.log(f"got version from logs '{version}'")
                    return version

    def get_lockfile(self):
        try:
            with open(os.path.join(os.getenv('LOCALAPPDATA'), R'Riot Games\Riot Client\Config\lockfile')) as lockfile:
                self.log("opened log file")
                data = lockfile.read().split(':')
                keys = ['name', 'PID', 'port', 'password', 'protocol']
                return dict(zip(keys, data))
        except FileNotFoundError:
            self.log("lockfile not found")
            raise Exception("Lockfile not found, you're not in a game!")


    def get_headers(self):
        if self.headers == {}:
            local_headers = {'Authorization': 'Basic ' + base64.b64encode(
                ('riot:' + self.lockfile['password']).encode()).decode()}
            response = requests.get(f"https://127.0.0.1:{self.lockfile['port']}/entitlements/v1/token",
                                    headers=local_headers, verify=False)
            entitlements = response.json()
            self.puuid = entitlements['subject']
            headers = {
                'Authorization': f"Bearer {entitlements['accessToken']}",
                'X-Riot-Entitlements-JWT': entitlements['token'],
                'X-Riot-ClientPlatform': "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjog"
                                         "IldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5"
                                         "MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9",
                'X-Riot-ClientVersion': self.get_current_version(),
                "User-Agent": "ShooterGame/13 Windows/10.0.19043.1.256.64bit"
            }
        return headers


