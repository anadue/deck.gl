const {chromium} = require('/opt/node22/lib/node_modules/playwright') ;
(async()=>{
  const b = await chromium.launch({executablePath:'/opt/pw-browsers/chromium', args:['--use-gl=swiftshader','--no-sandbox']});
  const p = await b.newPage({viewport:{width:1600,height:1000}});
  const errs=[];
  p.on('console', m=>{ if(m.type()==='error') errs.push(m.text()); });
  p.on('pageerror', e=>errs.push('PAGEERROR: '+e.message));
  await p.goto('file://'+__dirname+'/oostende-trip-origins-destinations.html');
  await p.waitForFunction(()=>document.getElementById('loading').style.display==='none' || document.getElementById('loading').innerText.includes('Could not'), {timeout:90000});
  await p.waitForTimeout(6000);
  const info = await p.evaluate(()=>({
    loading:document.getElementById('loading').innerText,
    subtitle:document.getElementById('subtitle').textContent,
    kpis:[...document.querySelectorAll('.kpi')].map(k=>k.querySelector('.l').textContent+': '+k.querySelector('.v').textContent),
    flows:document.getElementById('topFlow').innerText,
    starts:document.getElementById('topStart').innerText,
    ends:document.getElementById('topEnd').innerText,
    dayTitle:document.getElementById('dayTitle').textContent
  }));
  console.log(JSON.stringify(info,null,1));
  await p.screenshot({path:'shot1.png'});
  // exercise filters: end cells on, hour preset evening, weekend, 500m cells
  await p.click('#lEnd'); await p.click('[data-h="16,19"]'); await p.click('#weOnly');
  await p.selectOption('#cellSize','500'); await p.waitForTimeout(2500);
  const info2 = await p.evaluate(()=>({kpis:[...document.querySelectorAll('.kpi')].map(k=>k.querySelector('.l').textContent+': '+k.querySelector('.v').textContent), flows:document.getElementById('topFlow').innerText}));
  console.log('AFTER FILTERS', JSON.stringify(info2,null,1));
  await p.screenshot({path:'shot2.png'});
  // click a top start cell row to test cell filtering
  await p.click('#topStart tr:first-child'); await p.waitForTimeout(1800);
  const info3 = await p.evaluate(()=>({sel:document.getElementById('selCells').innerText, trips:document.querySelector('.kpi .v').textContent}));
  console.log('AFTER CELL CLICK', JSON.stringify(info3));
  await p.screenshot({path:'shot3.png'});
  console.log('CONSOLE ERRORS:', JSON.stringify(errs.slice(0,12),null,1));
  await b.close();
})();
