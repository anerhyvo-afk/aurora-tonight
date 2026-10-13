#!/usr/bin/env python3
"""Fetch real feeds and write data.json. Stdlib only."""
import json, math, re, urllib.request, datetime as dt
UA={"User-Agent":"aurora-tonight-prototype"}
def get(u):
    return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30).read().decode()
TOWNS=[("Rovaniemi","rovaniemi",66.50,25.73,"RAN"),("Levi","kittilä",67.80,24.81,"MUO"),("Saariselkä","inari",68.42,27.41,"IVA")]
def sun_elev(lat,lon,t):
    d=(t-dt.datetime(2000,1,1,12,tzinfo=dt.timezone.utc)).total_seconds()/86400
    g=math.radians((357.529+0.98560028*d)%360); q=(280.459+0.98564736*d)%360
    L=math.radians(q+1.915*math.sin(g)+0.020*math.sin(2*g)); e=math.radians(23.439-0.00000036*d)
    dec=math.asin(math.sin(e)*math.sin(L)); ra=math.atan2(math.cos(e)*math.sin(L),math.cos(L))
    gmst=(18.697374558+24.06570982441908*d)%24; ha=math.radians(gmst*15+lon)-ra
    la=math.radians(lat)
    return math.degrees(math.asin(math.sin(la)*math.sin(dec)+math.cos(la)*math.cos(dec)*math.cos(ha)))
def clouds(place):
    x=get("https://opendata.fmi.fi/wfs?service=WFS&version=2.0.0&request=getFeature&storedquery_id=fmi::forecast::harmonie::surface::point::simple&place="+urllib.parse.quote(place)+"&parameters=TotalCloudCover&timestep=60")
    t=re.findall(r"<BsWfs:Time>(.*?)</BsWfs:Time>",x); v=re.findall(r"<BsWfs:ParameterValue>(.*?)</BsWfs:ParameterValue>",x)
    return [(a,float(b)) for a,b in zip(t,v) if b!="NaN"]
import urllib.parse
now=dt.datetime.now(dt.timezone.utc)
r=json.loads(get("https://space.fmi.fi/MIRACLE/RWC/data/r_index_latest_en.json"))["data"]
kpf=json.loads(get("https://services.swpc.noaa.gov/products/noaa-planetary-k-index-forecast.json"))
kp_next=[k for k in kpf if k.get("observed")!="observed"][:3]
kp_max=max([k["kp"] for k in kp_next] or [0])
out={"updated":now.isoformat(timespec="minutes"),"kp_forecast_max_next9h":kp_max,"towns":[]}
for name,place,lat,lon,st in TOWNS:
    s=r[st]; R=s["R-index"]; lo,hi=s["Limit value lower"],s["Limit value higher"]
    activity=min(1,max(0,(R-0.5*lo)/(hi-0.5*lo)))          # 0..1 from live magnetometer
    activity=max(activity,min(1,(kp_max-2)/4)*0.7)           # Kp forecast floor
    cc=clouds(place); cloud=cc[0][1] if cc else 50
    elev=sun_elev(lat,lon,now); dark=1 if elev<-12 else (0.5 if elev<-6 else 0)
    score=round(100*activity*(1-cloud/100)*dark)
    verdict="Good" if score>=40 else "Possible" if score>=15 else "Unlikely"
    why=[]
    if dark==0: why.append("too bright")
    why.append(f"{int(cloud)}% cloud"); why.append(f"{s['Station']} activity {s['Probability of auroras'].split(' probability')[0].lower()} (R={R})")
    out["towns"].append(dict(name=name,verdict=verdict,score=score,reason=", ".join(why),cloud_next6h=cc[:6],station=s["Station"],r_index=R,sun_elev=round(elev,1)))
json.dump(out,open("data.json","w"),ensure_ascii=False,indent=1)
print(json.dumps({t["name"]:(t["verdict"],t["score"],t["reason"]) for t in out["towns"]},ensure_ascii=False),"Kp max",kp_max)
