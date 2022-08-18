import traceback
import urllib3
import os
import json
import time
from prettytable import PrettyTable
from alive_progress import alive_bar

import src.constants as consts
from src.player import Player
from src.requests import Requests
from src.logs import Logging
from src.config import Config
from src.colors import Colors
from src.rank import Rank
from src.content import Content
from src.names import Names
from src.presences import Presences

from src.states.menu import Menu
from src.states.pregame import Pregame
from src.states.coregame import Coregame

from src.table import Table
from src.server import Server

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

os.system('cls')
os.system(f"title VALORANT rank yoinker")

server = ""

def program_exit(status: int):  # so we don't need to import the entire sys module
    log(f"exited program with error code {status}")
    raise SystemExit(status)

def player_loop(state, players, table, tableClass, bar):
    partyCount = 0
    partyIcons = {}

    lastTeamBoolean = False
    lastTeam = "Red"

    for player in players:
        player.update({"seasonID": seasonID})
        player.update({"lastSeasonID": lastSeasonID})

        subject = Player(player, Requests, log, cfg)
        puuid = subject.get_uuid()

        party_icon = ""
    
        if state != "MENUS":
            # set party premade icon
            for party in partyOBJ:
                if puuid in partyOBJ[party]:
                    if party not in partyIcons:
                        partyIcons.update({party: consts.PARTYICONLIST[partyCount]})
                        # PARTY_ICON
                        party_icon = consts.PARTYICONLIST[partyCount]
                        partyCount += 1
                    else:
                        # PARTY_ICON
                        party_icon = partyIcons[party]
        else:
            party_icon = consts.PARTYICONLIST[0]

        player_level = subject.get_account_level()
        player_level_color = colors.level_to_color(player_level)

        name = subject.get_name()
        agent = subject.get_agent()

        currentRank = subject.get_current_rank()
        peakRank = subject.get_peak_rank()
        lastSeasonRank = subject.get_last_season_rank()
                
        peakRankName = peakRank.rank_name
        peakSeason = content.get_name_from_season_id(peakRank.season)

        if peakSeason != None and peakSeason != "UNKNOWN":
            peakRankName = peakRankName + " (%s)" % peakSeason

        leaderboardPosition = currentRank.position

        if state == "PREGAME":
            name = colors.get_color_from_team(pregame_stats['Teams'][0]['TeamID'], name, puuid, Requests.puuid)

            if player["CharacterSelectionState"] == "locked":
                agent = consts.color(str(agent_dict.get(agent.lower())), fore=(255, 255, 255))
            elif player["CharacterSelectionState"] == "selected":
                agent = consts.color(str(agent_dict.get(agent.lower())), fore=(128, 128, 128))
            else:
                agent = consts.color(str(agent_dict.get(agent.lower())), fore=(54, 53, 51))


        elif state == "INGAME":
            name = colors.get_color_from_team(subject.get_team(), name, puuid, Requests.puuid)

            agent = colors.get_agent_from_uuid(agent.lower())

            if lastTeam != subject.get_team():
                if lastTeamBoolean:
                    tableClass.add_row_table(table, ["", "", "", "", "", "", "", "", ""])

            lastTeam = player['TeamID']
            lastTeamBoolean = True
       
        tableClass.add_row_table(table, [party_icon,
                        agent,
                        name,
                        currentRank.rank_name,
                        currentRank.rr_points,
                        lastSeasonRank.rank_name,
                        peakRankName,
                        leaderboardPosition,
                        player_level_color
                        ])
        bar()


try:

    Requests = Requests()

    Logging = Logging()
    log = Logging.log

    cfg = Config(log)

    rank = Rank(Requests, log, cfg)

    content = Content(Requests, log)

    namesClass = Names(Requests, log)

    presences = Presences(Requests, log)

    menu = Menu(Requests, log, presences)
    pregame = Pregame(Requests, log)
    coregame = Coregame(Requests, log)

    Server = Server(Requests)
    Server.start_server()

    agent_dict = content.get_all_agents()

    colors = Colors(agent_dict, consts.agents)

    tableClass = Table()

    log(f"VALORANT rank yoinker")

    cwd = os.getcwd()
    if cfg.dumpDataToFiles:
        if not os.path.exists(f"{cwd}/data"):
            os.makedirs(f"{cwd}/data")
        if not os.path.exists(f"{cwd}/data/players"):
            os.makedirs(f"{cwd}/data/players")

    gameContent = content.get_content()
    seasonID = content.get_current_season_info(gameContent).get("ID")
    lastSeasonID = content.get_last_season_id(gameContent)
    lastSeasonName = content.get_name_from_season_id(lastSeasonID)
    currentSeasonName = content.get_name_from_season_id(seasonID)
    lastGameState = ""

    if cfg.dumpDataToFiles:
        with open("data/content.json", "w") as f:
            f.write(json.dumps(gameContent))
            f.close()
        with open("data/agents.json", "w") as f:
            f.write(json.dumps(agent_dict))
            f.close()
        with open("data/seasons.json", "w") as f:
            f.write(json.dumps(content.Seasons))
            f.close()

    while True:
        table = PrettyTable()

        try:
            presence = presences.get_presence()
            game_state = presences.get_game_state(presence)
        except TypeError:
            raise Exception("Game has not started yet!")

        if cfg.cooldown == 0 or game_state != lastGameState:

            if not cfg.keepPlayerFiles:
                log("Clearing players folder")
                for f in os.listdir(f"{cwd}/data/players/"):
                    if os.path.isfile(f"{cwd}/data/players/{f}"):
                        os.remove(f"{cwd}/data/players/{f}")

            log(f"getting new {game_state} scoreboard")

            lastGameState = game_state

            game_state_dict = {
                "INGAME": consts.color('In-Game', fore=(241, 39, 39)),
                "PREGAME": consts.color('Agent Select', fore=(103, 237, 76)),
                "MENUS": consts.color('In-Menus', fore=(238, 241, 54)),
            }

            if game_state == "INGAME":

                coregame_stats = coregame.get_coregame_stats()

                Players = coregame_stats["Players"]

                server = consts.GAMEPODS[coregame_stats["GamePodID"]]

                presences.wait_for_presence(namesClass.get_players_puuid(Players))
                
                names = namesClass.get_names_from_puuids(Players)

                with alive_bar(total=len(Players), title='Fetching Players', bar='classic2') as bar:
                    presence = presences.get_presence()
                    partyOBJ = menu.get_party_json(namesClass.get_players_puuid(Players), presence)

                    log(f"retrieved names dict: {names}")

                    Players.sort(key=lambda Players: Players["PlayerIdentity"].get("AccountLevel"), reverse=True)
                    Players.sort(key=lambda Players: Players["TeamID"], reverse=True)

                    player_loop(game_state, Players, table, tableClass, bar)

            elif game_state == "PREGAME":

                pregame_stats = pregame.get_pregame_stats()

                server = consts.GAMEPODS[pregame_stats["GamePodID"]]

                Players = pregame_stats["AllyTeam"]["Players"]

                presences.wait_for_presence(namesClass.get_players_puuid(Players))

                names = namesClass.get_names_from_puuids(Players)

                with alive_bar(total=len(Players), title='Fetching Players', bar='classic2') as bar:

                    presence = presences.get_presence()
                    partyOBJ = menu.get_party_json(namesClass.get_players_puuid(Players), presence)

                    log(f"retrieved names dict: {names}")

                    Players.sort(key=lambda Players: Players["PlayerIdentity"].get("AccountLevel"), reverse=True)

                    player_loop(game_state, Players, table, tableClass, bar)

            if game_state == "MENUS":

                Players = menu.get_party_members(Requests.puuid, presence)
                names = namesClass.get_names_from_puuids(Players)

                with alive_bar(total=len(Players), title='Fetching Players', bar='classic2') as bar:

                    log(f"retrieved names dict: {names}")

                    Players.sort(key=lambda Players: Players["PlayerIdentity"].get("AccountLevel"), reverse=True)

                    player_loop(game_state, Players, table, tableClass, bar)
            
            if (title := game_state_dict.get(game_state)) is None:
                time.sleep(10)

            if server != "":
                table.title = f"Valorant status: {title} - {server} - {currentSeasonName}"
            else:
                table.title = f"Valorant status: {title} - {currentSeasonName}"

            server = ""
            table.field_names = ["Party", "Agent", "Name", "Rank", "RR", "Last Season Rank (" + lastSeasonName + ")", "Peak Rank", "pos.", "Level"]
            if title is not None:
                print(table)
                print(f"VALORANT rank yoinker")

        if cfg.cooldown == 0:
            input("Press enter to fetch again...")
        else:
            time.sleep(cfg.cooldown)
except:
    print(consts.color(
        "The program has encountered an error. If the problem persists, please reach support"
        f" with the logs found in {cwd}\logs", fore=(255, 0, 0)))
    traceback.print_exc()
    input("press enter to exit...\n")
    os._exit(1)
