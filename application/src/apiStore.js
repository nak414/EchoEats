/** Real local backend adapter: accounts, cross-browser data, transactions, expiry, images. */
async function call(path,method='GET',payload){
  const opts={method,credentials:'same-origin',headers:{}};
  if(payload!==undefined){opts.headers['Content-Type']='application/json';opts.body=JSON.stringify(payload);}
  let result;
  try{result=await fetch(`/api${path}`,opts);}catch{throw Error('Cannot reach the EchoEats server. Start it using run_echoeats.py.');}
  let data;
  try{data=await result.json();}catch{throw Error(`Server error (${result.status}).`);}
  if(!result.ok)throw Error(typeof data.detail==='string'?data.detail:typeof data.error==='string'?data.error:'Request failed');
  return data;
}
function readImage(file){
  return new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve(reader.result);reader.onerror=()=>reject(Error('Unable to read image.'));reader.readAsDataURL(file);});
}
export const apiStore={
  mode:'server',
  getSession:()=>call('/session'),
  getSnapshot:()=>call('/snapshot'),
  signIn:(email,password)=>call('/auth/login','POST',{email,password}),
  signUp:values=>call('/auth/signup','POST',values),
  signOut:()=>call('/auth/logout','POST',{}),
  saveListing:(form,id)=>id?call(`/listings/${encodeURIComponent(id)}`,'PUT',form):call('/listings','POST',form),
  removeListing:id=>call(`/listings/${encodeURIComponent(id)}`,'DELETE'),
  reserve:(listing_id,quantity)=>call('/reservations','POST',{listing_id,quantity}),
  cancelReservation:id=>call(`/reservations/${encodeURIComponent(id)}/cancel`,'POST',{}),
  payReservation:id=>call(`/reservations/${encodeURIComponent(id)}/pay`,'POST',{}),
  collectReservation:id=>call(`/reservations/${encodeURIComponent(id)}/collect`,'POST',{}),
  updateProfile:values=>call('/profile','PATCH',values),
  changePassword:values=>call('/auth/change-password','POST',values),
  async uploadPhoto(file){
    if(!file?.type?.match(/^image\/(png|jpeg|webp)$/))throw Error('Choose a JPG, PNG, or WebP image.');
    if(file.size>2*1024*1024)throw Error('Photos must be smaller than 2 MB.');
    return (await call('/photos','POST',{data:await readImage(file)})).url;
  },
};
