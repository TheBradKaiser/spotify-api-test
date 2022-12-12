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
    scope = 'user-read-private user-read-email user-read-recently-played user-top-read user-library-read'
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
    print(res)
    print(res.headers)
    songArtistList=[]
    tmpArtist=""
    trackIds=[]
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
    returnString="Arists - Album - <b>Track</b> - Artist Popularity (0-100)<br> "
    i = 1
    for a in songArtistList:
        returnString+=str(i)+". "+a+"<br>"
        i+=1
    print(returnString)
    return str(returnString)