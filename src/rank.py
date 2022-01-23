class Rank:
    def __init__(self, Requests, log):
        self.Requests = Requests
        self.log = log

    def get_peak_rank(self, r, puuid):
        """
            :return [Peak rank, Peak rank season ID]
        """
        self.log(f"getting peak rank for \"{puuid}\"")
        #print(f"getting peak rank for \"{puuid}\"")

        max_rank = 0
        max_rank_season = "UNKNOWN"

        if r is None:
            return [
                max_rank, 
                max_rank_season    
            ]

        try:
            self.log("retrieved rank successfully")
            #print("retrieved rank successfully")

            seasons = r["QueueSkills"]["competitive"].get("SeasonalInfoBySeasonID")

            # loop through all seasons and find highest rank
            if seasons is not None:
                for season in r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"]:
                    if r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][season]["WinsByTier"] is not None:
                        for winByTier in r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][season]["WinsByTier"]:
                            if int(winByTier) > max_rank:
                                max_rank = int(winByTier)
                                max_rank_season = season
        except TypeError as e:
            print("[get_peak_rank] TypeError: ")
            print(e)
        except KeyError as e:
            print("[get_peak_rank] KeyError: ")
            print(e)

        return [
            max_rank, 
            max_rank_season    
        ]


    def get_season_rank(self, r, puuid, seasonID):
        """
            @return [Rank, RR Points, Leaderboard Position]
        """
        self.log(f"getting season rank for \"{puuid}\" for season \"{seasonID}\"")
        print(f"getting season rank for \"{puuid}\" for season \"{seasonID}\"")

        try:
            self.log("retrieved rank successfully")

            seasons = r["QueueSkills"]["competitive"].get("SeasonalInfoBySeasonID")

            if seasons is None:
                rank = [0, 0, 0]
                self.log(f"user \"{puuid}\" has not played competitive yet")
            elif seasonID not in seasons:
                rank = [0, 0, 0]
                self.log(f"user \"{puuid}\" has not played competitive in season \"{seasonID}\" yet")
            else:
                season = seasons[seasonID]

                rankTIER = season["CompetitiveTier"]

                if int(rankTIER) >= 21: # immortal 1
                    rank = [
                            rankTIER,
                            season["RankedRating"],
                            season["LeaderboardRank"], 
                        ]
                elif int(rankTIER) not in (0, 1, 2): # unrated, unrated, unrated
                    rank = [
                            rankTIER,
                            season["RankedRating"],
                            0,
                        ]
                else:
                    rank = [0, 0, 0] 

                #print("rank: ")
                #print(rank)

        except TypeError as e:
            print("[get_season_rank] TypeError: ")
            print(e)
            rank = [0, 0, 0]
        except KeyError as e:
            print("[get_season_rank] KeyError: ")
            print(e)
            rank = [0, 0, 0] 

        return rank

    # fetch player info here
    # and pass the response to the functions
    # and only call this function
    # instead of calling "get_season_rank" multiple times, should help with rate limitation

    def get_rank(self, puuid, seasonID, lastSeasonID):
        """
            [Rank, RR Points, Leaderboard Position, Highest rank, Highest rank season id]
            @return [current season info, last season info, response status]
        """
        response = self.Requests.fetch('pd', f"/mmr/v1/players/{puuid}", "get")

        max_rank = 0
        max_rank_season = "UNKNOWN"
        rank = []
        last_season_rank = []

        if response.ok:
            self.log(f"getting rank for season \"{seasonID}\"")
            #print(f"getting rank for season \"{seasonID}\"")

            r = response.json()

            # returns a tupple
            rank = self.get_season_rank(r, puuid, seasonID)

            # returns a tupple
            peak_rank = self.get_peak_rank(r, puuid)       

            max_rank = peak_rank[0]
            max_rank_season = peak_rank[1]

            last_season_rank = self.get_season_rank(r, puuid, lastSeasonID)

        else:
            self.log(f"failed to get rank information for \"{puuid}\" in season \"{seasonID}\"")
            self.log(response.text)
            rank = [0, 0, 0]

        rank.append(max_rank)
        rank.append(max_rank_season)  

        # rank structure
        # rank[0] = Rank
        # rank[1] = RR Points
        # rank[2] = Leaderboard position
        # rank[3] = Highest rank
        # rank[4] = Highest rank's season

        return [rank, last_season_rank, response.ok]