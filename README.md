# DownloadTheNBA
DownloadTheNBA is a code repository that scrapes game level of detail statistics for NBA games utilizing BeautifulSoup and Pandas.
Using this repo, a user is able to scrape the web to collect boxscore data for each game in single or multiple specified NBA seasons.
The format of the output is represented by the following schema:

- **Player**: Name of player
- **MP**: Minutes Played
- **FG**: Feild Goals Made
- **FGA**: Feild Goals Attempted
- **FG%**: Feild Goal Percentage
- **3P**: Three Point Feild Goals Made
- **3PA**: Three Point Feild Goals Attempted
- **3P%**: Three Point Feild Goal Percentage
- **FT**: Free Throws Made
- **FTA**: Free Throws Attempted
- **FT%**: Free Throw Percentage
- **ORB**: Offensive Rebounds
- **DRB**: Defensive Rebounds
- **TRB**: Total Rebounds
- **AST**: Assists
- **STL**: Steals
- **BLK**: Blocks
- **TOV**: Turnovers
- **PF**: Personal Fouls
- **PTS**: Points Scored
- **Team**: Player's Team
- **Opposing Team**: Team Player Played Against
- **Home**: Binary. 'Y' if Player's team was Home, else 'N'
- **Date**: Date of game
- **Game Link**: Link to game details on basketball-reference.com
- **OT**: Null if game ended in regulation. OT(N) if over-time was played where 
n = number of over-times
- **PlayerNotes**: Stores special notes on player

I designed this project to scrape the vast amount of game data stored on basketball-reference.com to practice my web-scraping skills,
and to use the data for my own personal analysis. This is an expansion of a [previous project](https://github.com/Meussdorffer/NBA_Stats) I did in late 2016 that scraped per-game
statistics on each player in the NBA. 

## Files:

### functions.py
- **assembleSeasonHTML(*startyear*, *endyear*)**: Designed to generate a list of links to each month in the NBA seasons specified by *startyear* and *endyear*.

- **getGameLinks(*html_string*, *post_2000*=True)**: Returns a table of summarized game data for all games in a given month (defined by *html_string*)

- **getLinkTags(*href*)**: Returns a link to a specific NBA game by parsing the HTML containing a table of games in a given month.

- **scrapeGameData(*data*)**: Returns box score table for both teams in game using a 1 row data frame containing surmized game data as input.

- **cleanMinutes(df)**: Reformats data in Minutes Played column from mm:ss to float. Also creates new column 'Notes' for to log DNPs, Injuries, etc.

### ScrapeSeasons.py

Used to scrape boxscore data for one or more seasons by utilizing the functions described in *functions.py*.
Seasons to gather data from are defined by local variables *start_yr* and *end_yr*. 
If these two variables are equal, a single year will be scraped. These variables take year inputs as full year integers, and refer to the latter
year in a season. 

    e.g. vars start_yr = 2000, end_yr = 2000 will return data for the 1999-00 NBA season
    
