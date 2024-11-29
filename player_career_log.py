from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
import pandas as pd
import time
from datetime import datetime
import json
from google.cloud import bigquery
import uuid

def get_player_career_log(player_name, save_files=False, upload_to_bq=False):
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
        seasons = [f"{year}-{str(year+1)[2:]}" for year in range(2000, current_year + 1)]
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
        career_df['TEAM'] = career_df['MATCHUP'].apply(lambda x: x.split()[0])
        career_df['OPPONENT'] = career_df['MATCHUP'].apply(
            lambda x: x.split()[-1] if 'vs' in x else x.split()[-1]
        )

        # Select columns
        career_df = career_df[[
            'SEASON',
            'GAME_DATE', 
            'TEAM',
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

        # Format date and game result
        career_df['GAME_DATE'] = pd.to_datetime(career_df['GAME_DATE'], format='%b %d, %Y').dt.strftime('%Y-%m-%d')
        career_df['WL'] = career_df['WL'].str[0]  # Convert 'W/L' to just 'W' or 'L'
        
        # Sort by date
        career_df = career_df.sort_values('GAME_DATE', ascending=True)

        # Save to CSV and TXT if requested
        if save_files:
            # Save to CSV
            filename = f"{player['full_name'].replace(' ', '_').lower()}_career_gamelog.csv"
            career_df.to_csv(filename, index=False)
            print(f"\nSaved career game log to {filename}")
            
            # Save to TXT
            txt_filename = f"{player['full_name'].replace(' ', '_').lower()}_career_gamelog.txt"
            with open(txt_filename, 'w') as f:
                f.write(f"Career Game Log for {player['full_name']}\n")
                f.write("-" * 50 + "\n")
                f.write(career_df.to_string())
            print(f"Saved career game log to {txt_filename}")

        # Upload to BigQuery only if requested
        if upload_to_bq:
            upload_to_bigquery(player, career_df)

    except Exception as e:
        print(f"Error: {str(e)}")

def load_available_players():
    try:
        with open('available_players.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Players list not found. Please run get_available_players.py first.")
        return None

def upload_to_bigquery(player_dict, career_df):
    try:
        # Initialize BigQuery client
        client = bigquery.Client(project='serene-build')
        
        # Insert player data if not exists
        player_data = {
            'player_id': player_dict['id'],
            'first_name': player_dict['first_name'],
            'last_name': player_dict['last_name']
        }
        
        player_query = f"""
        INSERT INTO `serene-build.nba_player_stats.players` (player_id, first_name, last_name)
        SELECT * FROM UNNEST([(
            {player_data['player_id']},
            '{player_data['first_name']}',
            '{player_data['last_name']}'
        )])
        WHERE NOT EXISTS (
            SELECT 1 FROM `serene-build.nba_player_stats.players`
            WHERE player_id = {player_data['player_id']}
        )
        """
        client.query(player_query)
        
        # Prepare game log data
        career_df['game_log_id'] = [uuid.uuid4().int & (2**63 - 1) for _ in range(len(career_df))]
        career_df['player_id'] = player_dict['id']
        
        # Rename columns to match BigQuery schema
        column_mapping = {
            'SEASON': 'season',
            'GAME_DATE': 'game_date',
            'TEAM': 'team',
            'OPPONENT': 'opponent',
            'WL': 'game_result',
            'MIN': 'minutes',
            'PTS': 'pts',
            'FGM': 'fgm',
            'FGA': 'fga',
            'FG_PCT': 'fg_pct',
            'FG3M': 'fg3m',
            'FG3A': 'fg3a',
            'FG3_PCT': 'fg3_pct',
            'FTM': 'ftm',
            'FTA': 'fta',
            'FT_PCT': 'ft_pct',
            'REB': 'reb',
            'AST': 'ast',
            'STL': 'stl',
            'BLK': 'blk',
            'TOV': 'tov',
            'PF': 'pf'
        }
        career_df = career_df.rename(columns=column_mapping)
        
        # Reorder columns to match BigQuery schema
        columns_order = [
            'game_log_id', 'player_id', 'season', 'game_date', 'team', 
            'opponent', 'game_result', 'minutes', 'pts', 'fgm', 'fga', 
            'fg_pct', 'fg3m', 'fg3a', 'fg3_pct', 'ftm', 'fta', 'ft_pct',
            'reb', 'ast', 'stl', 'blk', 'tov', 'pf'
        ]
        career_df = career_df[columns_order]
        
        # Ensure game_date is datetime type
        career_df['game_date'] = pd.to_datetime(career_df['game_date'])
        
        # Check for existing records and filter
        existing_records_query = f"""
        SELECT DISTINCT game_date, player_id 
        FROM `serene-build.nba_player_stats.game_logs`
        WHERE player_id = {player_dict['id']}
        """
        existing_df = client.query(existing_records_query).to_dataframe()
        
        if not existing_df.empty:
            # Convert existing dates to datetime for comparison
            existing_df['game_date'] = pd.to_datetime(existing_df['game_date'])
            
            # Create merge key using datetime objects
            career_df['merge_key'] = career_df['game_date'].dt.strftime('%Y-%m-%d') + '_' + career_df['player_id'].astype(str)
            existing_df['merge_key'] = existing_df['game_date'].dt.strftime('%Y-%m-%d') + '_' + existing_df['player_id'].astype(str)
            
            # Filter out existing records
            new_records = career_df[~career_df['merge_key'].isin(existing_df['merge_key'])].copy()
            new_records = new_records.drop('merge_key', axis=1)
        else:
            new_records = career_df.copy()

        if len(new_records) == 0:
            print("No new game logs to upload")
            return

        # Ensure integer types are correct
        new_records['game_log_id'] = new_records['game_log_id'].astype('int64')
        new_records['player_id'] = new_records['player_id'].astype('int64')

        # Upload to BigQuery without explicit schema (use table's existing schema)
        table_id = 'serene-build.nba_player_stats.game_logs'
        job_config = bigquery.LoadJobConfig(write_disposition='WRITE_APPEND')
        
        job = client.load_table_from_dataframe(
            new_records, table_id, job_config=job_config
        )
        job.result()
        
        print(f"Successfully uploaded {len(new_records)} new game logs to BigQuery")
        
    except Exception as e:
        print(f"Error uploading to BigQuery: {str(e)}")

def main():
    while True:
        print("\nNBA Player Career Game Log Generator")
        print("-" * 50)
        print("Enter 'quit' to exit")
        
        player_name = input("\nEnter player name: ")
        
        if player_name.lower() == 'quit':
            print("Goodbye!")
            break
            
        # Ask about file generation and BigQuery upload
        save_files = input("Would you like to save CSV and TXT files? (y/n): ").lower().strip() == 'y'
        upload_to_bq = input("Would you like to upload to BigQuery? (y/n): ").lower().strip() == 'y'
            
        get_player_career_log(player_name, save_files, upload_to_bq)
        
        print("\nPress Enter to search for another player or type 'quit' to exit...")
        user_input = input().lower()
        if user_input == 'quit':
            print("Goodbye!")
            break

if __name__ == '__main__':
    main() 