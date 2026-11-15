import { apiStore } from './apiStore.js';
/** Use the real local Python + SQLite server for all application data. */
export async function makeStore(){ return apiStore; }
