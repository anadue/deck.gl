import json, os, csv, datetime
from zoneinfo import ZoneInfo

TR="/root/.claude/projects/-home-user-deck-gl/0fb8e274-00dc-5566-a0f5-75cd3d31804a/tool-results/"
FILES=["mcp-PathFinder_Hoppy-pathfinder_run_sql-%s.txt"%s for s in
 ["1788962943007","1788962946575","1788962949772","1788962952876","1788962963668","1788962966836","1788962969671"]]

TZ=ZoneInfo("Europe/Brussels")
# ~250 m square cells at 51.23N: 1 deg lat = 111.2 km, 1 deg lon = 69.7 km
LAT_STEP=0.00225
LON_STEP=0.00359

rows=[]
seen=set()
for f in FILES:
    d=json.load(open(TR+f))
    assert d["truncated"] is False, f
    for r in d["data"]:
        for line in r["lines"].split(";"):
            p=line.split(",")
            assert len(p)==12, line
            rid=p[0]
            if rid in seen:  # guard against overlap
                continue
            seen.add(rid)
            rows.append(p)

print("trips parsed:", len(rows))
rows.sort(key=lambda p: int(p[1]))

def cell(lat, lon):
    r=int(round(lat/LAT_STEP)); c=int(round(lon/LON_STEP))
    return "R%dC%d"%(r,c), round(r*LAT_STEP,6), round(c*LON_STEP,6)

out="/tmp/claude-0/-home-user-deck-gl/0fb8e274-00dc-5566-a0f5-75cd3d31804a/scratchpad/work/oostende_trips.csv"
w=csv.writer(open(out,"w",newline=""))
w.writerow(["rental_id","start_epoch","end_epoch","start_local","end_local","date_local","hour_local","weekday",
            "start_lat","start_lon","end_lat","end_lon","distance_m","duration_s","duration_min",
            "start_cell_id","start_cell_lat","start_cell_lon","end_cell_id","end_cell_lat","end_cell_lon",
            "customer_id","vehicle_id","price_eur"])
WD=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
stats={"minst":None,"maxst":None,"dist":0,"dur":0,"nodur":0}
for p in rows:
    rid,st,et,slat,slon,elat,elon,dist,dur,cust,veh,price=p
    st=int(st); et=int(et) if et else None
    ls=datetime.datetime.fromtimestamp(st,TZ)
    le=datetime.datetime.fromtimestamp(et,TZ) if et else None
    sc=cell(float(slat),float(slon)); ec=cell(float(elat),float(elon))
    dur_i=int(dur) if dur else 0
    dist_i=int(dist) if dist else 0
    stats["dist"]+=dist_i; stats["dur"]+=dur_i
    stats["minst"]=st if stats["minst"] is None else min(stats["minst"],st)
    stats["maxst"]=st if stats["maxst"] is None else max(stats["maxst"],st)
    w.writerow([rid,st,et if et else "",ls.strftime("%Y-%m-%d %H:%M:%S"),
                le.strftime("%Y-%m-%d %H:%M:%S") if le else "",
                ls.strftime("%Y-%m-%d"),ls.hour,WD[ls.weekday()],
                slat,slon,elat,elon,dist_i,dur_i,round(dur_i/60,1),
                sc[0],sc[1],sc[2],ec[0],ec[1],ec[2],cust,veh,price])
print("csv rows:", len(rows), "->", out)
print("span:", datetime.datetime.fromtimestamp(stats["minst"],TZ), "->", datetime.datetime.fromtimestamp(stats["maxst"],TZ))
print("total km:", round(stats["dist"]/1000), "avg dur min:", round(stats["dur"]/len(rows)/60,1))
