const {chromium} = require('/opt/node22/lib/node_modules/playwright');
const G = /(googleapis|gstatic|google\.com|ggpht)/;
(async()=>{
  const b = await chromium.launch({executablePath:'/opt/pw-browsers/chromium', args:['--use-gl=swiftshader','--no-sandbox']});
  const p = await b.newPage({viewport:{width:1500,height:950}});
  await p.route('**/*', async route => {
    const url = route.request().url();
    if(!G.test(url)) return route.continue();
    try{
      const rq = route.request(); const pd = rq.postDataBuffer();
      const init = pd ? {method:rq.method(), headers:{'content-type':rq.headers()['content-type']||'application/json','Referer':'https://localhost/'}, body:pd}
                      : {headers:{'Referer':'https://localhost/'}};
      const r = await fetch(url, init);
      const buf = Buffer.from(await r.arrayBuffer());
      const h={}; r.headers.forEach((v,k)=>{ if(!/^content-(encoding|length)|^transfer-encoding/i.test(k)) h[k]=v; });
      await route.fulfill({status:r.status, headers:h, body:buf});
    }catch(e){ await route.abort(); }
  });
  const errs=[]; p.on('pageerror',e=>errs.push('PAGEERROR '+e.message));
  p.on('console',m=>{ if(m.type()==='error' && !/Failed to load resource|ApiProjectMapError/.test(m.text())) errs.push('ERR '+m.text().slice(0,140)); });
  await p.goto('file://'+__dirname+'/oostende-trip-origins-destinations.html');
  await p.waitForFunction(()=>document.getElementById('loading').style.display==='none',{timeout:90000});
  await p.waitForTimeout(11000);
  console.log('INITIAL', JSON.stringify(await p.evaluate(()=>({
    theme:document.body.dataset.theme, basemap:document.getElementById('basemap').value,
    themeBtn:document.getElementById('themeBtn').textContent,
    bodyBg:getComputedStyle(document.body).backgroundColor,
    note:document.getElementById('mapnote').hidden?null:document.getElementById('mapnote').innerText.slice(0,60),
    trips:document.querySelector('.kpi .v').textContent}))));
  await p.screenshot({path:'light1.png'});
  // built-in basemap in light theme
  await p.selectOption('#basemap','offline'); await p.waitForTimeout(3500);
  await p.screenshot({path:'light_offline.png'});
  // satellite in light theme
  await p.selectOption('#basemap','g-satellite'); await p.waitForTimeout(9000);
  await p.screenshot({path:'light_sat.png'});
  // dark toggle
  await p.click('#themeBtn'); await p.waitForTimeout(4000);
  console.log('AFTER TOGGLE', JSON.stringify(await p.evaluate(()=>({
    theme:document.body.dataset.theme, basemap:document.getElementById('basemap').value,
    themeBtn:document.getElementById('themeBtn').textContent}))));
  await p.screenshot({path:'dark_after.png'});
  await p.click('#themeBtn'); await p.waitForTimeout(4000);
  console.log('BACK TO LIGHT', JSON.stringify(await p.evaluate(()=>({
    theme:document.body.dataset.theme, basemap:document.getElementById('basemap').value,
    trips:document.querySelector('.kpi .v').textContent}))));
  console.log('ERRORS', JSON.stringify(errs.slice(0,5),null,1));
  await b.close();
})();
