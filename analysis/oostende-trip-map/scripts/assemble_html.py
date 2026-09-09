import json, re
W="/tmp/claude-0/-home-user-deck-gl/0fb8e274-00dc-5566-a0f5-75cd3d31804a/scratchpad/work/"
S="/root/.claude/skills/synced/733c5184-4b1c-4703-8ddc-b8997588abb3_26eefff1-93e9-4400-9c34-f1bcf18cff98/anadue-territory-trip-map/assets/"
def logo(p, h):
    s=open(S+p).read()
    s=re.sub(r'<\?xml[^>]*\?>','',s)
    s=re.sub(r'<!--.*?-->','',s,flags=re.S)
    s=re.sub(r'\s(width|height)="[^"]*"','',s,count=2)
    s=s.replace('<svg','<svg style="height:%dpx;width:auto;display:block"'%h,1)
    return s.strip()
html=open(W+"template.html").read()
html=html.replace("__HOPPY_LOGO__",logo("hoppy_logo.svg",30))
html=html.replace("__ANADUE_LOGO__",logo("anadue_logo.svg",18))
html=html.replace("__DECKGL__",open(W+"package/dist.min.js").read().replace("</script","<\\/script"))
html=html.replace("__LANDMARKS__",open(W+"landmarks.json").read().strip())
html=html.replace("__META__",open(W+"meta.json").read().strip())
html=html.replace("__PAYLOAD__",open(W+"payload.b64").read().strip())
out=W+"oostende-trip-origins-destinations.html"
open(out,"w").write(html)
print(out, round(len(html)/1e6,2),"MB")
