import requests
import re
import time
import json
from calendar import timegm

class Content():
    def __init__(self, Requests, log):
        self.Requests = Requests
        self.log = log
        self.Seasons = self.Requests.fetch("custom", "https://valorant-api.com/v1/seasons", "get")["data"]

    def get_content(self):
        content = self.Requests.fetch("custom", f"https://shared.{self.Requests.region}.a.pvp.net/content-service/v3/content", "get")           
        return content

    def get_latest_season_id(self, content):
        for season in content["Seasons"]:
            if season["IsActive"]:
                self.log(f"retrieved season id: {season['ID']}")
                return season["ID"]

    def get_last_season_id(self, content):
        currentSeason = 0
        latestSeasonID = ""
        seasons = content["Seasons"]

        nowTime = time.time()

        for season in seasons:
            if season["IsActive"]:
                currentSeason = int(re.findall("\d", season["Name"])[0])

        if currentSeason > 0:
            highestTime = 0

            for season in seasons:
                if season["Type"] == "act":
                    if season["Name"].find(str(currentSeason-1)) > 0:
                        endTime = timegm(time.strptime(season["EndTime"], "%Y-%m-%dT%H:%M:%SZ"))
                        if endTime > highestTime and endTime < nowTime:
                            highestTime = endTime                            
                            latestSeasonID = season["ID"]

            self.log(f"retrieved last season id: {latestSeasonID}")
            return latestSeasonID
        return "UNKNOWN"
    
    def get_name_from_season_id(self, seasonID):
        if seasonID == "UNKNOWN":
            return "UNKNOWN"

        act = ""
        parentUuid = ""

        for season in self.Seasons:
            uuid = season["uuid"]
            if uuid == seasonID:
                act = season["displayName"].replace("ACT ", "A")
                parentUuid = season["parentUuid"]

        for season in self.Seasons:
            uuid = season["uuid"]
            if uuid == parentUuid:
                episode = "%s:%s" % (season["displayName"].replace("EPISODE ", "E"), act)
                return episode        

    def get_all_agents(self):
        rAgents = requests.get("https://valorant-api.com/v1/agents?isPlayableCharacter=true").json()

        agent_dict = {}
        agent_dict.update({None: None})

        for agent in rAgents["data"]:
            agent_dict.update({agent['uuid'].lower(): agent['displayName']})

        self.log(f"retrieved agent dict: {agent_dict}")
        return agent_dict
