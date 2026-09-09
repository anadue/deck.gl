const {chromium} = require('/opt/node22/lib/node_modules/playwright');
const G = /(googleapis|gstatic|google\.com|ggpht)/;
(async()=>{
  const b = await chromium.launch({executablePath:'/opt/pw-browsers/chromium', args:['--use-gl=swiftshader','--no-sandbox']});
  const p = await b.newPage({viewport:{width:1500,height:950}});
  await p.route('**/*', async route => {
    const url = route.request().url();
    if(!G.test(url)) return route.continue();
    try{
      const rq = route.request();
      const pd = rq.postDataBuffer();
      const init = pd ? {method:rq.method(), headers:{'content-type':rq.headers()['content-type']||'application/json','Referer':'https://localhost/'}, body:pd}
                      : {headers:{'Referer':'https://localhost/'}};
      const r = await fetch(url, init);
      const buf = Buffer.from(await r.arrayBuffer());
      const h = {}; r.headers.forEach((v,k)=>{ if(!/^content-(encoding|length)|^transfer-encoding/i.test(k)) h[k]=v; });
      await route.fulfill({status:r.status, headers:h, body:buf});
    }catch(e){ await route.abort(); }
  });
  const errs=[];
  p.on('pageerror',e=>errs.push('PAGEERROR '+e.message));
  p.on('console',m=>{ if(m.type()==='error' && !/Failed to load resource/.test(m.text())) errs.push('ERR '+m.text().slice(0,150)); });
  await p.goto('file://'+__dirname+'/oostende-trip-origins-destinations.html');
  await p.waitForFunction(()=>document.getElementById('loading').style.display==='none',{timeout:90000});
  await p.waitForTimeout(11000);
  const st = await p.evaluate(()=>({basemap:document.getElementById('basemap').value,
    note:document.getElementById('mapnote').hidden?null:document.getElementById('mapnote').innerText,
    gmapChildren:document.getElementById('gmap').children.length,
    attrib:document.getElementById('attrib').innerText, trips:document.querySelector('.kpi .v').textContent,
    gBoxShown:!document.getElementById('gBox').hidden}));
  console.log('INITIAL', JSON.stringify(st,null,1));
  await p.screenshot({path:'g_roadmap.png'});
  await p.selectOption('#basemap','g-hybrid'); await p.waitForTimeout(9000);
  await p.screenshot({path:'g_sat.png'});
  // hover tooltip over a busy cell
  await p.mouse.move(880,420); await p.waitForTimeout(1200);
  const tip = await p.evaluate(()=>document.getElementById('tip').hidden?null:document.getElementById('tip').innerText);
  // street view
  await p.check('#svMode'); await p.waitForTimeout(400);
  await p.mouse.click(880,420); await p.waitForTimeout(9000);
  const sv = await p.evaluate(()=>({panel:!document.getElementById('svpanel').hidden,
    note:document.getElementById('mapnote').hidden?null:document.getElementById('mapnote').innerText}));
  await p.screenshot({path:'g_sv.png'});
  // back to built-in
  await p.uncheck('#svMode');
  await p.selectOption('#basemap','offline'); await p.waitForTimeout(3500);
  const back = await p.evaluate(()=>({basemap:document.getElementById('basemap').value,
    mapShown:document.getElementById('map').style.display!=='none',
    trips:document.querySelector('.kpi .v').textContent}));
  console.log('TOOLTIP', JSON.stringify(tip));
  console.log('STREETVIEW', JSON.stringify(sv));
  console.log('BACK', JSON.stringify(back));
  console.log('ERRORS', JSON.stringify(errs.slice(0,6),null,1));
  await b.close();
})();
