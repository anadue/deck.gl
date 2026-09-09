import json, os
TR="/root/.claude/projects/-home-user-deck-gl/0fb8e274-00dc-5566-a0f5-75cd3d31804a/tool-results/"
FILES={"Oostende":"mcp-SuperFlexMap_MCP-get_area_polygons-1788965353754.txt",
       "Middelkerke":"mcp-SuperFlexMap_MCP-get_area_polygons-1788965372633.txt",
       "Bredene":"mcp-SuperFlexMap_MCP-get_area_polygons-1788965393586.txt"}

def load(f):
    d=json.load(open(TR+f))
    r=d["result"] if isinstance(d,dict) and "result" in d else d
    return json.loads(r) if isinstance(r,str) else r

def perp(p,a,b):
    (x,y),(x1,y1),(x2,y2)=p,a,b
    dx,dy=x2-x1,y2-y1
    if dx==0 and dy==0: return ((x-x1)**2+(y-y1)**2)**.5
    t=max(0,min(1,((x-x1)*dx+(y-y1)*dy)/(dx*dx+dy*dy)))
    return ((x-(x1+t*dx))**2+(y-(y1+t*dy))**2)**.5

def dp(pts,tol):
    if len(pts)<3: return pts
    dmax,idx=0,0
    for i in range(1,len(pts)-1):
        d=perp(pts[i],pts[0],pts[-1])
        if d>dmax: dmax,idx=d,i
    if dmax>tol:
        return dp(pts[:idx+1],tol)[:-1]+dp(pts[idx:],tol)
    return [pts[0],pts[-1]]

TOL=8e-5
out=[]
bbox=[999,999,-999,-999]
for city,f in FILES.items():
    fc=load(f)
    for feat in fc["features"]:
        g=feat["geometry"]
        polys = g["coordinates"] if g["type"]=="MultiPolygon" else [g["coordinates"]]
        for poly in polys:
            ring=poly[0]
            s=dp([tuple(p) for p in ring], TOL)
            if len(s)<4: continue
            r=[[round(x,5),round(y,5)] for x,y in s]
            # drop consecutive duplicates
            r=[p for i,p in enumerate(r) if i==0 or p!=r[i-1]]
            if len(r)<4: continue
            for x,y in r:
                bbox[0]=min(bbox[0],x); bbox[1]=min(bbox[1],y)
                bbox[2]=max(bbox[2],x); bbox[3]=max(bbox[3],y)
            out.append({"c":city,"r":r})
print("polygons",len(out),"points",sum(len(p["r"]) for p in out))
print("bbox",bbox)
js=json.dumps(out,separators=(",",":"))
open("basemap.json","w").write(js)
print("size kb",round(len(js)/1024,1))
