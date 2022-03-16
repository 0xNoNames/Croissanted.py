#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from getpass import getpass
import random
import sys
import os
import requests
import re

class Croissanted():
    def __init__(self):
        self.__authorizationToken = ""
        self.__userInfos = {}
        self._guildsInfos = []
        self._channelsInfos = []
        self._selectedGuild = {}
        self._selectedChannel = {}
        self.showMenu()
    
    @property
    def authorizationToken(self): 
        return self.__authorizationToken 
    
    @property
    def userInfos(self):
        return self.__userInfos
    
    @property
    def guildsInfos(self):
        return self._guildsInfos
    
    @property
    def channelsInfos(self):
        return self._channelsInfos

    @property
    def selectedGuild(self):
        return self._selectedGuild  
    
    @property
    def selectedChannel(self):
        return self._selectedChannel        
            
    @authorizationToken.setter    
    def authorizationToken(self, authToken):
        self.__authorizationToken = authToken
        
    @userInfos.setter
    def userInfos(self, userInfos):
        self.__userInfos = userInfos
        
    @guildsInfos.setter
    def guildsInfos(self, guilds):
        self._guildsInfos = guilds
        
    @channelsInfos.setter
    def channelsInfos(self, channels):
        self._channelsInfos = channels
        
    @selectedGuild.setter
    def selectedGuild(self, guild):
        self._selectedGuild = guild  
            
    @selectedChannel.setter
    def selectedChannel(self, channel):
        self._selectedChannel = channel
        
        
    def resetObject(self):    
        self.__authorizationToken = ""
        self.__userInfos = {}
        self._guildsInfos = []
        self._channelsInfos = []
        self._selectedGuild = {}
        self._selectedChannel = {}
        
        
    def connect(self, authToken):
        self.showHeader()
                
        if (not re.search("[\w-]{24}\.[\w-]{6}\.[\w-]{27}", authToken)):
            getpass("{!} ERROR: Bad authorization token {!}\nPress Enter to return...")
            self.resetObject()
            return
        
        try:    
            # Retreive user's informations
            print("{+} Retreiving token's informations... {+}")
            url = "https://discord.com/api/v9/users/@me"
            with requests.get(url, headers={"Authorization" : authToken}) as rep:
                self.showHeader()
                data = rep.json()
                if rep.status_code == 401:
                    self.resetObject()
                    getpass("{!} ERROR: Bad authorization token {!}\nPress Enter to return...")
                    return
                else:
                    self.authorizationToken = authToken
                    self.userInfos = data
                    
            # Retreive user's servers informations
            print("{+} Retreiving user's servers informations... {+}")
            url = "https://discord.com/api/v9/users/@me/guilds"
            with requests.get(url, headers={"Authorization" : authToken}) as rep:
                self.showHeader()
                data = rep.json()
                if rep.status_code == 401:
                    self.resetObject()
                    getpass("{!} ERROR: Bad authorization token {!}\nPress Enter to return...")
                    return
                else:
                    guilds = []
                    for guild in rep.json():
                        guilds.append({"id" : guild.get("id"), "name" : guild.get("name")})
                    self.guildsInfos = guilds   
        except Exception as e:
            input(e)
            self.resetObject()
            getpass("{!} ERROR: Can't reatch Discord's servers {!}\nPress Enter to return...")
    
    
    def selectGuild(self):
        self.showHeader()
        
        print("{+} Available servers {+}\n")
        for i, guild in enumerate(self.guildsInfos):
            print(f'    [{i+1}] - {guild.get("name")}')

        choice = input("\n\nEnter your choice (\"Q\" to quit): ")
        if (choice.upper() == "Q"):
            return
            
        try:
            if (int(choice) == 0):
                self.selectGuild()
            self.selectedGuild = self.guildsInfos[int(choice)-1]
        except Exception as e:
            input(e)
            self.selectGuild()
            
        self.showHeader()            
        print("{+} Retreiving channels informations... {+}")
        try:
            url = f"https://discord.com/api/v9/guilds/{self.selectedGuild.get('id')}/channels"
            with requests.get(url, headers={"Authorization" : self.authorizationToken}) as rep:
                self.showHeader()
                data = rep.json()
                if rep.status_code == 401:
                    getpass("{!} ERROR: User doesn't have enough permissions {!}\nPress Enter to return...")
                    self.selectGuild()
                else:
                    orphanChannels = []        
                    categories = []
                    for element in data:
                        if (element.get("type") == 4):
                            channels = [{"id":channel.get("id"), "name":channel.get("name")} for channel in data if (channel.get("parent_id") == element.get("id") and channel.get("type") == 0)]
                            if (len(channels) > 0):
                                categories.append({"name" : element.get("name"), "id" : element.get("id"), "channels" : channels})
                        elif (element.get("type") == 0 and element.get("parent_id") == None) :
                            orphanChannels.append({"name" : element.get("name"), "id" : element.get("id")})
                    
                    self.channelsInfos = [categories, orphanChannels]
                    self.selectedChannel = {}
                    self.selectChannel()
        except Exception as e:
            input(e)
            getpass("{!} ERROR: Can't reatch Discord's servers {!}\nPress Enter to return...")
            
            
    def selectChannel(self):
        self.showHeader()            
        
        print("{+} Available channels {+}\n")
        channels = []
        i = 1
        for category in self.channelsInfos[0]:
            print("    {-} " + category.get('name') + " {-}")
            for channel in category.get("channels"):
                channels.append(channel)
                print(f'        [{i}] - {channel.get("name")}')
                i += 1
            print("\n", end="")
        
        if (len(self.channelsInfos[1]) > 0):
            print("    {-} Uncategorized channels {-}")
            for channel in self.channelsInfos[1]:
                channels.append(channel)
                print(f'        [{i}] - {channel.get("name")}')
                i += 1
        
        choice = input("\n\nEnter your choice (\"Q\" to quit): ")
        if (choice.upper() == "Q"):
            return        
        
        try:
            if (int(choice) == 0):
                self.selectChannel()
            self.selectedChannel = channels[int(choice)-1]
        except Exception as e:
            self.selectChannel()
            
            
    def sendSingle(self):
        self.showHeader()
        
        message = input("Message to send (\"$Q\" to quit): ") 
            
        if (message.upper() == "$Q"):
            return
        
        self.showHeader()
        
        print(f"Sending message: \"{message}\"")
        
        url = f"https://discord.com/api/v9/channels/{self._selectedChannel.get('id')}/messages"
        json = {"content": message, "nonce": random.randint(0, sys.maxsize), "tts": "false"}
        headers = {"Authorization": self.__authorizationToken}
        with requests.post(url, json=json, headers=headers) as rep:
            self.showHeader()
            if (rep.status_code == 200):
                getpass("{+} Message sent {+}\nEnter to return...")
            else:
                getpass("{!} ERROR: Message not sent, user may not have enough permissions {!}\nEnter to return...")
                
                
    def sendMultiple(self):
        self.showHeader()
        
        while not False:  
            message = input("Message to send (\"$Q\" to quit): ") 
                
            if (message.upper() == "$Q"):
                return
            
            url = f"https://discord.com/api/v9/channels/{self._selectedChannel.get('id')}/messages"
            json = {"content": message, "nonce": random.randint(0, sys.maxsize), "tts": "false"}
            headers = {"Authorization": self.__authorizationToken}
            with requests.post(url, json=json, headers=headers) as rep:
                if (rep.status_code == 200):
                    print("{+} Message sent {+}\n")
                else:
                    print("{!} ERROR: Message not sent, user may not have enough permissions {!}\n")


    def showHeader(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print(bytes.fromhex("20205f5f5f5f2020202020202020202020202020205f20202020202020202020202020202020202020202020202020205f20202020202020202020202020205f0a202f205f5f5f7c205f205f5f2020205f5f5f2020285f29205f5f5f20205f5f5f2020205f5f205f20205f205f5f20207c207c5f2020205f5f5f2020205f5f7c207c0a7c207c202020207c20275f5f7c202f205f205c207c207c2f205f5f7c2f205f5f7c202f205f60207c7c20275f205c207c205f5f7c202f205f205c202f205f60207c0a7c207c5f5f5f207c207c2020207c20285f29207c7c207c5c5f5f205c5f5f20205c7c20285f7c207c7c207c207c207c7c207c5f207c20205f5f2f7c20285f7c207c0a205c5f5f5f5f7c7c5f7c202020205c5f5f5f2f207c5f7c7c5f5f5f2f7c5f5f5f2f205c5f5f2c5f7c7c5f7c207c5f7c205c5f5f7c205c5f5f5f7c205c5f5f2c5f7c0a").decode("ASCII") + "\n" )
        
        message = "{#} Username: " + (self.userInfos.get("username") if (len(self.userInfos) > 0) else "_") + "\n"
        message += "{#} Server: " + ((self.selectedGuild.get("name") + " (" + self.selectedGuild.get("id") + ")") if (len(self.selectedGuild) > 0) else "_") + "\n"
        message += "{#} Channel: " +  ((self.selectedChannel.get("name") + " (" + self.selectedChannel.get("id") + ")") if (len(self.selectedChannel) > 0) else "_") + "\n"
        print(f"{message}\n")


    def showMenu(self):
        self.showHeader()
        
        noAuth = ["Set authorization token", "Quit"]
        noGuild = ["Change authorization token", "Select server", "", "List user's informations", "Quit"]
        noChan = ["Change authorization token", "Select server", "Select channel", "", "List user's informations", "Quit"]
        all = ["Change authorization token", "Select server", "Select channel", "", "Send single message", "Send multiple message", "", "List user's informations", "Quit"]
        
        try:
            if (self.authorizationToken == ""):
                for i in range(0, 2):
                    print(f"    [{i + 1}] - " + noAuth[i])
                choice = noAuth[int(input("\n\nEnter your choice: ")) - 1] 
            elif (len(self.selectedGuild) == 0):
                for i in range(0, 5):
                    if (noGuild[i] == ""):
                        print("\n", end="")
                        continue
                    print(f"    [{i + 1}] - " + noGuild[i])
                choice = noGuild[int(input("\n\nEnter your choice: ")) - 1]
            elif (len(self.selectedChannel) == 0):
                for i in range(0, 6):
                    if (noChan[i] == ""):
                        print("\n", end="")
                        continue
                    print(f"    [{i + 1}] - " + noChan[i])
                choice = noChan[int(input("\n\nEnter your choice: ")) - 1]
            else:
                for i in range(0, 9):
                    if (all[i] == ""):
                        print("\n", end="")
                        continue
                    print(f"    [{i + 1}] - " + all[i])   
                choice = all[int(input("\n\nEnter your choice: ")) - 1]
        except Exception:
            choice = ""

        if (choice == "Set authorization token" or choice == "Change authorization token"):
            self.showHeader()
            token = getpass("Authorization token (\"Q\" to quit): ")
            if (token.upper() != "Q"):
                self.connect(token)
        
        elif (choice == "Select server"):
            self.selectGuild()
                
        elif (choice == "Select channel"):
            self.selectChannel()
            
        elif (choice == "Send single message"):
            self.sendSingle()
            
        elif (choice == "Send multiple message"):
            self.sendMultiple()
                
        elif (choice == "List user's informations"):
            self.showHeader()
            for key in self.userInfos:
                print(f"    {key} -> {self.userInfos[key]}")
            getpass("\n\nPress Enter to return...")
                    
        elif (choice == "Quit"):
            os.system('cls' if os.name == 'nt' else 'clear')
            sys.exit()
        
        self.showMenu()


def main():
    Croissanted()


if __name__ == "__main__":
    main()