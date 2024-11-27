from nba_api.stats.static import players
import json

def create_players_list():
    try:
        # Get all players from NBA API
        all_players = players.get_players()
        
        # Sort players by full name
        all_players.sort(key=lambda x: x['full_name'])
        
        # Create a formatted string of player names
        player_text = "Available NBA Players:\n"
        player_text += "=" * 50 + "\n\n"
        
        # Add each player's info
        for player in all_players:
            player_text += f"Name: {player['full_name']}\n"
            player_text += f"ID: {player['id']}\n"
            player_text += f"Active: {'Yes' if player['is_active'] else 'No'}\n"
            player_text += "-" * 30 + "\n"
        
        # Save as text file
        with open('available_players.txt', 'w', encoding='utf-8') as f:
            f.write(player_text)
            
        # Also save as JSON for programmatic access
        with open('available_players.json', 'w', encoding='utf-8') as f:
            json.dump(all_players, f, indent=4)
            
        print(f"Successfully created available_players.txt and available_players.json")
        print(f"Total players: {len(all_players)}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    create_players_list() 