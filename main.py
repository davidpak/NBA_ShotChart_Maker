# Import Packages
from nba_api.stats.endpoints import shotchartdetail
from nba_api.stats.endpoints import commonplayerinfo
import json
import requests
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

# Load teams file
teams = json.loads(requests.get('https://raw.githubusercontent.com/bttmly/nba/master/data/teams.json').text)
# Load players file
players = json.loads(requests.get('https://raw.githubusercontent.com/bttmly/nba/master/data/players.json').text)


# Get team ID from the team name, returns -1 if team cannot be found
def get_team_id(team_name):
    for team in teams:
        if team['teamName'] == team_name:
            return team['teamId']
    return -1


# Get player ID based on player name, returns -1 if player cannot be found
def get_player_id(player_name):
    name_parts = player_name.split()
    first = name_parts[0]
    last = ' '.join(name_parts[1:])

    for player in players:
        if player['firstName'] == first and player['lastName'] == last:
            return player['playerId']
    print(f"{player_name} not found")
    return -1


# Get the team name of the given player
def get_player_team(player_name):
    player_id = get_player_id(player_name)

    player_info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
    player_info = player_info.get_data_frames()[0]

    # Find the current team name
    city_name = player_info['TEAM_CITY'].values[0]
    team_name = player_info['TEAM_NAME'].values[0]

    current_team = city_name + " " + team_name

    return current_team


# Collects shot data for a specific player during a specific season formatted: "20XY-XY+1"
def collect_shot_data(player_name, season):
    team_name = get_player_team(player_name)
    # Create json request
    shot_json = shotchartdetail.ShotChartDetail(
        team_id=get_team_id(team_name),
        player_id=get_player_id(player_name),
        context_measure_simple='PTS',
        season_nullable=season,
        season_type_all_star='Regular Season'
    )

    # Get the data from the API response
    response = shot_json.get_dict()

    if response['resultSets']:
        # Extract headers and rows
        headers = response['resultSets'][0]['headers']
        rows = response['resultSets'][0]['rowSet']

        # Create a DataFrame
        player_data = pd.DataFrame(rows, columns=headers)

        # Select specific columns
        selected_columns = ['SHOT_TYPE', 'SHOT_ZONE_AREA', 'SHOT_ZONE_RANGE',
                            'SHOT_DISTANCE']

        # Print the DataFrame with selected columns
        print(player_data[selected_columns][:20])
        return player_data
    else:
        print("No shot data found for the player.")
        return -1


# Draw basketball court
def create_court(ax, color):
    # Short corner 3PT Lines
    ax.plot([-220, -220], [0, 140], linewidth=2, color=color)
    ax.plot([220, 220], [0, 140], linewidth=2, color=color)

    # 3PT arc
    ax.add_artist(mpl.patches.Arc((0, 140), 440, 315, theta1=0, theta2=180, facecolor='none', edgecolor=color, lw=2))

    # Lane and Key
    ax.plot([-80, -80], [0, 190], linewidth=2, color=color)
    ax.plot([80, 80], [0, 190], linewidth=2, color=color)
    ax.plot([-60, -60], [0, 190], linewidth=2, color=color)
    ax.plot([60, 60], [0, 190], linewidth=2, color=color)
    ax.plot([-80, 80], [190, 190], linewidth=2, color=color)
    ax.add_artist(mpl.patches.Circle((0, 190), 60, facecolor='none', edgecolor=color, lw=2))

    # Rim
    ax.add_artist(mpl.patches.Circle((0, 60), 15, facecolor='none', edgecolor=color, lw=2))

    # Backboard
    ax.plot([-30, 30], [40, 40], linewidth=2, color=color)

    # Remove ticks
    ax.set_xticks([])
    ax.set_yticks([])

    # Set axis limits
    ax.set_xlim(-250, 250)
    ax.set_ylim(0, 470)

    return ax


def main():
    player_name = input("Which player's shot chart do you want?")
    season = input("From which season? (Ex: 2015-16)")

    player_data = collect_shot_data(player_name, season)
    # General plot parameters
    mpl.rcParams['font.family'] = 'Sans-serif'
    mpl.rcParams['font.size'] = 18
    mpl.rcParams['axes.linewidth'] = 2
    # Draw basketball court
    fig = plt.figure(figsize=(4, 3.76))
    ax = fig.add_axes([0, 0, 1, 1])
    # Plot hexbin of shots with logarithmic binning
    ax.hexbin(player_data['LOC_X'], player_data['LOC_Y'] + 60, gridsize=(30, 30), extent=(-300, 300, 0, 940),
              bins='log',
              cmap='Blues')
    # Annotate player name and season
    ax = create_court(ax, 'black')
    plt.show()


if __name__ == '__main__':
    main()