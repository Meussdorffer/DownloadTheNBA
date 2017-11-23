#######################################################
# Jack Meussdorffer                                   #
# Created:  Jul-29-2017                               #
# Modified: Nov-22-2017                               #
# LinkedIn: https://www.linkedin.com/in/meussdorffer/ #
# e-Mail:   jackcmv@gmail.com                         #
#######################################################

import os
from time import sleep
from functions import *

do_sleep = False

# Starting script timer
startTime = datetime.datetime.now()


######################################################
#       SCRAPING EVERY LINK FOR EVERY GAME           #
######################################################


# Assemble HTML strings at a year-month level from year (x) to year (y)
# and creating a table of game info and box score links for every game played
start_yr = 1989
end_yr = 1989
html_strings = assembleSeasonHTML(start_yr, end_yr)


# Determines output file name depending on single season pull or multi season pull
# mainout = "C:\\Users\\Jack\\Desktop\\Scraping NBA Data\\Output\\"
mainout = os.getcwd()+'/Output/'

if start_yr == end_yr:
    # Single season
    output = mainout + str(start_yr) + '.csv'
else:
    # Multiple seasons
    output = mainout + str(start_yr) + '_' + str(end_yr) + '.csv'


gamedata = []
for year_month in html_strings:
    try:
        # Getting table of all games for year ranges in assembleSeasonHTML()
        gamedata.append(getGameLinks(html_strings[year_month], post_2000=(year_month[0] > 2000)))
    except ValueError:
        # Link is invalid, no games played during month/year combo
        print('FAILED: ' + html_strings[year_month])
        continue
# Joining list of dfs
all_gamedata = pd.concat(gamedata)

######################################################
#       SCRAPING BOX-SCORES FOR ALL GAMES            #
######################################################

games = []

for index, row in all_gamedata.iterrows():

    # Waiting 5 seconds before trying to scrape next game
    if do_sleep:
        sleep(5)

    df = scrapeGameData(row['BoxScore'], row['Date'], row['Home Team'], row['Away Team'], row['OT'])
    games.append(df)

data = pd.concat(games)
data.to_csv(output, index = False)

print('Scrape completed at: ' + str(datetime.datetime.now()) + ' in ' + str(startTime - datetime.datetime.now()))