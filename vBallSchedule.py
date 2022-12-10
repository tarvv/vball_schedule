from PyPDF2 import PdfReader
from datetime import datetime
import re
import argparse

class SeasonSchedule:
    def __init__(self, teamName, season, league, weeknight, playerCount, gender, location):
        self.teamName = teamName
        self.season = season
        self.league = league
        self.weeknight = weeknight
        self.playerCount = playerCount
        self.gender = gender
        self.location = location
        self.schedule = []
        self.court = 0

    def buildSchedule(self, text):
        year = datetime.today().year
        teamNum = re.findall(r'(\d+). ' + self.teamName.lower(), text).pop()  #Grab the team number based on the name
        self.court = re.findall(r'court (\d+)', text).pop()         #grab the court number
        for line in text.split('\n'):
            if ':' in line and not re.search('[a-zA-Z]', line):     #Is this the line with game times?
                regTimes = line.split()            #Make list of game times
            if re.search('[0-9]-[0-9]', line):      #is this a line containing matches
                gameNight = line.split()
                if len(gameNight) > 5:              #more than 5 means that the line contains a month
                    month = monthNameToNum(gameNight.pop(0))
                    if month == 1: year += 1           #if the schedule switches to January, select the following year. TODO: will be an issue for winter league
                day = int(gameNight.pop(0))
                for i in range(len(gameNight)):
                    if re.search(rf'[{teamNum}]', gameNight[i]):
                        gameTime = regTimes[i].split(':')
                        self.schedule.append(datetime(year, month, day, int(gameTime[0])+12, int(gameTime[1])))
    
    def __str__(self):
        scheduleStr = '-----------------------------------\n'
        scheduleStr = scheduleStr + f'Schedule for team {self.teamName} on court {self.court}\n'
        scheduleStr = scheduleStr +'-----------------------------------\n'
        for game in self.schedule:
            scheduleStr = scheduleStr + game.strftime('%B %d at %I:%M%p') + '\n'
        return scheduleStr


def extractText(fName):
    reader = PdfReader(fName)
    page = reader.pages[0]
    return page.extract_text().lower()

def monthNameToNum(mName):
    return {'jan':1, 'feb':2, 'mar':3, 'apr':4, 'may':5, 'jun':6, 'jul':7, 'aug':8, 'sept':9, 'sep':9, 'oct':10, 'nov':11, 'dec':12}[mName]

def downloadFile():
    #return(fileName)
    pass
    
def parseArgs():
    parser = argparse.ArgumentParser(description='Do stuff with vball schedule')
    parser.add_argument('-t', '--teamname', default='Suggit', nargs='?', help='Name of team as it appears on the schedule. If multiple words, surround with quotes.')
    parser.add_argument('-s', '--season', default='fall', nargs='?', choices=['spring', 'summer', 'fall', 'winter'], help='The season for the desired schedule')
    parser.add_argument('-n', '--weeknight', default='tue', nargs='?', choices=['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'], help='Night of the week that games are played')
    parser.add_argument('-l', '--league', default='bb-b', nargs='?', choices=['a', 'b', 'bb-b', 'bb', 'c'], help='League of play')
    parser.add_argument('-c', '--playercount', default=4, nargs='?', choices=[4, 6], type=int, help='Number of players on a team')
    parser.add_argument('-g', '--gender', default='m', nargs='?', choices=['m', 'f', 'c'], help='League gender; \'c\' for coed')
    parser.add_argument('-L', '--location', default='oshkosh', nargs='?', help='Location of games')
    parser.add_argument('-d', '--download', action='store_true', help='Force download of the schedule')
    return parser.parse_args()

args = parseArgs()
x = SeasonSchedule(args.teamname, args.season, args.league, args.weeknight, args.playercount, args.gender, args.location)
x.buildSchedule(extractText('working.pdf'))
print(x)