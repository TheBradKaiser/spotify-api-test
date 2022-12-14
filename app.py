from flask import Flask,redirect,request, session
import secret as s
import requests

#secrets file has clientID, clientSecret, and b64 ("id:secret" b64 encoded.)

app = Flask(__name__)
redirect_uri='http://localhost:5000/callback'
redirect_uri2='http://localhost:5000/done'
authUrlBase="https://accounts.spotify.com/authorize?"
authCodeUrlBase="https://accounts.spotify.com/api/token"
app.config["SECRET_KEY"]="zzzzzzzzzasdfjajfjiowqjrowqnhnfhuwq128u459128*&(Y^yh321h5iu21"
apiUrl="https://api.spotify.com/v1"
@app.before_first_request
def firstFunct():
    pass



@app.route('/')
def hello():
    #if user doesnt have permission then redirect to the spotify auth page
    #lets just do that every time.
    state = "asdfjkl"
    scope = 'user-read-private user-read-email user-read-recently-played user-top-read user-library-read app-remote-control streaming user-modify-playback-state user-read-playback-state'
    return redirect(authUrlBase+
    'client_id='+s.clientId+
    '&scope='+scope+
    '&redirect_uri='+redirect_uri+
    "&response_type=code"+
    "&state="+state
    )
@app.route('/callback')
def callback():
    code = request.args["code"]
    state = request.args["state"]
    headers = {"Authorization": "Basic "+s.b64}
    payload = {"code":code,
    "redirect_uri":redirect_uri,
    "grant_type": "authorization_code"
    }
    res = requests.post(authCodeUrlBase,headers=headers,data=payload)
    print(res.content)
    session["access_token"] = res.json()["access_token"]
    session["refresh_token"] = res.json()["refresh_token"]
    
    print(session)


    return redirect("/done")

@app.route('/done')
def done():
    headers = {"Authorization":"Bearer "+session["access_token"],
                "Content-Type":"application/json"}
    params = {"limit":50,"time_range":"long_term"}
    res = requests.get(apiUrl+"/me/top/tracks", headers=headers,params=params)
    #print(res)
    #print(res.headers)
    songArtistList=[]
    tmpArtist=""
    for i in res.json()["items"]:
        tmpAlbum = i["album"]["name"]
        tmpTrack = i["name"]
        tmpArtist=""
        tmpPop = i["popularity"]
        for j in i["artists"]:
            if tmpArtist !="":
                tmpArtist +=", "+ j["name"]
            else:
                tmpArtist=j["name"]
        artistSongString = tmpArtist+" - "+tmpAlbum+" - <b>"+tmpTrack+" - "+str(tmpPop)+"</b>"
        songArtistList.append(artistSongString)
    returnString="Arists - Album - <b>Track</b> - Artist Popularity (0-100)<br>"
    i = 1
    for a in songArtistList:
        returnString+=str(i)+". "+a+"<br>"
        i+=1
    print(returnString)

    headers = {"Authorization":"Bearer "+session["access_token"],
                "Content-Type":"application/json"}
    params = {"limit":50,"time_range":"long_term"}

    more = True
    songArtistList=[]
    nextUrl = apiUrl+"/me/player/recently-played"
    while more == True:


        res = requests.get(nextUrl, headers=headers,params=params)
        print(str(res.json()))
        #print(res.content)
        for i in res.json()["items"]:
            #print(str(i))
            tmpAlbum = i["track"]["album"]["name"]
            tmpTrack = i["track"]["name"]
            tmpArtist=""
            tmpPop = i["track"]["popularity"]
            tmpPlayTime=i["played_at"]
            for j in i["track"]["artists"]:
                if tmpArtist !="":
                    tmpArtist +=", "+ j["name"]
                else:
                    tmpArtist=j["name"]
            artistSongString = str(tmpPlayTime)+" - "+tmpArtist+" - "+tmpAlbum+" - <b>"+tmpTrack+" - "+str(tmpPop)+"</b><br>"
            songArtistList.append(artistSongString)
        if res.json()["next"] is None:
            more = False
        else:
            nextUrl = res.json()["next"]

    recentlyPlayed="<br>Recently Played Songs<br>"
    for i in songArtistList:
        recentlyPlayed+=i
    returnString+=recentlyPlayed

    body = {"position_ms":0,"uris":["spotify:track:4cOdK2wGLETKBW3PvgPWqT"]}
    userData = requests.get(apiUrl+"/me/player/devices",headers=headers)
    print(str(userData.json()))
    deviceId = userData.json()["devices"][0]["id"]
    print(deviceId)


    result = requests.put("https://api.spotify.com/v1/me/player/play?device_id="+deviceId,headers=headers,json=body)
    print(result.text)


    return str(returnString)


