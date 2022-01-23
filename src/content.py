import requests
import re
import time
from calendar import timegm

class Content():
    def __init__(self, Requests, log):
        self.Requests = Requests
        self.log = log

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
    
    def get_name_from_season_id(self, content, seasonID):
        if seasonID == "UNKNOWN":
            return "UNKNOWN"

        seasonStartTime = 0
        act = ""

        for season in content["Seasons"]:
            if season["ID"] == seasonID:                
                seasonStartTime = timegm(time.strptime(season["StartTime"], "%Y-%m-%dT%H:%M:%SZ"))
                act = season["Name"].replace("ACT ", "A")
        for season in content["Seasons"]:
            if season["Type"] == "episode":
                episodeStartTime = timegm(time.strptime(season["StartTime"], "%Y-%m-%dT%H:%M:%SZ"))
                episodeEndTime = timegm(time.strptime(season["EndTime"], "%Y-%m-%dT%H:%M:%SZ"))
                if seasonStartTime >= episodeStartTime and seasonStartTime <= episodeEndTime:
                    name = "%s:%s" % (season["Name"].replace("EPISODE ", "E"), act)
                    self.log(f"retrieved season name: {name}")
                    return name
        

    def get_all_agents(self):
        rAgents = requests.get("https://valorant-api.com/v1/agents?isPlayableCharacter=true").json()
        agent_dict = {}
        agent_dict.update({None: None})
        for agent in rAgents["data"]:
            agent_dict.update({agent['uuid'].lower(): agent['displayName']})
        self.log(f"retrieved agent dict: {agent_dict}")
        return agent_dict
