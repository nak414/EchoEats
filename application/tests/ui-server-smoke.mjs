// Render and navigation smoke tests for the server-backed frontend (without browser dependencies).
import assert from 'node:assert/strict';
const map=new Map();
globalThis.localStorage={getItem:k=>map.get(k)??null,setItem:(k,v)=>map.set(k,String(v)),removeItem:k=>map.delete(k)};
const app={innerHTML:''};
const listeners={};
let user=null;
const food={id:'food-1',name:'Almond Croissant Box',description:'Fresh food',category:'Bakery',dietary:'Vegetarian',emoji:'🥐',vendor_id:'vendor-1',quantity:5,original_price:4.5,initial_price:3,min_price:1.5,current_price:2.7,pickup_deadline:new Date(Date.now()+3600000).toISOString(),expires_at:new Date(Date.now()+7200000).toISOString(),created_at:new Date().toISOString(),active:true};
const vendor={id:'vendor-1',role:'vendor',name:'Maya',email:'vendor@echoeats.test',vendor_name:'Green Oven Bakery',address:'Adliya, Bahrain'};
const consumer={id:'consumer-1',role:'consumer',name:'Demo Customer',email:'consumer@echoeats.test'};
const json=x=>({ok:true,status:200,json:async()=>x});
globalThis.FormData=class {constructor(form){this.form=form;}entries(){return Object.entries(this.form.values||{});}};
globalThis.fetch=async (url,opts)=> {
  if(url==='/api/session')return json(user);
  if(url==='/api/snapshot')return json({listings:[food],profiles:[vendor],reservations:[]});
  if(url==='/api/auth/login'){user=JSON.parse(opts.body).email.startsWith('vendor')?vendor:consumer;return json({session:user});}
  return json({ok:true});
};
globalThis.document={
  body:{classList:{toggle(){}}},
  querySelector:sel=>sel==='#app'?app:null,
  querySelectorAll:()=>[],
  addEventListener:(name,fn)=>listeners[name]=fn,
  activeElement:{tagName:'DIV'},
};
globalThis.window={scrollTo(){}};
globalThis.setInterval=()=>0;
globalThis.confirm=()=>true;
const wait=()=>new Promise(resolve=>setTimeout(resolve,35));
await import('../src/app.js');await wait();
assert.match(app.innerHTML,/Today's good deals/);
assert.match(app.innerHTML,/Almond Croissant Box/);
assert.match(app.innerHTML,/Log in \/ Sign up/);
async function click(action,extra={}){
  const el={dataset:{action,...extra}};
  await listeners.click({target:{closest:sel=>sel==='[data-action]'?el:null}});
  await wait();
}
await click('details',{id:'food-1'});assert.match(app.innerHTML,/Reserve for 15 minutes/);
await click('open-auth');assert.match(app.innerHTML,/Welcome back/);
await click('auth-tab',{tab:'signup'});assert.match(app.innerHTML,/Create your account/);
// Log in using the same form event handler used by the real frontend.
await click('auth-tab',{tab:'login'});
await listeners.submit({preventDefault(){},target:{id:'auth-form',values:{email:'vendor@echoeats.test',password:'Demo12345!'}}});await wait();
assert.match(app.innerHTML,/My food listings/);
await click('add-listing');assert.match(app.innerHTML,/Price reduction curve/);
await click('navigate',{page:'orders'});assert.match(app.innerHTML,/Customer orders/);
await click('navigate',{page:'tasks'});assert.match(app.innerHTML,/Preparation checklist/);
await click('navigate',{page:'profile'});assert.match(app.innerHTML,/Account details/);
console.log('PASS server UI smoke: home, details, signup, vendor, listing form, orders, tasks, profile');
