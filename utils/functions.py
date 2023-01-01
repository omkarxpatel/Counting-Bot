import re
import string
import base64
import urllib
import discord
import datetime
from io import BytesIO
from datetime import datetime as dt
from datetime import timedelta
from PIL import Image, ImageDraw, ImageFont
from colorthief import ColorThief

class Spotify:
    __slots__ = ('member', 'bot', 'embed', 'regex', 'headers', 'counter')
    def __init__(self, *, bot, member) -> None:
        self.member = member
        self.bot = bot
        self.embed = discord.Embed(title=f"{member.display_name} is Listening to Spotify", color = discord.Color.green())
        self.regex = "(https\:\/\/open\.spotify\.com\/artist\/[a-zA-Z0-9]+)"
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}
        self.counter = 0

    async def request_pass(self, *, track_id: str):
        try:
            if not self.bot.spotify_session or dt.utcnow() > self.bot.spotify_session[1]:
                resp = await self.bot.session.post("https://accounts.spotify.com/api/token", params={"grant_type": "client_credentials"}, headers={"Authorization": f'Basic {base64.urlsafe_b64encode(f"{self.bot.spotify_client_id}:{self.bot.spotify_client_secret}".encode()).decode()}', "Content-Type": "application/x-www-form-urlencoded",},)
                auth_js = await resp.json()
                timenow = dt.utcnow() + timedelta(seconds=auth_js['expires_in'])
                type_token = auth_js['token_type']
                token = auth_js['access_token']
                auth_token = f"{type_token} {token}"
                self.bot.spotify_session = (auth_token, timenow)
                print('Generated new Token')

            else:
                auth_token = self.bot.spotify_session[0]
                print('Using previous token')

        except Exception:
            return False

        else:
            try:
                resp = await self.bot.session.get(f"https://api.spotify.com/v1/tracks/{urllib.parse.quote(track_id)}",
                        params={
                            "market": "US",
                        },
                        headers={
                            "Authorization": auth_token},
                )
                json = await resp.json()
                return json

            except Exception:
                if self.counter == 4:
                    return False

                else:
                    self.counter += 1
                    await self.request_pass(track_id=track_id)

    def PIL_process(self, pic, name, artists, time, time_at, track):
        s = ColorThief(pic)
        color = s.get_palette(color_count=2)
        result = Image.new('RGBA', (575, 170))
        draw = ImageDraw.Draw(result)
        color_font = "white" if sum(color[1]) < 450 else "black" 
        draw.rounded_rectangle(((0, 0), (575, 170)), 20, fill=color[1])
        s = Image.open(pic)
        s = s.resize((128, 128))
        result1 = Image.new('RGBA', (129, 128))
        Image.Image.paste(result, result1, (29, 23))
        Image.Image.paste(result, s, (27, 20))
        font = ImageFont.truetype(f"Assets/spotify.ttf", 28)
        font2 = ImageFont.truetype(f"Assets/spotify.ttf", 18)
        draw.text((170, 20), name, color_font,font=font)
        draw.text((170, 55), artists, color_font,font=font2)
        draw.text((500, 120), time, color_font,font=font2)
        draw.text((170, 120), time_at, color_font,font=font2)
        draw.rectangle(((230, 130), (490, 127)), fill="grey")
        draw.rectangle(((230, 130), (230 + track, 127)), fill=color_font)
        draw.ellipse((230 + track-5, 122, 230 + track+5, 134), fill = color_font, outline =color_font)
        output = BytesIO()
        result.save(output, "png")
        output.seek(0)
        return discord.File(fp=output, filename="spotify.png")

    async def get_from_local(self, bot, act: discord.Spotify):
        s = tuple(f"{string.ascii_letters}{string.digits}{string.punctuation} ")
        artists = ', '.join(act.artists)
        artists = ''.join([x for x in artists if x in s])
        time = act.duration.seconds
        time_at = (datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) - act.created_at).total_seconds()
        track = (time_at/time)*260
        time = f"{time//60:02d}:{time%60:02d}"
        time_at = f"{int((time_at if time_at > 0 else 0)//60):02d}:{int((time_at if time_at > 0 else 0)%60):02d}"
        pog = act.album_cover_url
        name = ''.join([x for x in act.album if x in s])
        name = name[0:21] + "..." if len(name) > 21 else name
        rad = await bot.session.get(pog)
        pic = BytesIO(await rad.read())
        
        return await bot.loop.run_in_executor(None, self.PIL_process, pic, name, artists, time, time_at, track)

    @staticmethod
    async def fetch_from_api(bot, activity: discord.Spotify):
        act = activity
        base_url = "https://api.jeyy.xyz/discord/spotify"
        params = {'title': act.album, 'cover_url': act.album_cover_url, 'artists': act.artists[0], 'duration_seconds': act.duration.seconds, 'start_timestamp': int(act.start.timestamp())}
        connection = await bot.session.get(base_url, params=params)
        buffer = BytesIO(await connection.read())
        return discord.File(fp=buffer, filename="spotify.png")


    async def send_backup_artist_request(self, activity):
        artists = activity.artists
        url = activity.track_url
        result = await self.bot.session.get(url, headers=self.headers)
        text = await result.text()
        my_list = re.findall(self.regex, text)
        final = sorted(set(my_list), key=my_list.index)
        total = len(artists)
        final_total = final[0:total]
        final_string = ', '.join([f"[{artists[final_total.index(x)]}]({x})" for x in final_total])
        return final_string
 

    async def get_embed(self):  
        activity = discord.utils.find(lambda activity: isinstance(activity, discord.Spotify), self.member.activities)
        if not activity:
            return False
        try:
            result = await self.request_pass(track_id=activity.track_id)
            final_string = ', '.join([f"[{resp['name']}]({resp['external_urls']['spotify']})" for resp in result['artists']])
        except Exception:
            final_string = await self.send_backup_artist_request(activity)
        url = activity.track_url
        image = await self.get_from_local(self.bot, activity)
        self.embed.description = f"**Artists**: {final_string}\n**Album**: [{activity.album}]({url})"
        self.embed.set_image(url="attachment://spotify.png")
        return self.embed, image