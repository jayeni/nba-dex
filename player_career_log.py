from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
import pandas as pd
import time
from datetime import datetime
import json

def get_player_career_log(player_name):
    try:
        print(f"\nSearching for {player_name}...")
        
        # Find player
        player_dict = players.find_players_by_full_name(player_name)
        
        if not player_dict:
            print(f"Error: Player '{player_name}' not found.")
            return
            
        player = player_dict[0]
        player_id = player['id']
        
        print(f"Fetching career game logs for {player['full_name']}...")

        current_year = datetime.now().year
        seasons = [f"{year}-{str(year+1)[2:]}" for year in range(1946, current_year + 1)]
        all_seasons = []
        games_found = False

        for season in seasons:
            try:
                game_log = playergamelog.PlayerGameLog(
                    player_id=player_id,
                    season=season
                )
                
                df = game_log.get_data_frames()[0]
                
                if len(df) > 0:
                    games_found = True
                    print(f"Found {len(df)} games in {season}")
                    df['SEASON'] = season
                    all_seasons.append(df)
                
                time.sleep(1)
                
            except Exception as e:
                print(f"Error fetching {season}: {str(e)}")
                continue

        if not games_found:
            print("No games found for this player.")
            return

        # Combine all seasons
        career_df = pd.concat(all_seasons, ignore_index=True)

        # Process matchup information
        career_df['HOME_GAME'] = career_df['MATCHUP'].str.contains('vs')
        career_df['TEAM'] = career_df['MATCHUP'].apply(lambda x: x.split()[0])
        career_df['OPPONENT'] = career_df['MATCHUP'].apply(
            lambda x: x.split()[-1] if 'vs' in x else x.split()[-1]
        )

        # Select and rename columns
        career_df = career_df[[
            'SEASON',
            'GAME_DATE', 
            'TEAM',
            'HOME_GAME',
            'OPPONENT',
            'WL',
            'MIN', 
            'PTS',
            'FGM',
            'FGA',
            'FG_PCT',
            'FG3M',
            'FG3A',
            'FG3_PCT',
            'FTM',
            'FTA',
            'FT_PCT',
            'REB',
            'AST',
            'STL',
            'BLK',
            'TOV',
            'PF'
        ]]

        # Rename columns
        career_df.columns = [
            'Season',
            'Date',
            'Team',
            'Home_Game',
            'Opponent',
            'Result',
            'Minutes',
            'Points',
            'FG_Made',
            'FG_Attempts',
            'FG_Percentage',
            '3PT_Made',
            '3PT_Attempts',
            '3PT_Percentage',
            'FT_Made',
            'FT_Attempts',
            'FT_Percentage',
            'Rebounds',
            'Assists',
            'Steals',
            'Blocks',
            'Turnovers',
            'Fouls'
        ]

        # Format date and boolean
        career_df['Date'] = pd.to_datetime(career_df['Date']).dt.strftime('%Y-%m-%d')
        career_df['Home_Game'] = career_df['Home_Game'].map({True: 'Home', False: 'Away'})
        
        # Sort by date
        career_df = career_df.sort_values('Date', ascending=True)

        # Save to CSV
        filename = f"{player['full_name'].replace(' ', '_').lower()}_career_gamelog.csv"
        career_df.to_csv(filename, index=False)
        print(f"\nSaved career game log to {filename}")

        # Print career stats summary
        print("\nCareer Summary:")
        print("-" * 50)
        print(f"Total Games: {len(career_df)}")
        print(f"Seasons Played: {len(career_df['Season'].unique())}")
        print(f"Teams Played For: {', '.join(career_df['Team'].unique())}")
        
        # Home vs Away splits
        print("\nHome/Away Splits:")
        print("-" * 50)
        location_splits = career_df.groupby('Home_Game').agg({
            'Points': 'mean',
            'Assists': 'mean',
            'Rebounds': 'mean',
            'Result': lambda x: (x == 'W').mean() * 100  # Win percentage
        }).round(2)
        print(location_splits)
        
        # Top opponents
        print("\nTop Scoring Averages by Opponent:")
        print("-" * 50)
        opponent_stats = career_df.groupby('Opponent').agg({
            'Points': 'mean',
            'Games': 'size'
        }).sort_values('Points', ascending=False)
        print(opponent_stats.head().round(2))

        # Print highest scoring games
        print("\nTop 5 Scoring Games:")
        print("-" * 50)
        top_games = career_df.nlargest(5, 'Points')[
            ['Date', 'Team', 'Home_Game', 'Opponent', 'Points', 'FG_Made', 'FG_Attempts', '3PT_Made']
        ]
        print(top_games.to_string(index=False))

    except Exception as e:
        print(f"Error: {str(e)}")

def load_available_players():
    try:
        with open('available_players.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Players list not found. Please run get_available_players.py first.")
        return None

def main():
    while True:
        print("\nNBA Player Career Game Log Generator")
        print("-" * 50)
        print("Enter 'quit' to exit")
        
        player_name = input("\nEnter player name: ")
        
        if player_name.lower() == 'quit':
            print("Goodbye!")
            break
            
        get_player_career_log(player_name)
        
        print("\nPress Enter to search for another player or type 'quit' to exit...")
        user_input = input().lower()
        if user_input == 'quit':
            print("Goodbye!")
            break

if __name__ == '__main__':
    main() 