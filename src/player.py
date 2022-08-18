import time
import src.rank as Rank
from src.requests import Requests
from src.logs import Logging
from src.config import Config
from src.names import Names



class Player:

    seasonID: str
    lastSeasonID: str
    playerData: str
    uuid: str
    name: str
    rank: Rank.rank_info

    def __init__(self, playerData: str, Requests: Requests, log: Logging.log, cfg: Config = None):
        self.Requests = Requests
        self.Rank = Rank.Rank(Requests, log, cfg)
        self.Names = Names(Requests, log)
        self.log = log
        self.Cfg = cfg


        self.seasonID = playerData["seasonID"]
        self.lastSeasonID = playerData["lastSeasonID"]

        self.playerData = playerData

        self.uuid = playerData["Subject"]
        self.name = self.Names.get_name_from_puuid(self.uuid)

        self.rank = self.Rank.get_rank(self.uuid, self.seasonID, self.lastSeasonID, self.name)

    def get_uuid(self) -> str:
        return self.uuid

    def get_name(self) -> str:
        return self.name

    def get_rank(self) -> Rank.rank_info:
        return self.rank

    def get_current_rank(self) -> Rank.season_rank:
        return self.rank.current

    def get_peak_rank(self) -> Rank.peak_rank:
        return self.rank.peak

    def get_last_season_rank(self) -> Rank.season_rank:
        return self.rank.last_season

    def get_account_level(self) -> int:
        return self.playerData["PlayerIdentity"].get("AccountLevel")

    def get_agent(self) -> str:
        return self.playerData.get("CharacterID", None)
    
    def get_team(self) -> str:
        return self.playerData.get("TeamID", None)

    def __str__(self) -> str:
        return (
            f"name: {self.name}\n"
            f"uuid: {self.uuid}\n"
            f"level: {self.get_account_level()}\n"
            f"rank: {self.rank}"
        )
