import requests
import urllib3
import os
import base64
import json
import time
from prettytable import PrettyTable

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    with open("config.json", "r") as file:
        config = json.load(file)
        enableColors = config.get("enableColors")
except FileNotFoundError:
    with open("config.json", "w+") as file:
        enableColors = bool(input("Disable colors? (1 for yes, 0 for no): "))
        json.dump({"enableColors": enableColors}, file)

if enableColors:
    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    BROWN = "\033[0;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    LIGHT_GRAY = "\033[0;37m"
    DARK_GRAY = "\033[1;30m"
    LIGHT_RED = "\033[1;31m"
    LIGHT_GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    LIGHT_BLUE = "\033[1;34m"
    LIGHT_PURPLE = "\033[1;35m"
    LIGHT_CYAN = "\033[1;36m"
    LIGHT_WHITE = "\033[1;37m"
    BOLD = "\033[1m"
    FAINT = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    NEGATIVE = "\033[7m"
    CROSSED = "\033[9m"
    end_tag = "\033[0m"
else:
    BLACK = RED = GREEN = BROWN = BLUE = PURPLE = CYAN = LIGHT_GRAY = DARK_GRAY = LIGHT_RED = LIGHT_GREEN = YELLOW = ''
    LIGHT_BLUE = LIGHT_PURPLE = LIGHT_CYAN = LIGHT_WHITE = BOLD = FAINT = ITALIC = UNDERLINE = ''
    BLINK = NEGATIVE = CROSSED = end_tag = ''

number_to_ranks = {
    0: LIGHT_GRAY + "Unrated" + end_tag,
    1: LIGHT_GRAY + "Unrated" + end_tag,
    2: LIGHT_GRAY + "Unrated" + end_tag,
    3: LIGHT_GRAY + "Iron 1" + end_tag,
    4: LIGHT_GRAY + "Iron 2" + end_tag,
    5: LIGHT_GRAY + "Iron 3" + end_tag,
    6: BROWN + "Bronze 1" + end_tag,
    7: BROWN + "Bronze 2" + end_tag,
    8: BROWN + "Bronze 3" + end_tag,
    9: LIGHT_WHITE + "Silver 1" + end_tag,
    10: LIGHT_WHITE + "Silver 2" + end_tag,
    11: LIGHT_WHITE + "Silver 3" + end_tag,
    12: BOLD + YELLOW + "Gold 1" + end_tag,
    13: BOLD + YELLOW + "Gold 2" + end_tag,
    14: BOLD + YELLOW + "Gold 3" + end_tag,
    15: LIGHT_CYAN + "Platinum 1" + end_tag,
    16: LIGHT_CYAN + "Platinum 2" + end_tag,
    17: LIGHT_CYAN + "Platinum 3" + end_tag,
    18: LIGHT_PURPLE + "Diamond 1" + end_tag,
    19: LIGHT_PURPLE + "Diamond 2" + end_tag,
    20: LIGHT_PURPLE + "Diamond 3" + end_tag,
    21: LIGHT_RED + "Immortal" + end_tag,
    22: LIGHT_RED + "Immortal 2" + end_tag,
    23: LIGHT_RED + "Immortal 3" + end_tag,
    24: BOLD + "Radiant" + end_tag
}

headers = {}


def get_region():
    path = os.path.join(os.getenv('LOCALAPPDATA'), R'VALORANT\Saved\Logs\ShooterGame.log')
    with open(path, "r", encoding="utf8") as file:
        while True:
            line = file.readline()
            if '.a.pvp.net/account-xp/v1/' in line:
                pd_url = line.split('.a.pvp.net/account-xp/v1/')[0].split('.')[-1]
            elif 'https://glz' in line:
                glz_url = []
                glz_url.append(line.split('https://glz-')[1].split(".")[0])
                glz_url.append(line.split('https://glz-')[1].split(".")[1])
            if "pd_url" in locals() and "glz_url" in locals():
                return[pd_url, glz_url]


region = get_region()
pd_url = f"https://pd.{region[0]}.a.pvp.net"
glz_url = f"https://glz-{region[1][0]}.{region[1][1]}.a.pvp.net"
region = region[0]



def get_current_version():
    # version = f"{data['branch']}-shipping-{data['buildVersion']}-{data['version'].split('.')[3]}"
    # release-03.02-shipping-9-587972
    path = os.path.join(os.getenv('LOCALAPPDATA'), R'VALORANT\Saved\Logs\ShooterGame.log')
    with open(path, "r", encoding="utf8") as file:
        while True:
            line = file.readline()
            if 'CI server version:' in line:
                version_without_shipping = line.split('CI server version: ')[1].strip()
                version = version_without_shipping.split("-")
                version.insert(2, "shipping")
                return "-".join(version)
                # return version


def fetch(url_type, endpoint, method):
    global response
    try:
        if url_type == "glz":
            response = requests.request(method, glz_url + endpoint, headers=get_headers(), verify=False)
            return response.json()
        elif url_type == "pd":
            response = requests.request(method, pd_url + endpoint, headers=get_headers(), verify=False)
            return response.json()
        elif url_type == "local":
            local_headers = {}
            local_headers['Authorization'] = 'Basic ' + base64.b64encode(
                ('riot:' + lockfile['password']).encode()).decode()
            response = requests.request(method, f"https://127.0.0.1:{lockfile['port']}{endpoint}",
                                        headers=local_headers,
                                        verify=False)
            return response.json()
        elif url_type == "custom":
            response = requests.request(method, f"{endpoint}", headers=get_headers(),
                                        verify=False)
            return response.json()
    except json.decoder.JSONDecodeError:
        print(response)
        print(response.text)


def get_lockfile():
    try:
        with open(os.path.join(os.getenv('LOCALAPPDATA'), R'Riot Games\Riot Client\Config\lockfile')) as lockfile:
            data = lockfile.read().split(':')
            keys = ['name', 'PID', 'port', 'password', 'protocol']
            return dict(zip(keys, data))
    except:
        raise Exception("Lockfile not found, you're not in a game!")


lockfile = get_lockfile()

puuid = ''


def get_headers():
    global headers
    if headers == {}:
        global puuid
        local_headers = {}
        local_headers['Authorization'] = 'Basic ' + base64.b64encode(
            ('riot:' + lockfile['password']).encode()).decode()
        response = requests.get(f"https://127.0.0.1:{lockfile['port']}/entitlements/v1/token", headers=local_headers,
                                verify=False)
        entitlements = response.json()
        puuid = entitlements['subject']
        headers = {
            'Authorization': f"Bearer {entitlements['accessToken']}",
            'X-Riot-Entitlements-JWT': entitlements['token'],
            'X-Riot-ClientPlatform': "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Z"
                                     "m9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0I"
                                     "jogIlVua25vd24iDQp9",
            'X-Riot-ClientVersion': get_current_version()
        }
    return headers


def get_puuid():
    return puuid


def get_coregame_match_id():
    global response
    try:
        response = fetch(url_type="glz", endpoint=f"/core-game/v1/players/{get_puuid()}", method="get")
        match_id = response['MatchID']
        return match_id
    except KeyError:
        print(f"No match id found. {response}")
        return 0
    except TypeError:
        print(f"No match id found. {response}")
        return 0


def get_pregame_match_id():
    try:
        response = fetch(url_type="glz", endpoint=f"/pregame/v1/players/{get_puuid()}", method="get")
        match_id = response['MatchID']
        return match_id
    except KeyError:
        print(f"No match id found. {response}")
        return 0
    except TypeError:
        print(f"No match id found. {response}")
        return 0


def get_coregame_stats():
    response = fetch("glz", f"/core-game/v1/matches/{get_coregame_match_id()}", "get")
    return response


def get_pregame_stats():
    response = fetch("glz", f"/pregame/v1/matches/{get_pregame_match_id()}", "get")
    return response


def getRank(puuid, seasonID):
    response = fetch('pd', f"/mmr/v1/players/{puuid}", "get")
    try:
        rankTIER = response["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][seasonID]["CompetitiveTier"]
        if int(rankTIER) >= 21:
            rank = [rankTIER,
                    response["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][seasonID]["RankedRating"],
                    response["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][seasonID]["LeaderboardRank"]]
        elif int(rankTIER) not in (0, 1, 2, 3):
            rank = [rankTIER,
                    response["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][seasonID]["RankedRating"],
                    0]
        else:
            rank = [0, 0, 0]
    except TypeError:
        rank = [0, 0, 0]
    except KeyError:
        rank = [0, 0, 0]
    return rank


def get_name_from_puuid(puuid):
    response = requests.put(pd_url + f"/name-service/v2/players", headers=get_headers(), json=[puuid], verify=False)
    return response.json()[0]["GameName"] + "#" + response.json()[0]["TagLine"]

def get_multiple_names_from_puuid(puuids):
    response = requests.put(pd_url + "/name-service/v2/players", headers=get_headers(), json=puuids,
                            verify=False)
    name_dict = {}
    for player in response.json():
        name_dict.update({player["Subject"]: player["GameName"] + "#" + player["TagLine"]})
    return name_dict


def get_content():
    content = fetch("custom", f"https://shared.{region}.a.pvp.net/content-service/v2/content", "get")
    return content


def get_latest_season_id(content=get_content()):
    for season in content["Seasons"]:
        if season["IsActive"]:
            return season["ID"]


def get_all_agents(content=get_content()):
    agent_dict = {}
    for agent in content["Characters"]:
        if "NPE" not in agent["AssetName"]:
            agent_dict.update({agent['ID'].lower(): agent['Name']})
    return agent_dict


def presence(puuid):
    presences = fetch(url_type="local", endpoint="/chat/v4/presences", method="get")
    for presence in presences['presences']:
        if presence['puuid'] == puuid:
            return json.loads(base64.b64decode(presence['private']))


def level_to_color(level):
    PLcolor = ''
    if level >= 400:
        PLcolor = CYAN  # PL = Player Level
        pass
    elif level >= 300:
        PLcolor = YELLOW
        pass
    elif level >= 200:
        PLcolor = BLUE
        pass
    elif level >= 100:
        PLcolor = BROWN
        pass
    elif level < 100:
        PLcolor = LIGHT_GRAY
    return PLcolor

def get_names_from_puuids(players):
    players_puuid = []
    for player in players:
        players_puuid.append(player["Subject"])
    return get_multiple_names_from_puuid(players_puuid)

def get_color_from_team(team):
    if team == 'Red':
        color = LIGHT_RED
    elif team == 'Blue':
        color = LIGHT_BLUE
    else:
        color = ''
    return color

content = get_content()
agent_dict = get_all_agents(content)
seasonID = get_latest_season_id(content)
table = PrettyTable()
# current in-game status
game_state = presence(get_puuid())["sessionLoopState"]
game_state_dict = {
    "INGAME": LIGHT_RED + "In-Game" + end_tag,
    "PREGAME": LIGHT_GREEN + "Agent Select" + end_tag,
    "MENUS": BOLD + YELLOW + "In-Menus" + end_tag
}
table.title = f"Valorant status: {game_state_dict[game_state]}"
table.field_names = ["Agent", "Name", "Rank", "RR", "Leaderboard Position", "Level"]
if game_state == "INGAME":
    Players = get_coregame_stats()["Players"]
    names = get_names_from_puuids(Players)
    for player in Players:
        rank = getRank(player["Subject"], seasonID)
        player_level = player["PlayerIdentity"].get("AccountLevel")
        color = get_color_from_team(player['TeamID'])

        PLcolor = level_to_color(player_level)

        table.add_rows([[BOLD + agent_dict.get(player["CharacterID"].lower()) + end_tag,
                         color + names[player["Subject"]] + end_tag,
                         number_to_ranks[rank[0]],
                         rank[1],
                         rank[2],
                         PLcolor + str(player_level) + end_tag
                         ]])
        time.sleep(0.5)
elif game_state == "PREGAME":
    pregame_stats = get_pregame_stats()
    Players = pregame_stats["AllyTeam"]["Players"]
    names = get_names_from_puuids(Players)
    for player in Players:
        rank = getRank(player["Subject"], seasonID)
        player_level = player["PlayerIdentity"].get("AccountLevel")
        color = get_color_from_team(pregame_stats["AllyTeam"]['TeamID'])

        PLcolor = level_to_color(player_level)

        if player["CharacterSelectionState"] == "locked":
            agent_color = BOLD
        else:
            agent_color = LIGHT_GRAY
        table.add_rows([[agent_color + str(agent_dict.get(player["CharacterID"].lower())) + end_tag,
                         color + names[player["Subject"]] + end_tag,
                         number_to_ranks[rank[0]],
                         rank[1],
                         rank[2],
                         PLcolor + str(player_level) + end_tag
                         ]])
        time.sleep(0.5)

print(table)
input("Press enter to exit...")
