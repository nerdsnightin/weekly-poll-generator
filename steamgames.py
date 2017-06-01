import urllib
import urllib2
from bs4 import BeautifulSoup
import re
import json

class SteamException(Exception):
    pass

def getPopularTags(appid):
    '''Get the popular tags for a game.
    
    :param appid: Game appid
    :return: 
    '''
    steamURL = 'http://store.steampowered.com/app/' + str(appid)
    steamRequest = urllib2.Request(steamURL)
    steamRequest.add_header('Cookie', 'birthtime=568022401')
    steamResponse = urllib2.urlopen(steamRequest)
    if steamResponse.msg != "OK":
        raise SteamException("Unable to retrieve Steam App page")
#    if isSteamAgeResponse(steamResponse):
#        steamAgeCheck(steamURL)
    steamPage = steamResponse.read()
    steamSoup = BeautifulSoup(steamPage, 'html.parser')
    popular_tag_links = steamSoup.find_all("div", { "class" : "popular_tags", "class" : "glance_tags"})
    popular_tags = BeautifulSoup(str(popular_tag_links[0]), 'html.parser').find_all("a")
    all_tags = []
    for tag in popular_tags:
        all_tags.append(tag.text.strip())
    return all_tags

def getSteamGames(steamid):
    '''Get all games for Steam user

    Get all games for the given Steam User by Steam ID.
    This is of the form http://steamcommunity.com/id/<steamid>
    :param steamid: Steam ID
    :return: Array of dictionaries possibly containing:
        appid
        friendlyURL
        hours_forever
        last_played
        logo
        name
        availStatLinks
            achievements
            global_achievements
            global_leaderboards
            leaderboards
            stats
    '''
    try:
        val = int(steamid)
        steamIdIsNumber = True
    except ValueError:
        steamIdIsNumber = False
    if steamIdIsNumber:
        steamRequest = urllib2.Request('http://steamcommunity.com/profiles/' + steamid + '/games/?tab=all')
    else:
        steamRequest = urllib2.Request('http://steamcommunity.com/id/' + steamid + '/games/?tab=all')
    steamResponse = urllib2.urlopen(steamRequest)
    if steamResponse.msg != "OK":
        raise SteamException("Unable to retrieve Steam Profile.")
    steamPage = steamResponse.read()
    if steamPage.find("An error was encountered while processing your request") > 0:
        raise SteamException("Invalid Steam ID.")
    steamSoup = BeautifulSoup(steamPage, 'html.parser')
    # print(steamSoup.prettify())
    steamGameJavascript = steamSoup.find_all("script")[-1].string
    pattern = re.compile('[\s]*var rgGames = (.*?);')
    gamesMatch = pattern.match(steamGameJavascript)
    #    print(gamesMatch.groups()[0])
    steamGames = json.loads(gamesMatch.groups()[0])
    return steamGames

if __name__ == "__main__":
    try:
#        steamGames = getSteamGames("heaney")
        steamGames = getSteamGames("76561198067970522")
        for game in steamGames:
            if "name" in game:
                print "Game : " + game['name']
            if "appid" in game:
                print "AppID: " + str(game['appid'])
            if "hours_forever" in game:
                print "Hours played: " + str(game['hours_forever'])
            else:
                print "Hours played: 0"
            print "Tags:"
            tags = getPopularTags(str(game["appid"]))
            for tag in tags:
                print "\t" + str(tag)
            print ""
    except SteamException:
        print "Steam Exception caught."
        raise


exit(0)