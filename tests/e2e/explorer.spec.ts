import {test,expect} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import {mkdirSync} from 'node:fs';
const pages=[['/','Ontario Hospital Quality Improvement Explorer'],['/interventions/','Intervention Explorer'],['/hospitals/','Hospital Explorer'],['/current-plans/','Current 2026/27 Plans'],['/reporting-quality/','Reporting & Data Quality'],['/methodology/','Methodology']];
for(const width of [1440,1024,390]){
 test(`all pages are usable at ${width}px`,async({page})=>{
  await page.setViewportSize({width,height:1000});const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error'||m.type()==='warning')errors.push(m.text())});
  for(const [path,title] of pages){
   await page.goto(path);await expect(page.getByRole('heading',{name:title,exact:true,level:1})).toBeVisible();await expect(page.locator('nav a[aria-current="page"]')).toHaveCount(1);
   if(path!=='/methodology/')await expect(page.getByRole('combobox',{name:'Fiscal year',exact:true})).toBeVisible();else await expect(page.getByRole('heading',{name:'Phase 2 methodology',exact:true})).toBeVisible();
   expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);
   if(path==='/'){
    await expect(page.getByText('488',{exact:true})).toBeVisible();await expect(page.getByText('429',{exact:true})).toBeVisible();
    await expect(page.locator('.recharts-wrapper').first()).toBeVisible();
    await page.locator('.recharts-bar-rectangle path').first().hover();await expect(page.locator('.recharts-tooltip-wrapper').first()).toBeVisible();await expect(page.locator('.recharts-tooltip-wrapper').first()).toContainText('initiatives');await page.mouse.move(0,0);
    await page.getByRole('button',{name:'About Hospitals represented',exact:true}).hover();await expect(page.getByRole('tooltip')).toContainText('Reporting organizations');await page.mouse.move(0,0);await page.keyboard.press('Escape');await expect(page.getByRole('tooltip')).toHaveCount(0);
    mkdirSync('docs/screenshots',{recursive:true});await page.screenshot({path:`docs/screenshots/${width===1440?'desktop':width===390?'mobile':'tablet'}.png`,fullPage:true});
   }
   if(path==='/interventions/'){
    const scroll=page.locator('div.overflow-x-auto').first();expect(await scroll.evaluate(e=>e.scrollWidth>e.clientWidth)).toBe(true);
    await page.getByRole('button',{name:/View source details for/}).first().click();await expect(page.getByRole('dialog')).toBeVisible();await expect(page.getByRole('heading',{name:'Source records & submitted values'})).toBeVisible();await expect(page.getByRole('dialog')).toContainText('Reporting periods have not been verified');await page.getByRole('button',{name:'Close details'}).click();
   }
   if(path==='/hospitals/'){await expect(page.getByRole('heading',{name:'Reporting timeline'})).toBeVisible();await page.locator('main section button').first().click();await expect(page.getByRole('heading',{name:'Source records & submitted values'})).toBeVisible();await page.getByRole('button',{name:'Close details'}).click();}
   const violations=(await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa']).analyze()).violations;
   expect(violations.map(v=>`${v.id}: ${v.nodes.map(n=>n.target).join(',')}`)).toEqual([]);
  }
  expect(errors).toEqual([]);
 });
}
test('filters, drill-down, empty states, table controls and export',async({page})=>{
 await page.goto('/');await page.getByRole('combobox',{name:'Region',exact:true}).selectOption('East Region');await page.getByRole('combobox',{name:'Fiscal year',exact:true}).selectOption('2025/26');
 await page.getByRole('link',{name:'Intervention Explorer',exact:true}).click();await expect(page.getByRole('combobox',{name:'Region',exact:true})).toHaveValue('East Region');
 await page.getByLabel('Search interventions').fill('no-such-hospital-xyz');await expect(page.getByText('No interventions match the current filters and search.')).toBeVisible();
 await page.getByLabel('Search interventions').fill('');await page.getByRole('button',{name:'Next',exact:true}).click();await expect(page.getByText(/Page 2 of/)).toBeVisible();await page.getByRole('button',{name:'Previous',exact:true}).click();await page.getByRole('button',{name:'Columns',exact:true}).click();await page.getByRole('menuitemcheckbox',{name:'Change idea',exact:true}).click();await page.keyboard.press('Escape');await expect(page.getByRole('columnheader',{name:'Change idea',exact:true})).toHaveCount(0);
 await page.getByRole('button',{name:'Hospital',exact:true}).click();await expect(page.locator('th[aria-sort="ascending"]')).toContainText('Hospital');
 const downloaded=page.waitForEvent('download');await page.getByRole('button',{name:'Export CSV'}).click();expect((await downloaded).suggestedFilename()).toBe('interventions.csv');
 await page.getByRole('link',{name:'Current Plans',exact:true}).click();await expect(page.getByText('No initiatives match the selected filters.').first()).toBeVisible();await page.getByRole('button',{name:'Reset filters'}).click();await expect(page.getByText('429 selected initiatives',{exact:false})).toBeVisible();
 await page.getByRole('link',{name:'Overview',exact:true}).click();await expect(page.getByRole('heading',{name:'Ontario Hospital Quality Improvement Explorer',level:1})).toBeVisible();await page.getByRole('combobox',{name:'Implementation status',exact:true}).selectOption('Current plan');await expect(page.getByRole('paragraph').filter({hasText:/^Unavailable$/})).toBeVisible();
 await page.getByRole('button',{name:'Reset filters'}).click();await page.locator('summary').filter({hasText:'View exact counts and explore records'}).first().click();await page.locator('details[open] table button').first().click();await expect(page).toHaveURL(/interventions/);await expect(page.getByRole('combobox',{name:'Intervention category',exact:true})).not.toHaveValue('');
});
test('loading, retry and unavailable source states',async({page})=>{
 await page.route('**/data/explorer.json',route=>route.fulfill({status:503,body:'Unavailable'}));await page.goto('/');await expect(page.getByRole('heading',{name:'Data unavailable'})).toBeVisible();await page.unroute('**/data/explorer.json');await page.getByRole('button',{name:'Try again'}).click();await expect(page.getByRole('combobox',{name:'Region',exact:true})).toBeVisible();
 await page.goto('/interventions/');await page.route('**/data/details/*.json',route=>route.fulfill({status:503,body:'Unavailable'}));await page.getByRole('button',{name:/View source details for/}).first().click();await expect(page.getByRole('dialog').getByRole('alert')).toBeVisible();await page.unroute('**/data/details/*.json');await page.getByRole('button',{name:'Retry source details'}).click();await expect(page.getByRole('heading',{name:'Source records & submitted values'})).toBeVisible();
});
test('guided tour persists, reopens, and assistant guards scope',async({page})=>{
 await page.addInitScript(()=>{if(!sessionStorage.getItem('clear-tour-state')){localStorage.clear();sessionStorage.setItem('clear-tour-state','true');}});
 await page.goto('/');
 await expect(page.getByLabel('Dashboard tour')).toBeVisible();
 await page.getByRole('button',{name:'Take a quick tour',exact:true}).click();
 const tourTitles=['What is this?','Narrow the data','Understand the summary','Explore improvement activity','Know what cannot be concluded'];
 for(const title of tourTitles){await expect(page.getByRole('dialog').getByRole('heading',{name:title,exact:true})).toBeVisible();if(title!==tourTitles.at(-1))await page.getByRole('button',{name:'Next',exact:true}).click();}
 await page.getByRole('button',{name:'Start exploring',exact:true}).click();
 await expect(page.evaluate(()=>localStorage.getItem('tourCompleted'))).resolves.toBe('true');
 await page.reload();await expect(page.getByLabel('Dashboard tour')).toHaveCount(0);
 await page.getByRole('button',{name:'Take a quick tour',exact:true}).click();await expect(page.getByRole('dialog').getByRole('heading',{name:'What is this?'})).toBeVisible();await page.keyboard.press('Escape');
 const medical=await page.evaluate(async()=>{const response=await fetch('/api/assistant',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:'Should I go to Humber River or Sunnybrook for chest pain?',history:[]})});return response.json();});
 expect(medical.answer).toContain('not a medical decision tool');
 await page.route('**/api/assistant',route=>route.fulfill({contentType:'application/json',body:JSON.stringify({answer:'This is a short project explanation.'})}));
 await page.getByRole('button',{name:'Ask about the data',exact:true}).click();await page.getByRole('button',{name:'What is this project?',exact:true}).click();await expect(page.getByText('This is a short project explanation.')).toBeVisible();await page.getByRole('button',{name:'Clear chat',exact:true}).click();await expect(page.getByText('Try a project question:')).toBeVisible();
});
