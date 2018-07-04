# ---------------------------------------
#   Import Libraries
# ---------------------------------------
import json
import codecs
import re
import os
import clr
clr.AddReference("IronPython.Modules.dll")
import urllib


# ---------------------------------------
#   [Required]  Script Information
# ---------------------------------------
ScriptName = "Invest"
Website = "https://www.twitch.tv/frittenfettsenpai"
Description = "Invest System. No API Key required. Viewer can add currency to a pot. Just set a goal in your stream like: for 100k coins I will do a 12h stream and let them lose their coins."
Creator = "frittenfettsenpai"
Version = "1.0.1"

# ---------------------------------------
#   [Required] Intialize Data (Only called on Load)
# ---------------------------------------
def Init():
    global settings, investEnabled, investAmount
    settingsfile = os.path.join(os.path.dirname(__file__), "settings.json")

    try:
        with codecs.open(settingsfile, encoding="utf-8-sig", mode="r") as f:
            settings = json.load(f, encoding="utf-8")
    except:
        settings = {
            "onStartUpEnabled": False,
            "command": "!invest",
            "commandStart": "!startInvest",
            "commandStop": "!stopInvest",
            "commandSet": "!setInvest",
            "commandReset": "!resetInvest",
            "minimumAmount": 1,
            "investFileName": "investCount.txt",
            "investSound": "",
            "investSoundVolume": 1.00,
            "languageInvestDone": "{0} has invested {1} {2}! New invest value is {3}",
            "languageErrorLessCurrency": "You don't have enough {1}!",
            "languageErrorMinimumAmount": "You have to invest at least {0} {1}!",
            "languageErrorAlreadyStarted": "Invest is already in progress. Stop the invest first!",
            "languageErrorAlreadyStopped": "An active invest is currently not running!",
            "languageInvestStarted": "{0} has opend the invest! Use '{1} <{2}-99999>' to invest. The current invest value is {3}.",
            "languageInvestStopped": "{0} has closed the invest!",
            "languageInvestResetted": "{0} has resetted and disabled the invest!!",
            "languageInvestSetted": "{0} has setted the invest to {1}!"
        }

    investfile = os.path.join(os.path.dirname(__file__), settings['investFileName'])
    if os.path.isfile(investfile):
        file = open(investfile, "r")
        investAmount = int(file.read())
        file.close()
    else:
        investAmount = 0
        SetInvest(0)
    if settings["onStartUpEnabled"]:
        investEnabled = 1
    else:
        investEnabled = 0
    return


# ---------------------------------------
#   [Required] Execute Data / Process Messages
# ---------------------------------------
def Execute(data):
    global settings, investEnabled, investAmount
    if data.IsChatMessage():
        user = data.User
        username = Parent.GetDisplayName(user)
        
        if (investEnabled == 1 and data.GetParam(0).lower() == settings["command"] and data.GetParamCount() > 1):
            userInvest = int(data.GetParam(1))
            if (Parent.GetPoints(user) >= userInvest and userInvest >= settings["minimumAmount"]):
                Parent.RemovePoints(user, userInvest)
                investAmount = investAmount + userInvest
                Parent.SendTwitchMessage(settings["languageInvestDone"].format(username, userInvest, Parent.GetCurrencyName(), investAmount))
                SetInvest(investAmount)
                if (settings['investSound'] != ""):
                    soundfile = os.path.join(os.path.dirname(__file__), settings['investSound'])
                    Parent.PlaySound(soundfile, settings['investSoundVolume'])
            else:
                if (userInvest > settings["minimumAmount"]):
                    Parent.SendTwitchWhisper(user, settings["languageErrorMinimumAmount"].format(settings["minimumAmount"], Parent.GetCurrencyName()))
                else:
                    Parent.SendTwitchWhisper(user, settings["languageErrorLessCurrency"].format(Parent.GetCurrencyName()))   
        elif (data.GetParam(0) == settings["commandStart"] and Parent.HasPermission(user, "Caster", "")):
            if (investEnabled == 1):
                Parent.SendTwitchWhisper(user, settings["languageErrorAlreadyStarted"])
            else:
                Parent.SendTwitchMessage(settings["languageInvestStarted"].format(username, settings['command'], settings['minimumAmount'], investAmount))
                investEnabled = 1
        elif (data.GetParam(0) == settings["commandStop"] and Parent.HasPermission(user, "Caster", "")):
            if (investEnabled == 0):
                Parent.SendTwitchWhisper(user, settings["languageErrorAlreadyStopped"])
            else:
                Parent.SendTwitchMessage(settings["languageInvestStopped"].format(username))
                investEnabled = 0
        elif (data.GetParam(0) == settings["commandReset"] and Parent.HasPermission(user, "Caster", "")):
            investEnabled = 0
            investAmount = 0
            Parent.SendTwitchMessage(settings["languageInvestResetted"].format(username))
            SetInvest(investAmount)
        elif (data.GetParam(0) == settings["commandSet"] and data.GetParamCount() > 1 and Parent.HasPermission(user, "Caster", "")):
            investAmount = int(data.GetParam(1))
            if (investAmount > settings["minimumAmount"]):
                Parent.SendTwitchMessage(settings["languageInvestSetted"].format(username, investAmount))
                SetInvest(investAmount)
    return

#---------------------------------------
#    [Required] Tick Function
#---------------------------------------
def Tick():
    return


def SetInvest(investAmount):
    global settings
    investfile = os.path.join(os.path.dirname(__file__), settings['investFileName'])
    file = open(investfile, "w")
    file.write(str(investAmount))
    file.close()
    return
