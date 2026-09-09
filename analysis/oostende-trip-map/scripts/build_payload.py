import csv, gzip, base64, json, struct, datetime
from zoneinfo import ZoneInfo
W="/tmp/claude-0/-home-user-deck-gl/0fb8e274-00dc-5566-a0f5-75cd3d31804a/scratchpad/work/"
TZ=ZoneInfo("Europe/Brussels")
rows=list(csv.DictReader(open(W+"oostende_trips.csv")))
rows.sort(key=lambda r:int(r["start_epoch"]))
n=len(rows)
base_date=datetime.date.fromisoformat(rows[0]["date_local"])
st=[];dur=[];dist=[];slat=[];slon=[];elat=[];elon=[];day=[];lmin=[];dow=[]
WD={"Mon":0,"Tue":1,"Wed":2,"Thu":3,"Fri":4,"Sat":5,"Sun":6}
for r in rows:
    st.append(int(r["start_epoch"])); dur.append(min(int(r["duration_s"]),86400)); dist.append(int(r["distance_m"]))
    slat.append(round(float(r["start_lat"])*1e5)); slon.append(round(float(r["start_lon"])*1e5))
    elat.append(round(float(r["end_lat"])*1e5));   elon.append(round(float(r["end_lon"])*1e5))
    day.append((datetime.date.fromisoformat(r["date_local"])-base_date).days)
    hh,mm,ss=r["start_local"].split(" ")[1].split(":")
    lmin.append(int(hh)*60+int(mm)); dow.append(WD[r["weekday"]])
def pack(arr,fmt):  # delta-encode monotone int32 for compression
    return struct.pack("<%d%s"%(len(arr),fmt),*arr)
buf=b"".join([
    pack([st[0]]+[st[i]-st[i-1] for i in range(1,n)],"i"),
    pack(dur,"i"), pack(dist,"i"),
    pack(slat,"i"), pack(slon,"i"), pack(elat,"i"), pack(elon,"i"),
    pack(day,"H"), pack(lmin,"H"), pack(dow,"B"),
])
gz=gzip.compress(buf,9)
b64=base64.b64encode(gz).decode()
meta={"n":n,"base_date":base_date.isoformat(),
      "last_date":rows[-1]["date_local"],
      "tz":"Europe/Brussels","raw_bytes":len(buf),"gz_bytes":len(gz)}
open(W+"payload.b64","w").write(b64)
open(W+"meta.json","w").write(json.dumps(meta))
print(meta, "b64 chars", len(b64))
