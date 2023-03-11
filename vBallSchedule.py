import sys
import io
import re
import argparse
import requests
from PyPDF2 import PdfReader    # must be version >2.*
from datetime import datetime

class SeasonSchedule:
    def __init__(self, teamName, season, league, weekday, playerCount, gender, location):
        self.teamName = teamName
        self.season = season
        self.league = league
        self.weekday = weekday
        self.playerCount = playerCount
        self.gender = gender
        self.court = 0
        self.location = location
        self.schedule = self.buildSchedule()   # List of all vball games

    def buildSchedule(self):
        rawText = self.getScheduleText()
        scheduleList = []
        year = datetime.today().year
        teamNum = re.findall(r'(\d+). ' + self.teamName.lower(), rawText).pop()  # Grab the team number based on the name
        #TODO: The following will give questionable results for leagues that use multiple courts
        self.court = re.findall(r'court (\d+)', rawText).pop()         # grab the court number
        for line in rawText.split('\n'):
            if ':' in line and not re.search('[a-zA-Z]', line):     # Is this the line with game times?
                #TODO: some schedules have letters (e.g., 'DH', 'Court') on this line but must get here!
                regTimes = line.split()            # Make list of game times
            if re.search('[0-9]-[0-9]', line):      # is this a line containing matches
                gameNight = line.split()
                if len(gameNight) > 5:              # more than 5 means that the line contains a month
                    month = monthNameToNum(gameNight.pop(0))
                    if month == 1: year += 1           # if the schedule switches to January, select the following year
                day = int(gameNight.pop(0))
                for i in range(len(gameNight)):
                    if re.search(rf'[{teamNum}]', gameNight[i]):
                        gameTime = regTimes[i].split(':')
                        scheduleList.append(datetime(year, month, day, int(gameTime[0])+12, int(gameTime[1])))
        return(scheduleList)

    def getScheduleText(self):
        url = self.buildURL()

        #TODO: Should these use a context manager?
        r = requests.get(url)       # Get request for pdf schedule
        f = io.BytesIO(r.content)   # hold pdf bytes in memory
        reader = PdfReader(f)       
        text = reader.pages[0].extract_text().lower()   # Extract the text in lower case
        return(text)

    def buildURL(self):
        #TODO Is using space character ' ' always safe in URL; should we use url encoding '%20'?
        #TODO Locations that aren't oshkosh have weird urls and league names

        url = 'https://www.meetatthebar.com/league_schedules/'
        if self.season == 'winter' and datetime.now().month <= 3:
            # Winter schedule year is labelled in start year, so subtract 1 from current year in the beginning of the year
            urlYear = str(datetime.now().year - 1)
        else:
            urlYear = str(datetime.now().year)

        match self.location:
            case 'green bay lime kiln':
                pass
            case 'appleton lynndale':
                pass
            case 'oshkosh':
                urlDay = {'mon':'Mon', 'tue':'Tues', 'wed':'Wed', 'thu':'Thurs'}[self.weekday]
                urlGender = {'m':'Mens', 'w':'Womens', 'c':'Coed', 'kq':'KQ'}[self.gender]
                urlPlayerCount = {4:'Quads', 6:'Sixes'}[self.playerCount]
                url += 'Oshkosh ' + \
                       urlDay + ' ' + \
                       urlYear + ' ' + \
                       self.season.capitalize() + ' ' + \
                       urlGender + ' ' + \
                       urlPlayerCount + ' ' + \
                       self.league.upper() + '.pdf'
            case 'wausau':
                pass
            case _:
                sys.exit('Location' + self.locationNumToName(self.location) + ' is not known')
        print(url)
        return url
    
    def locationNameToNum(self, lName):
        # Converts lower case location string to the number as used in The Bar's url
        return{
            'green bay lime kiln':1001,
            'appleton lynndale':1002,
            'oshkosh':1003,
            'green bay holmgren way':1004,
            'appleton the avenue':1005,
            'wausau':1006
            }[lName]

    def locationNumToName(self, lNum):
        # Helper function to return location as human readable string
        return{
            1001:'green bay lime kiln',
            1002:'appleton lynndale',
            1003:'oshkosh',
            1004:'green bay holmgren way',
            1005:'appleton the avenue',
            1006:'wausau'
        }[lNum]

    def __str__(self):
        scheduleStr = '-----------------------------------\n'
        scheduleStr = scheduleStr + f'Schedule for team {self.teamName} on court {self.court}\n'
        scheduleStr = scheduleStr +'-----------------------------------\n'
        for game in self.schedule:
            scheduleStr = scheduleStr + game.strftime('%B %d at %I:%M%p') + '\n'
        return scheduleStr

def scheduleExists(location):
    #TODO should check by scanning the website rather than hardcoded
    if location == 'green bay holmgren way' or location == 'appleton the avenue':
        return False
    return True

def monthNameToNum(mName):
    return {'jan':1, 'feb':2, 'mar':3, 'apr':4, 'may':5, 'jun':6, 'jul':7, 'aug':8, 'sept':9, 'sep':9, 'oct':10, 'nov':11, 'dec':12}[mName]
    
def parseArgs():
    # command for default args: python3 vBallSchedule.py
    #TODO print example use
    parser = argparse.ArgumentParser(description='Do stuff with vball schedule')
    parser.add_argument('-t', '--teamname', default='Suggit', nargs='?', help='Name of team as it appears on the schedule. If multiple words, surround with quotes.')
    parser.add_argument('-s', '--season', default='spring', nargs='?', choices=['spring', 'summer', 'fall', 'winter'], help='The season for the desired schedule')
    parser.add_argument('-n', '--weekday', default='tue', nargs='?', choices=['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'], help='Night of the week that games are played')
    parser.add_argument('-l', '--league', default='b', nargs='?', choices=['a', 'b', 'bb-b', 'bb', 'c'], help='League of play')
    parser.add_argument('-c', '--playercount', default=4, nargs='?', choices=[4, 6], type=int, help='Number of players on a team')
    parser.add_argument('-g', '--gender', default='m', nargs='?', choices=['m', 'f', 'c', 'kq'], help='League gender; \'c\' for coed and \'kq\' for kings and queens')
    parser.add_argument('-L', '--location', default='oshkosh', nargs='?', help='Location of games')
    parser.add_argument('-d', '--download', action='store_true', help='Force download of the schedule') #TODO need to add functionality
    #TODO add option to use downloaded file rather than from get request
    return parser.parse_args()

def main():
    args = parseArgs()
    if not scheduleExists(args.location):
        sys.exit('No volleyball schedules for location ' + args.location)   # locations don't have vball schedules, just give up.

    scheduleObj = SeasonSchedule(args.teamname, args.season, args.league, args.weekday, args.playercount, args.gender, args.location)
    print(scheduleObj)

if __name__ == '__main__':
    main()
