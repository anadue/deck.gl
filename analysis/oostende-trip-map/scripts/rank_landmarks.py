import json, csv, math
W="/tmp/claude-0/-home-user-deck-gl/0fb8e274-00dc-5566-a0f5-75cd3d31804a/scratchpad/work/"
LM=json.load(open(W+"landmarks.json"))
# 1. weight each landmark by trips starting/ending within 350 m
w=[0]*len(LM)
R=350.0
for row in csv.DictReader(open(W+"oostende_trips.csv")):
    for la,lo in ((float(row["start_lat"]),float(row["start_lon"])),
                  (float(row["end_lat"]),float(row["end_lon"]))):
        best,bd=-1,R*R
        for i,(n,mla,mlo) in enumerate(LM):
            dy=(la-mla)*111200; dx=(lo-mlo)*69700
            d=dy*dy+dx*dx
            if d<bd: bd,best=d,i
        if best>=0: w[best]+=1
order=sorted(range(len(LM)), key=lambda i:-w[i])

# 2. greedy zoom tiers: a label appears at the lowest zoom where it clears
#    every higher-ranked label already shown, by ~62 px
ZOOMS=[12.0,12.5,13.0,13.5,14.0,14.5,15.0,15.5,16.0]
SEP=62.0
minz=[ZOOMS[-1]]*len(LM)
for z in ZOOMS:
    mpp = 156543.03*math.cos(math.radians(51.23))/(2**z)   # metres per pixel
    shown=[]
    for i in order:
        la,lo = LM[i][1], LM[i][2]
        ok=True
        for j in shown:
            dy=(la-LM[j][1])*111200; dx=(lo-LM[j][2])*69700
            if math.hypot(dy,dx)/mpp < SEP: ok=False; break
        if ok:
            shown.append(i)
            if minz[i]>z: minz[i]=z
out=[[LM[i][0], LM[i][1], LM[i][2], minz[i], w[i]] for i in range(len(LM))]
json.dump(out, open(W+"landmarks.json","w"), ensure_ascii=False)
tiers={}
for o in out: tiers[o[3]]=tiers.get(o[3],0)+1
print("labels per zoom tier:", dict(sorted(tiers.items())))
print("busiest:", [(o[0],o[4]) for o in sorted(out,key=lambda o:-o[4])[:6]])
