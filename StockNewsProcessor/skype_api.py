# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 20:25:37 2017

@author: Isaac
"""

from skpy import Skype
sk = Skype('ahoumaisaac', 'patriots') # connect to Skype

sk.user # you
sk.contacts # your contacts
sk.chats # your conversations

ch = sk.chats.create(["joe.4", "daisy.5"]) # new group conversation
ch = sk.contacts["joe.4"].chat # 1-to-1 conversation

ch.sendMsg(content) # plain-text message
ch.sendFile(open("song.mp3", "rb"), "song.mp3") # file upload
ch.sendContact(sk.contacts["daisy.5"]) # contact sharing

ch.getMsgs() # retrieve recent messages