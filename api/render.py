import json
import random
import requests

from base64 import b64encode
from flask import render_template

from .constants import FALLBACK_THEME, PLACEHOLDER_IMAGE


class SvgRenderer():

    def renderLoginSVG(self, login_url):
        try:
            templates = json.loads(open("api/templates.json", "r").read())
            rendered_template = render_template(
                templates["templates"]["login"], **{"login_url": login_url})
            return rendered_template
        except Exception as e:
            print(f"Failed to load templates: {e}")

    def renderSVG(self, data, background_color, border_color):
        barCount = 84
        contentBar = "".join(
            ["<div class='bar'></div>" for _ in range(barCount)])
        barCSS = self.__barGen(barCount)

        if not "is_playing" in data:
            # contentBar = "" #Shows/Hides the EQ bar if no song is currently playing
            currentStatus = "Was playing:"
            recentPlaysLength = len(data["items"])
            itemIndex = random.randint(0, recentPlaysLength - 1)
            item = data["items"][itemIndex]["track"]
        else:
            item = data["item"]
            currentStatus = "Vibing to:"

        if item["album"]["images"] == []:
            image = PLACEHOLDER_IMAGE
        else:
            image = self.__loadImageB64(item["album"]["images"][1]["url"])

        artistName = item["artists"][0]["name"].replace("&", "&amp;")
        songName = item["name"].replace("&", "&amp;")
        songURI = item["external_urls"]["spotify"]
        artistURI = item["artists"][0]["external_urls"]["spotify"]

        dataDict = {
            "contentBar": contentBar,
            "barCSS": barCSS,
            "artistName": artistName,
            "songName": songName,
            "songURI": songURI,
            "artistURI": artistURI,
            "image": image,
            "status": currentStatus,
            "background_color": background_color,
            "border_color": border_color
        }

        return render_template(self.__getTemplate(), **dataDict)

    def __barGen(self, barCount):
        barCSS = ""
        left = 1
        for i in range(1, barCount + 1):
            anim = random.randint(1000, 1350)
            barCSS += (
                ".bar:nth-child({})  {{ left: {}px; animation-duration: {}ms; }}".format(
                    i, left, anim
                )
            )
            left += 4
        return barCSS

    def __loadImageB64(self, url):
        response = requests.get(url)
        return b64encode(response.content).decode("ascii")

    def __getTemplate(self):
        try:
            file = open("api/templates.json", "r")
            templates = json.loads(file.read())
            return templates["templates"][templates["current-theme"]]
        except Exception as e:
            print(f"Failed to load templates: {e}")
            return FALLBACK_THEME
