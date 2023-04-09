import os
import json
import random
import re

import requests
import colorgram

from base64 import b64encode
from dotenv import load_dotenv, find_dotenv
from flask import Flask, Response, render_template, request
from io import BytesIO
from PIL import Image


load_dotenv(find_dotenv())

# Spotify scopes:
#   user-read-currently-playing
#   user-read-recently-played
PLACEHOLDER_IMAGE = "/9j/4QDKRXhpZgAATU0AKgAAAAgABgESAAMAAAABAAEAAAEaAAUAAAABAAAAVgEbAAUAAAABAAAAXgEoAAMAAAABAAIAAAITAAMAAAABAAEAAIdpAAQAAAABAAAAZgAAAAAAAADYAAAAAQAAANgAAAABAAeQAAAHAAAABDAyMjGRAQAHAAAABAECAwCgAAAHAAAABDAxMDCgAQADAAAAAQABAACgAgAEAAAAAQAAAu+gAwAEAAAAAQAAAvOkBgADAAAAAQAAAAAAAAAAAAD/4gIoSUNDX1BST0ZJTEUAAQEAAAIYYXBwbAQAAABtbnRyUkdCIFhZWiAH5gABAAEAAAAAAABhY3NwQVBQTAAAAABBUFBMAAAAAAAAAAAAAAAAAAAAAAAA9tYAAQAAAADTLWFwcGzs/aOOOIVHw220vU962hgvAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAApkZXNjAAAA/AAAADBjcHJ0AAABLAAAAFB3dHB0AAABfAAAABRyWFlaAAABkAAAABRnWFlaAAABpAAAABRiWFlaAAABuAAAABRyVFJDAAABzAAAACBjaGFkAAAB7AAAACxiVFJDAAABzAAAACBnVFJDAAABzAAAACBtbHVjAAAAAAAAAAEAAAAMZW5VUwAAABQAAAAcAEQAaQBzAHAAbABhAHkAIABQADNtbHVjAAAAAAAAAAEAAAAMZW5VUwAAADQAAAAcAEMAbwBwAHkAcgBpAGcAaAB0ACAAQQBwAHAAbABlACAASQBuAGMALgAsACAAMgAwADIAMlhZWiAAAAAAAAD21QABAAAAANMsWFlaIAAAAAAAAIPfAAA9v////7tYWVogAAAAAAAASr8AALE3AAAKuVhZWiAAAAAAAAAoOAAAEQsAAMi5cGFyYQAAAAAAAwAAAAJmZgAA8qcAAA1ZAAAT0AAACltzZjMyAAAAAAABDEIAAAXe///zJgAAB5MAAP2Q///7ov///aMAAAPcAADAbv/bAIQAAQEBAQEBAgEBAgMCAgIDBAMDAwMEBQQEBAQEBQYFBQUFBQUGBgYGBgYGBgcHBwcHBwgICAgICQkJCQkJCQkJCQEBAQECAgIEAgIECQYFBgkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJ/90ABAAv/8AAEQgC8wLmAwEiAAIRAQMRAf/EAaIAAAEFAQEBAQEBAAAAAAAAAAABAgMEBQYHCAkKCxAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6AQADAQEBAQEBAQEBAAAAAAAAAQIDBAUGBwgJCgsRAAIBAgQEAwQHBQQEAAECdwABAgMRBAUhMQYSQVEHYXETIjKBCBRCkaGxwQkjM1LwFWJy0QoWJDThJfEXGBkaJicoKSo1Njc4OTpDREVGR0hJSlNUVVZXWFlaY2RlZmdoaWpzdHV2d3h5eoKDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uLj5OXm5+jp6vLz9PX29/j5+v/aAAwDAQACEQMRAD8A/kXooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAP/Q/kXooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAP/R/kXooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAP/S/kXooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAP/T/kXooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAP/U/kXooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAP/V/kXooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAP/W/kXooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAP/X/kXooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAP/Q/kXooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAP/R/kXooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAP/S/kXooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAP/T/kXooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigDqtB8E+M/FFu1z4Y0i81GNDsZraB5VVvQ7AcVt/wDCoPit/wBCzqv/AIBz/wDxNf0D/wDBFUkfBPxXg/8AMXj/APRNfs6Hb1oA/hd/4VB8Vv8AoWNV/wDAOb/4mm/8Kh+K/wD0LGq/+Ac3/wATX90u9vWje3rQB/C1/wAKg+K+f+RY1X/wDm/+JrG1zwL408L263niPR73T4Sdoe5t5IkJ7AFlAzX9329vWvyA/wCCzpJ/Zz0LP/QYX/0XQB/MqeKSnN96m0AFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFAH//U/kXooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigD+kz/gip/yRPxWP+ovH/6Jr9mxX4zf8EVP+SJ+Kx/1F4//AETX7NdqACiiigAr8gP+CzY/4x10L/sMj/0Cv1/r8gf+Czf/ACbroP8A2GV/9F0AfzK0UUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFAH//1f5F6KKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA/pO/4Ip/8kT8Wf8AYXj/APRNfs3xivxk/wCCKf8AyRPxX/2F4/8A0TX7NDpzQAtJRRQAV+QP/BZvj9nXQR/1GV/9F1+v/tX5Af8ABZv/AJN10H/sMr/6LoA/mVooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAP//W/kXooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigD+k7/gin/yRPxZ/wBheP8A9E1+zY6V+Mn/AART/wCSKeK/+wvH/wCia/ZugBKWij8KACvyB/4LOf8AJu2g/wDYZX/0XX6/dK/IH/gs5/ybroP/AGGV/wDRdAH8ylFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQB/9f+ReiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAP6Tv+CKX/JFPFn/AGF4/wD0TX7N1+Mn/BFP/kifiz/sLx/+ia/ZvnsKACilpMdqADOeK/ID/gs3/wAm66D/ANhlf/RdfsBjFfkB/wAFnP8Ak3XQf+wyv/ougD+ZSiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA//9D+ReiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAP6Tv+CKX/JE/Ff/AGF4/wD0TX7Ng1+Mn/BFL/kifiz/ALC8f/omv2c6UAGOKKTtTqAEHpX5Af8ABZzH/DOug/8AYZX/ANF1+wHFfkB/wWd/5N10H/sMr/6LoA/mTooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAP/9H+ReiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAP6T/wDgil/yRPxX/wBheP8A9E1+zfpxivxk/wCCKX/JE/Ff/YXj/wDRNfs2OnSgAxRj0pfwpPagAGfSvyA/4LO/8m66D/2Gl/8ARdfsB36V+P8A/wAFnP8Ak3XQf+wyv/ougD+ZSiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA//9L+ReiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAP6T/wDgil/yRPxZ/wBheP8A9E1+zg4r8Yv+CKP/ACRPxZ/2F4//AETX7PDFACdqO+BxS5HTFKOnFADa/ID/AILOY/4Z10H/ALDK/wDouv2AwOBX4/8A/BZwY/Z00H/sMr/6LNAH8ydFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQB//T/kXopaOM0AJRRRQAUUtHGaAEooooAKKWjjNACUUUUAFFLRxmgBKKKKACilo4zQAlFFFABRS0cZoASiiigAopaOM0AJRRRQAUUtHGaAEooooAKKWjjNACUUUUAFFLRxmgBKKKKACilo4zQAlFFFABRS0cZoASiiigD+k//gil/wAkT8Wf9heP/wBE1+zq1+Mf/BFP/kiXiz/sLx/+ia/ZwY4oAO1JThQOtAB2r8f/APgs5j/hnTQcf9Blf/RZr9gOtfj9/wAFnB/xjpoOf+gyv/ougD+ZOilpKACilo4zQAlFFFABRS0cZoASiiigAopaOM0AJRRRQAUUtHGaAEooooAKKWjjNACUUUUAFFLRxmgBKKKKACilo4zQAlFFFABRS0cZoASiiigAopaOM0AJRRRQAUUuKMUAf//U/kY7UlLxR0FACUvSij2oAO1JS8UdBQAlL0oo9qADtSUv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o8c61HcapGPk0uyKTXjN2BjU/IPd8Cv5zP2tP+Ci3xi/aZuZvDujySeG/Cp4GnW0hDzL63Ei43/7n3RX5+3V3d39w97fSNNNKSWd23Mx9z3quRnGe39OlACKFxhQAB0xS0tFABiiiigApKWigAxRRRQAUlLRQAYooooAKSlooAMUUUUAFJS0UAGKKKKACkpaKADFFFFABSUtFABiiiigApKWigAxRRRQAUlLRQAYooooAKSlooAMUUUUAFJS0UAJgUYFH1pPloA//9D+R+iiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooATjtQFAzS0UAJwDmgAZzgcUtFACY/SloooAQgHAbt0oxS0UAJ9KWiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA/9H+R+iiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA/9L+R+iiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA/9P+R+iiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA/9T+R+iiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA/9X+R+iiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA/9b+R+iiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA/9f+R+iiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA/9D+R+iiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA/9H+R+iiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA/9L+R+iiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA/9P+R+iiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA/9T+R+iiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA/9X+R+iiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA/9b+R+iiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA/9k="
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_SECRET_ID = os.getenv("SPOTIFY_SECRET_ID")
SPOTIFY_REFRESH_TOKEN = os.getenv("SPOTIFY_REFRESH_TOKEN")
SPOTIFY_TOKEN = ""

DEFAULT_GRADIENT_COLORS = ["#20BDFF", "#ab66ff", "#5433FF", "#20BDFF"]
REFRESH_TOKEN_URL = "https://accounts.spotify.com/api/token"
NOW_PLAYING_URL = "https://api.spotify.com/v1/me/player/currently-playing"
RECENTLY_PLAYING_URL = (
    "https://api.spotify.com/v1/me/player/recently-played?limit=10"
)

app = Flask(__name__)


def get_auth():
    return b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_SECRET_ID}".encode()).decode(
        "ascii"
    )


def refresh_token():
    data = {
        "grant_type": "refresh_token",
        "refresh_token": SPOTIFY_REFRESH_TOKEN,
    }

    headers = {"Authorization": "Basic {}".format(get_auth())}
    response = requests.post(
        REFRESH_TOKEN_URL, data=data, headers=headers).json()

    try:
        return response["access_token"]
    except KeyError:
        print(json.dumps(response))
        print("\n---\n")
        raise KeyError(str(response))


def get(url):
    global SPOTIFY_TOKEN

    if (SPOTIFY_TOKEN == ""):
        SPOTIFY_TOKEN = refresh_token()

    response = requests.get(
        url, headers={"Authorization": f"Bearer {SPOTIFY_TOKEN}"})

    if response.status_code == 401:
        SPOTIFY_TOKEN = refresh_token()
        response = requests.get(
            url, headers={"Authorization": f"Bearer {SPOTIFY_TOKEN}"}).json()
        return response
    elif response.status_code == 204:
        raise Exception(f"{url} returned no data.")
    else:
        return response.json()


def generate_bars_css(barCount):
    bar_css = ""
    left = 1
    for i in range(1, barCount + 1):
        anim = random.randint(500, 1000)
        # below code generates random cubic-bezier values
        x1 = random.random()
        y1 = random.random()*2
        x2 = random.random()
        y2 = random.random()*2
        bar_css += (
            ".bar:nth-child({})  {{ left: {}px; animation-duration: 15s, {}ms; animation-timing-function: ease, cubic-bezier({},{},{},{}); }}".format(
                i, left, anim, x1, y1, x2, y2
            )
        )
        left += 4
    return bar_css


def get_template():
    try:
        with open("api/templates.json", "r") as template_file:
            template_data = json.load(template_file)
            current_theme = template_data["current-theme"]
            templates = template_data["templates"]
            return current_theme, templates[current_theme]
    except FileNotFoundError:
        raise Exception("Templates file not found")
    except json.JSONDecodeError:
        raise Exception("Invalid JSON data in templates file")
    except KeyError:
        raise Exception("Current theme not found in templates file")


def load_image_base64(url):
    response = requests.get(url)
    return b64encode(response.content).decode("ascii")


def create_svg_element(data, background_color, border_color, gradient_colors):
    bar_count = 84
    bars_html = "".join(["<div class='bar'></div>" for _ in range(bar_count)])
    bars_css = generate_bars_css(bar_count)

    if not "is_playing" in data:
        # contentBar = "" #Shows/Hides the EQ bar if no song is currently playing
        current_status = "Was playing:"
        recently_played = get(RECENTLY_PLAYING_URL)
        recently_played_count = len(recently_played["items"])
        item_index = random.randint(0, recently_played_count - 1)
        item = recently_played["items"][item_index]["track"]
    else:
        item = data["item"]
        current_status = "Vibing to:"

    is_album_images_array_empty = item["album"]["images"] == []
    if is_album_images_array_empty:
        image = PLACEHOLDER_IMAGE
        album_art_url = None
    else:
        album_art_url = item["album"]["images"][1]["url"]
        image = load_image_base64(album_art_url)

    artist_name = item["artists"][0]["name"].replace("&", "&amp;")
    song_name = item["name"].replace("&", "&amp;")
    song_uri = item["external_urls"]["spotify"]
    artist_uri = item["artists"][0]["external_urls"]["spotify"]

    svg_data = {
        "bars_html": bars_html,
        "bars_css": bars_css,
        "artist_name": artist_name,
        "song_name": song_name,
        "song_uri": song_uri,
        "artist_uri": artist_uri,
        "image": image,
        "status": current_status,
        "background_color": background_color,
        "border_color": border_color,
        "gradient_colors": gradient_colors
    }

    current_theme, template = get_template()
    if gradient_colors == "auto":
        theme_colors, gradient_colors = get_automatic_colors(
            current_theme, album_art_url)
        svg_data["background_color"] = theme_colors[0]
        svg_data["song_title_font_color"] = theme_colors[1]
        svg_data["song_artist_font_color"] = theme_colors[2]
        svg_data["border_color"] = theme_colors[3]
        svg_data["gradient_colors"] = gradient_colors
    return render_template(template, **svg_data)


def get_automatic_colors(current_theme, album_art_url):
    def get_average_brightness(color_list):
        brightness_list = []
        for color in color_list:
            r, g, b = int(color[1:3], 16), int(
                color[3:5], 16), int(color[5:7], 16)
            brightness = (r * 299 + g * 587 + b * 114) / 1000
            brightness_list.append(brightness)
        return sum(brightness_list) / len(brightness_list)

    def get_dominant_colors(album_art_url, num_colors=4):
        if not album_art_url:
            return DEFAULT_GRADIENT_COLORS
        response = requests.get(album_art_url)
        img = Image.open(BytesIO(response.content))
        colors = colorgram.extract(img, num_colors)
        return [f"#{c.rgb[0]:02x}{c.rgb[1]:02x}{c.rgb[2]:02x}" for c in colors]

    def get_theme_colors(threshold):
        if threshold:
            background_color = "#FFFFFF"
            song_title_font_color = "#666"
            song_artist_font_color = "#b3b3b3"
            border_color = "#181414"
        else:
            background_color = "#181414"
            song_title_font_color = "#f7f7f7"
            song_artist_font_color = "#9f9f9f"
            border_color = "#9f9f9f"
        return background_color, song_title_font_color, song_artist_font_color, border_color

    gradient_colors = get_dominant_colors(album_art_url)
    average_brightness = get_average_brightness(gradient_colors)
    theme_colors = get_theme_colors(
        average_brightness > 90 if current_theme == "light" else average_brightness < 90)
    return theme_colors, gradient_colors


@ app.route("/", defaults={"path": ""})
@ app.route("/<path:path>")
@ app.route('/with_parameters')
def catch_all(path):
    border_color = request.args.get('border_color', default=None)
    background_color = request.args.get('background_color') or "#181414"
    gradient_colors = request.args.get(
        'gradient_colors', default=DEFAULT_GRADIENT_COLORS)

    print(gradient_colors)
    try:
        data = get(NOW_PLAYING_URL)
    except Exception:
        data = get(RECENTLY_PLAYING_URL)

    svg_element = create_svg_element(data, background_color,
                                     border_color, gradient_colors)

    resp = Response(svg_element, mimetype="image/svg+xml")
    resp.headers["Cache-Control"] = "s-maxage=1"

    return resp


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=os.getenv("PORT") or 5000)
