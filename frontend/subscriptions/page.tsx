'use client';
import { useEffect, useState } from 'react'; import { Shell } from '@/components/Shell'; import { api } from '@/lib/api';
export default function Subs(){ const [rows,setRows]=useState<any[]>([]); useEffect(()=>{api('/subscriptions').then(setRows)},[]); return <Shell><h1 className="text-3xl font-bold mb-6">Subscriptions</h1><div className="card">{rows.map(r=><div className="py-3 border-b flex justify-between" key={r.id}><span>{r.name}</span><span>{r.currency} {r.amount}/{r.interval}</span><span>{r.status}</span></div>)}</div></Shell> }
