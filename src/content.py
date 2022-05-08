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
    
    # gets info about the current act
    def get_current_season_info(self, content):
        for season in content["Seasons"]:
            if season["IsActive"] and season["Type"] == "act":
                id = season["ID"]
                name = season["Name"]
                startTime = season["StartTime"]
                endTime = season["EndTime"]

                self.log(f"retrieved season id: {id}")
                return {
                    "ID": id,
                    "Name": name,
                    "StartTime": startTime,
                    "EndTime": endTime
                }

    # this needs to be recoded
    # each episode only has 3 acts
    # if we are in act 1, we need to get the last act of the previous episode
    # possible layout:
    # Episode 1: ACT 1, ACT 2, ACT 3
    # Episode 2: ACT 1, ACT 2, ACT 3
    # Episode 3: ACT 1, ACT 2, ACT 3
    # Episode 4: ACT 1, ACT 2, ACT 3

    def get_last_season_id(self, content):
        currentEpisode = 0
        currentAct = 0
        episodeStartTime = 0
        episodeEndTime = 0

        lastSeasonID = ""

        seasons = content["Seasons"]

        # get current episode and act
        for season in seasons:
            if season["IsActive"]:
                if season["Type"] == "episode":
                    # gets the number, startTime and endTime of the current episode
                    episodeStartTime = timegm(time.strptime(season["StartTime"], "%Y-%m-%dT%H:%M:%SZ"))
                    episodeEndTime = timegm(time.strptime(season["EndTime"], "%Y-%m-%dT%H:%M:%SZ"))
                    currentEpisode = int(re.findall("\d", season["Name"])[0])

                elif season["Type"] == "act":
                    # gets the number of the current act
                    currentAct = int(re.findall("\d", season["Name"])[0])
        

        if currentEpisode > 0 and currentAct > 0:

            # if our current act isnt 1, subtract 1 from the current act
            # and get id if the episodes are the same
            for season in seasons:
                if currentAct != 1:
                    if season["Type"] == "act":
                        actStartTime = timegm(time.strptime(season["StartTime"], "%Y-%m-%dT%H:%M:%SZ"))
                        actEndTime = timegm(time.strptime(season["EndTime"], "%Y-%m-%dT%H:%M:%SZ"))
                        
                        if actStartTime >= episodeStartTime and actEndTime <= episodeEndTime:
                            if season["Name"].find(str(currentAct-1)) > 0:
                                lastSeasonID = season["ID"]
                else: 
                    # this means that our current act is 1 and a new episode has started
                    # so we need to subtract 1 from the current episode
                    # and get the id for the 3rd act of the previous episode                    
                    # get episode start and endtime first
                    if season["Type"] == "episode":
                        if season["Name"].find(str(currentEpisode-1)) > 0:
                            episodeStartTime = timegm(time.strptime(season["StartTime"], "%Y-%m-%dT%H:%M:%SZ"))
                            episodeEndTime = timegm(time.strptime(season["EndTime"], "%Y-%m-%dT%H:%M:%SZ"))

            for season in seasons:
                if season["Type"] == "act" and not season["IsActive"]:
                    actStartTime = timegm(time.strptime(season["StartTime"], "%Y-%m-%dT%H:%M:%SZ"))
                    actEndTime = timegm(time.strptime(season["EndTime"], "%Y-%m-%dT%H:%M:%SZ"))                    
                    if season["Name"] == "ACT 3":
                        if actStartTime >= episodeStartTime and actEndTime <= episodeEndTime:
                            lastSeasonID = season["ID"]

            self.log(f"retrieved last season id: {lastSeasonID}")
            return lastSeasonID

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
