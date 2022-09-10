import os

from flask import Flask, Response, request, redirect

from .auth import SpotifyClient
from .login import getLoginUrl
from .render import SvgRenderer
from .constants import NOW_PLAYING_URL, RECENTLY_PLAYING_URL
from .exceptions import EmptyResponse

app = Flask(__name__)

spotify = SpotifyClient()
svg_renderer = SvgRenderer()


@app.route('/callback/', methods=["GET"])
@app.route('/with_parameters')
def spotify_WebAPI_callback():
    global spotify
    code = request.args.get('code')
    spotify.authenticate(code)
    return redirect("/")


@app.route("/", defaults={"path": ""})
@app.route('/with_parameters')
def catch_all(path):
    global spotify, svg_renderer
    access_token = spotify.getAccessToken()
    refresh_token = spotify.getRefreshToken()
    print(
        f"[+] Access token: {access_token} and Refresh token: {refresh_token}")
    if (access_token and refresh_token):
        background_color = request.args.get('background_color') or "181414"
        border_color = request.args.get('border_color') or "181414"

        try:
            data = spotify.get(NOW_PLAYING_URL)
        except EmptyResponse:
            data = spotify.get(RECENTLY_PLAYING_URL)

        svg = svg_renderer.renderSVG(data, background_color, border_color)

        response = Response(svg, mimetype="image/svg+xml")
        response.headers["Cache-Control"] = "s-maxage=1"
        return response
    else:
        login_url = getLoginUrl()
        svg = svg_renderer.renderLoginSVG(login_url=login_url)
        response = Response(svg, mimetype="image/svg+xml")
        response.headers["Cache-Control"] = "s-maxage=1"
        return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=os.getenv("FLASK_ENV")
            == "development", port=os.getenv("PORT") or 80)
