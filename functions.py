import pandas as pd
from bs4 import BeautifulSoup
import requests
import datetime


def assembleSeasonHTML(startyear, endyear):
    '''
    Returns a list of HTML links for each month in a season to be scraped
    startyear and endyear refer to a single season, or a range of seasons. For example:
        (2000, 2000) = Single 1999-00 NBA Season
        (2000, 2001) = Both 1999-00 and 2000-01 NBA Seasons
        (2000, 2002) = 1999-00 NBA Season, 2000-01 NBA Season, and 2001-02 NBA Season
    Due to above, links reference games beginning in Oct. of startyear, and ending in games in Jun. of endyear
    '''

    # Defining each piece of the combined html string
    base = 'http://www.basketball-reference.com/leagues/'

    # Allows single-year query if a range of years isn't specified
    if startyear != endyear:
        years = range(startyear, endyear + 1)  # will pull all links from this daterange
    else:
        years = [startyear]

    # Assembling html strings
    months = [10,11,12,1,2,3,4,5,6] # Months that can contain scheduled NBA games

    links = {}
    for year in years:
        for month in months:
            links[(year, month)] = (base + 'NBA_' + str(year) + '_games-' +
                         datetime.date(1900, month, 1).strftime('%B').lower() + '.html')

    return links


def getLinkTags(href):
    '''
    Input is a single <a href> tag
    Returns a link to a single game's box score
    Used in getGameLinks to return URLs used in scrapeGameData
    '''

    if "Box Score" in str(href):  # All tags we need contain 'Box Score'
        link = str(href).split()[1]
        link = link[6:len(link) - 5]  # Link exists between tags
        return (link)
    else:
        # invalid link
        return None


def getGameLinks(html_string, post_2000=True):
    '''
    Returns a data frame containing home team, away team, points, OTs,
    and link to boxscores for all games played within a month of an NBA season
    post_2000 exists for seasons that track time of game start, which occur 2001 onward
    '''

    # Request page, get table
    url = requests.get(html_string)
    print("Scraping page link " + str(html_string))

    soup = BeautifulSoup(url.content, "html.parser")
    link_tags = soup.find_all('a')  # Contains embedded links
    table_tags = soup.find_all('table')  # Contains Home / Away / OT / Points
    table_tags = str(table_tags)

    # Holds Home / Away / OT / Points info
    game_info = pd.DataFrame(pd.read_html(table_tags)[0])

    # Removing Regular Season / Playoff record delimiter present in playoff months
    game_info = game_info[game_info.Date.str.contains("Playoffs") == False]

    # Generating a list of box score links
    base_link = 'https://www.basketball-reference.com'
    box_score_links = []

    for tag in link_tags:
        box_link = getLinkTags(tag)

        if box_link is not None:
            # Valid link, add to list
            box_score_links.append(base_link + box_link)
        else:
            # Link is invalid
            continue

    game_info['Box Score Links'] = box_score_links

    # Drop time of game start column
    if post_2000:
        game_info.drop(game_info.columns[1], axis =1, inplace=True)

    cols = ['Date', 'Away Team', 'Away Points', 'Home Team', 'Home Points', 'nan1', 'OT',
            'nan2', 'BoxScore']
    game_info.columns = cols
    game_info = game_info.drop(game_info.columns[[5, 7]], axis=1) # Drop null columns
    game_info.fillna('none')

    return game_info


def scrapeGameData(data):
    '''
    Input: 1 row dataframe contianing the following game data:
        Home Team
        Away Team
        Date
        OT
        BoxScore link
    Returns box score table for both teams in game
    '''

    print('Scraping data for game ' + data['Away Team'] + ' at ' + data['Home Team'] + ' on ' + data['Date'])

    try:
        tbl_data = pd.read_html(data['BoxScore'], header= 1)
    except ValueError:
        print('No tables found for {}'.format(data['BoxScore']))
        return None
    
    # Box score data lies in tables [0], [2] for away, home team
    if len(tbl_data) > 2:
        awy_data = pd.DataFrame(tbl_data[0])
        hm_data = pd.DataFrame(tbl_data[2])
    elif len(tbl_data) == 2:
        # Many older games do not have advanced stat tables
        awy_data = pd.DataFrame(tbl_data[0])
        hm_data = pd.DataFrame(tbl_data[1])
    else:
        print('Tables could not be read for following game:\n', data)

    # Assigning team information to respective data frames
    hm_data['Team'], awy_data['Team'] = data['Home Team'], data['Away Team']
    hm_data['Opposing Team'], awy_data['Opposing Team'] = data['Away Team'], data['Home Team']
    hm_data['Home'], awy_data['Home'] = 'Y', 'N'

    # Joining data
    joined = pd.concat([hm_data, awy_data])

    # Additional cleaning of joined data frame
    joined = joined.loc[~joined['Starters'].isin(['Reserves', 'Team Totals']), :] # Removes table delimiters
    joined.columns.values[0] = 'Player'
    joined['Date'] = data['Date']
    joined['Game Link'] = data['BoxScore']
    joined['OT'] = data['OT']
    joined = joined.fillna(0)
    joined = cleanMinutes(joined)

    return(joined)

def cleanMinutes(df, read_csv=False):
    '''
    Converts MP from mm:ss to float for input dataframe
    output specifies cleaned file name
    '''

    if read_csv:
        df = pd.read_csv(df)

    if df['MP'].dtype != 'object':
        # Already numeric
        return df
    else:

        p_notes = df['MP'].tolist()

        for i in range(len(p_notes)):
            try:
                float(p_notes[i][0])
                p_notes[i] = None
            except:
                continue

        df['PlayerNotes'] = p_notes

        # Split MP string on ':' and sum minutes+seconds
        df['MP'] = df['MP'].str[:5]
        df['MP'].fillna('0:0', inplace=True)
        df['MP'].replace('0', '0:0', inplace=True)
        splt = df['MP'].str.split(':')

        mins = []
        for string in splt:
            try:
                mins.append(float(string[0]) + (float(string[1]) / 60))
            except ValueError:
                # field contains non-numeric data. Likely DNPs, or sit-outs.
                mins.append(0)
        df['MP'] = mins

        return df
