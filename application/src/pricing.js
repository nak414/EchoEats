/** EchoEats time + demand pricing. Prices are in Bahraini dinars (BHD). */
export const round3 = n => Math.round((Number(n) + Number.EPSILON) * 1000) / 1000;
export const money = n => `BD ${Number(n || 0).toFixed(3)}`;
export const percentOff = (original, current) => original > 0 ? Math.max(0, Math.round((1 - current / original) * 100)) : 0;

export function calculatePrice(listing, now = Date.now()) {
  const initial = Number(listing.initial_price);
  const minimum = Number(listing.min_price);
  const current = Number(listing.current_price ?? initial);
  const start = new Date(listing.created_at).getTime();
  const end = new Date(listing.pickup_deadline).getTime();
  if (!Number.isFinite(start) || !Number.isFinite(end) || end <= start) return round3(Math.max(minimum, Math.min(current, initial)));
  const progress = Math.max(0, Math.min(1, (now - start) / (end - start)));
  const demandRatio = Number(listing.demand_count || 0) / Math.max(1, Number(listing.initial_quantity || 1));
  const demandFactor = demandRatio >= 0.5 ? 0.65 : demandRatio < 0.15 ? 1.10 : 0.90;
  const timeDiscount = Math.min(0.85, progress * 0.75 * demandFactor);
  const proposed = round3(initial * (1 - timeDiscount));
  // Prices may decrease but never increase; always honor the vendor's minimum.
  return round3(Math.max(minimum, Math.min(initial, current, proposed)));
}

export function validateListing(form) {
  const original = Number(form.original_price), initial = Number(form.initial_price), min = Number(form.min_price);
  const qty = Number(form.quantity);
  if (!String(form.name || '').trim()) throw Error('Please enter the food name.');
  if (!String(form.category || '').trim()) throw Error('Please choose a category.');
  if (!Number.isInteger(qty) || qty < 0 || qty > 9999) throw Error('Quantity must be a whole number between 0 and 9999.');
  if (!(original >= initial && initial > min && min > 0)) throw Error('Prices must follow: original ≥ initial > minimum > 0.');
  if (!form.pickup_deadline || !form.expires_at) throw Error('Please enter pickup and expiration times.');
  const pickup = new Date(form.pickup_deadline).getTime(), expiry = new Date(form.expires_at).getTime();
  if (!Number.isFinite(pickup) || !Number.isFinite(expiry)) throw Error('Please enter valid dates.');
  if (pickup <= Date.now()) throw Error('Pickup deadline must be in the future.');
  if (pickup > expiry) throw Error('Pickup deadline cannot be after food expiration.');
  return true;
}

export const isAvailable = (food, now = Date.now()) => food.active !== false && Number(food.quantity) > 0 && new Date(food.pickup_deadline).getTime() > now && new Date(food.expires_at).getTime() > now;
export const formatDate = value => new Date(value).toLocaleString('en-BH', {month:'short',day:'numeric',hour:'numeric',minute:'2-digit'});
export function countdown(target, now = Date.now()) {
  const s = Math.max(0, Math.ceil((new Date(target).getTime() - now) / 1000));
  return `${String(Math.floor(s/60)).padStart(2,'0')}:${String(s%60).padStart(2,'0')}`;
}
