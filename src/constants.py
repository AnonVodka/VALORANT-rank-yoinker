from typing import Tuple
from colr import color
import requests

class Agents:
    def __init__(self):
        self.agents = {
            "neon": (28, 69, 161),
            "none": (100, 100, 100),
            "viper": (48, 186, 135),
            "yoru": (52, 76, 207),
            "astra": (113, 42, 232),
            "breach": (217, 122, 46),
            "brimstone": (217, 122, 46),
            "cypher": (245, 240, 230),
            "jett": (154,222,255),
            "kay/o": (133, 146, 156),
            "killjoy": (255, 217, 31),
            "omen": (71, 80, 143),
            "phoenix": (254, 130, 102),
            "raze": (217, 122, 46),
            "reyna": (181, 101, 181),
            "sage": (90, 230, 213),
            "skye": (192, 230, 158),
            "sova": (37, 143, 204),
            "chamber": (200, 200, 200),
            "fade": (92, 92, 94)
        }
    def get(self, agent: str) -> Tuple[int, int, int]:
        if agent not in self.agents:
            return (255, 255, 255)
        return self.agents[agent]

    def __getitem__(self, agent: str) -> Tuple[int, int, int]:
        return self.get(agent)


agents = Agents()

GAMEPODS = requests.get("https://valorant-api.com/internal/locres/en-US").json()["data"]["UI_GamePodStrings"]

symbol = "■"
PARTYICONLIST = [
    color(symbol, fore=(227, 67, 67)),
    color(symbol, fore=(216, 67, 227)),
    color(symbol, fore=(67, 70, 227)),
    color(symbol, fore=(67, 227, 208)),
    color(symbol, fore=(94, 227, 67)),
    color(symbol, fore=(226, 237, 57)),
    color(symbol, fore=(212, 82, 207)),
    symbol
]

def hexToRgb(hex):
    return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))

class Ranks:
    def __init__(self):
        self.ranks = [ 
            color("Unranked" if "Unused" in x["tierName"] else x["tierName"].capitalize(), fore=hexToRgb(x["color"])) 
            for x in requests.get("https://valorant-api.com/v1/competitivetiers").json()["data"][-1]["tiers"] 
        ]
    def get(self, rankID: int) -> str:
        if rankID < 0 or rankID >= len(self.ranks):
            return color("UNKNOWN", fore=(100, 100, 100))
        return self.ranks[rankID]

    def __getitem__(self, rankID: int) -> str:
        return self.get(rankID)

ranks = Ranks()