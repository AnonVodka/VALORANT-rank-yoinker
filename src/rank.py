from dataclasses import dataclass
import src.constants as consts
import json 

@dataclass
class rank_data:
    rank: int = 0
    rank_name: str = consts.ranks.get(0)

@dataclass
class peak_rank(rank_data):
    season: str = "UNKNOWN"

@dataclass
class season_rank(rank_data):
    rr_points: int = 0
    position: int = 0

@dataclass
class rank_info:
    current: season_rank = season_rank(rank = 0, rr_points = 0, position = 0, rank_name="UNKNOWN")
    peak: peak_rank = peak_rank(rank = 0, season = "UNKNOWN", rank_name="UNKNOWN")
    last_season: season_rank = season_rank( rank = 0, rr_points = 0, position = 0, rank_name="UNKNOWN")

class Rank:
    def __init__(self, Requests, log, cfg=None):
        self.Requests = Requests
        self.log = log
        self.Cfg = cfg

    def get_peak_rank(self, r: dict, puuid: str) -> peak_rank:
        """gets the peak rank for the given player uuid

        Args:
            r (dict): response from the api
            puuid (str): player uuid

        Returns:
            peak_rank: peak rank, peak rank name, season id
        """
        
        self.log(f"getting peak rank for \"{puuid}\"")

        peak = peak_rank()

        if r is None:
            return peak

        try:
            self.log("retrieved rank successfully")

            seasons = r["QueueSkills"]["competitive"].get("SeasonalInfoBySeasonID")

            # loop through all seasons and find highest rank
            if seasons is not None:
                for season in r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"]:
                    if r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][season]["WinsByTier"] is not None:
                        for winByTier in r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][season]["WinsByTier"]:
                            if int(winByTier) > peak.rank:
                                peak.rank = int(winByTier)
                                peak.season = season
                                peak.rank_name = consts.ranks.get(peak.rank)

        except TypeError as e:
            print("[get_peak_rank] TypeError: ")
            print(e)
        except KeyError as e:
            print("[get_peak_rank] KeyError: ")
            print(e)

        return peak

    def get_season_rank(self, r: dict, puuid: str, seasonID: str) -> season_rank:
        """gets the season rank for the given player uuid and season id

        Args:
            r (dict): response from the api
            puuid (str): player uuid
            seasonID (str): season uuid

        Returns:
            season_rank: rank, rank name, rr points, leaderboard position
        """              
        self.log(f"getting season rank for \"{puuid}\" for season \"{seasonID}\"")

        rank = season_rank()

        try:
            self.log("retrieved rank successfully")

            seasons = r["QueueSkills"]["competitive"].get("SeasonalInfoBySeasonID")

            if seasons is None:
                self.log(f"user \"{puuid}\" has not played competitive yet")
            elif seasonID not in seasons:
                self.log(f"user \"{puuid}\" has not played competitive in season \"{seasonID}\" yet")
            else:
                season = seasons[seasonID]

                rank.rank = season["CompetitiveTier"]
                rank.rank_name = consts.ranks.get(rank.rank)
                rank.rr_points = season["RankedRating"]

                if int(rank.rank) >= 24: # immortal 1
                    rank.position = season["LeaderboardRank"]

        except TypeError as e:
            print("[get_season_rank] TypeError: ")
            print(e)
        except KeyError as e:
            print("[get_season_rank] KeyError: ")
            print(e)

        return rank

    def get_rank(self, puuid: str, seasonID: str, lastSeasonID: str, name: str = None) -> rank_info:
        """gets the full rank info for the given player uuid and season uuid

        Args:
            puuid (str): player uuid
            seasonID (str): current season uuid
            lastSeasonID (str): last seasn uuid
            name (str, optional): player name for logging purposes. Defaults to None.

        Returns:
            rank_info: season_rank, peak_rank, last_season_rank
        """
               
        response = self.Requests.fetch('pd', f"/mmr/v1/players/{puuid}", "get")

        info = rank_info()

        if response.ok:
            self.log(f"getting rank for season \"{seasonID}\"")

            r = response.json()

            if self.Cfg is not None and self.Cfg.dumpDataToFiles:
                with open(f"data/players/{name if name is not None else puuid}.json", "w") as f:
                    f.write(json.dumps(r))
                    f.close()

            info.current = self.get_season_rank(r, puuid, seasonID)

            info.peak = self.get_peak_rank(r, puuid)   
            
            self.log(f"getting rank for last season \"{lastSeasonID}\"")
            info.last_season = self.get_season_rank(r, puuid, lastSeasonID)

        else:
            self.log(f"failed to get rank information for \"{puuid}\" in season \"{seasonID}\"")
            self.log(response.text)

        return info