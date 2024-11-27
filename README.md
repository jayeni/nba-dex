# NBA Dex 🏀

NBA Dex is a Python application that fetches NBA player career statistics and exports them to CSV format, making it easy to analyze data in business intelligence tools like Looker Studio, Power BI, Tableau, and others.

## Features

- Fetch complete career statistics for any NBA player.
- Export data to CSV format for easy integration with BI tools.
- Compatible with major BI tools such as Looker Studio, Power BI, Tableau, and Excel.
- Includes active and historical NBA players.
- Generate a comprehensive player directory for reference and analysis.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- NBA API key (e.g., from [NBA Stats API](https://github.com/swar/nba_api) or another data source)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/nba-dex.git
cd nba-dex
```

### 2. Set up Python environment

#### Windows

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate

# Verify Python version
python --version  # Should be 3.8 or higher
```

#### macOS/Linux

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Verify Python version
python3 --version  # Should be 3.8 or higher
```

### 3. Install dependencies

```bash
# Upgrade pip to latest version
python -m pip install --upgrade pip

# Install required packages
pip install -r requirements.txt
```

## Running the Application

### 1. Basic Usage

```bash
# Make sure your virtual environment is activated
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

# First, generate the players list
python get_available_players.py

# Then run the main application
python player_career_log.py
```

### 2. Interactive Mode

When running `player_career_log.py`, follow these steps:

1. Enter player name when prompted

   ```bash
   Enter player name: LeBron James
   ```

2. Wait for data processing

   ```bash
   Fetching data for LeBron James...
   Processing career statistics...
   ```

3. Check output directory for CSV file
   ```bash
   # File will be named: lebron_james_career_log.csv
   ```

### 3. Command Line Options

```bash
# Specify output directory
python player_career_log.py --output ./data

# Get data for specific seasons
python player_career_log.py --player "LeBron James" --seasons 2020-2023

# Export in different format
python player_career_log.py --format json

# Get help
python player_career_log.py --help
```

### 4. Batch Processing

Create a text file (`players.txt`) with player names:

```text
LeBron James
Stephen Curry
Kevin Durant
```

Then run:

```bash
python player_career_log.py --batch players.txt
```

### 5. Error Handling

If you encounter errors:

1. Player not found

   ```bash
   # Try using partial name
   Enter player name: Curry
   # System will show matching players
   ```

2. Rate limiting

   ```bash
   # Wait 60 seconds and try again
   # Or use the --delay option
   python player_career_log.py --delay 2
   ```

3. Connection issues
   ```bash
   # Check your internet connection
   # Try again with --retry option
   python player_career_log.py --retry 3
   ```

### 6. Output Format

The generated CSV will include:

```csv
Season,Team,Games,GamesStarted,MinutesPlayed,...
2003-04,CLE,79,79,3122,...
2004-05,CLE,80,80,3388,...
```

### 7. Monitoring Progress

1. Check the terminal for progress messages
2. Look for success confirmation:
   ```bash
   ✅ Data successfully exported to: lebron_james_career_log.csv
   ```

### 8. Cleaning Up

```bash
# Deactivate virtual environment when done
deactivate

# Remove generated files (optional)
rm *.csv
rm available_players.txt
```

### 9. Tips for Best Results

- Keep the virtual environment activated while running scripts
- Use full player names for best matches
- Check `available_players.txt` for correct player names
- Wait a few seconds between requests for different players
- Keep your Python packages updated
