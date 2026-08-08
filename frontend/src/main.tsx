import React, {useEffect, useState} from "react";
import {createRoot} from "react-dom/client";
import "./styles.css";
import {EvidenceEntryForm} from "./components/EvidenceEntryForm";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000/api";
type Indicator = {source_id:number; domain_code:string; standard_code:string; text:string; weightage:number; allows_partial:boolean; category:string; frequency:string|null; evidence_format:string};
type Profile = {id?:number; lab_name:string; address:string; phc_registration_no:string; supervising_pathologist:string};

async function get<T>(path:string): Promise<T> { const r=await fetch(`${API}${path}`); if(!r.ok) throw new Error("Request failed"); return r.json(); }
async function saveProfile(p:Profile):Promise<Profile>{const r=await fetch(`${API}/lab-profile/`,{method:"PATCH",headers:{"Content-Type":"application/json"},body:JSON.stringify(p)});return r.json();}

function App(){
 const [items,setItems]=useState<Indicator[]>([]); const [domains,setDomains]=useState<{code:string;name:string}[]>([]); const [profile,setProfile]=useState<Profile|null>(null); const [filter,setFilter]=useState({domain:"",standard:"",category:"",frequency:""}); const [message,setMessage]=useState(""); const [selected,setSelected]=useState<Indicator|null>(null);
 useEffect(()=>{get<Indicator[]>("/indicators/").then(setItems);get<typeof domains>("/domains/").then(setDomains);get<Profile>("/lab-profile/").then(setProfile)},[]);
 useEffect(()=>{const q=(Object.entries(filter) as [string,string][]).filter(([,v])=>v).map(([k,v])=>`${k}=${encodeURIComponent(v)}`).join("&");get<Indicator[]>(`/indicators/${q?`?${q}`:""}`).then(setItems)},[filter]);
 const update=(key:string,value:string)=>setFilter({...filter,[key]:value});
 return <main><header><div><p className="eyebrow">PHC MSDS · Stage 0–2</p><h1>Compliance Tracker</h1><p className="muted">Al Shifa Laboratory · 118 indicators</p></div><a className="button" href={`${API}/exports/print-pack/`}>Download print pack</a></header>
  <section className="profile"><div><h2>Lab profile</h2><p className="muted">Editable institution details used by the registry and drafts.</p></div>{profile&&<form onSubmit={async e=>{e.preventDefault();setProfile(await saveProfile(profile));setMessage("Profile saved")}}>{(["lab_name","address","phc_registration_no","supervising_pathologist"] as const).map(k=><label key={k}>{k.replace(/_/g," ")}<input value={profile[k]} onChange={e=>setProfile({...profile,[k]:e.target.value})}/></label>)}<button>Save profile</button>{message&&<span className="saved">{message}</span>}</form>}</section>
  <section><div className="section-title"><div><h2>Indicator registry</h2><p className="muted">Read-only PHC checklist. Filter by the locked taxonomy.</p></div><strong>{items.length} indicators</strong></div><div className="filters"><select value={filter.domain} onChange={e=>update("domain",e.target.value)}><option value="">All domains</option>{domains.map(d=><option key={d.code} value={d.code}>{d.code} · {d.name}</option>)}</select><input placeholder="Standard (e.g. ROM-1)" value={filter.standard} onChange={e=>update("standard",e.target.value)}/><select value={filter.category} onChange={e=>update("category",e.target.value)}><option value="">All categories</option><option>physical</option><option>one_time</option><option>recurring</option></select><select value={filter.frequency} onChange={e=>update("frequency",e.target.value)}><option value="">All frequencies</option>{["daily","weekly","monthly","quarterly","biannual","annual","as_needed"].map(x=><option key={x}>{x}</option>)}</select></div><div className="table-wrap"><table><thead><tr><th>#</th><th>Domain / standard</th><th>Indicator</th><th>Category</th><th>Frequency</th><th>Format</th><th>Weight</th><th>Partial</th><th></th></tr></thead><tbody>{items.map(i=><tr key={i.source_id}><td>{i.source_id}</td><td><b>{i.domain_code}</b><br/><span className="muted">{i.standard_code}</span></td><td>{i.text}</td><td><span className={`tag ${i.category}`}>{i.category}</span></td><td>{i.frequency||"—"}</td><td>{i.evidence_format}</td><td>{i.weightage}%</td><td>{i.allows_partial?"Yes":"No"}</td><td><button className="small" onClick={()=>setSelected(i)}>Enter</button></td></tr>)}</tbody></table></div>{selected&&<EvidenceEntryForm indicator={selected} onSaved={()=>{setSelected(null);setMessage("Evidence saved")}}/>}</section>
 </main>
}
createRoot(document.getElementById("root")!).render(<React.StrictMode><App/></React.StrictMode>);
