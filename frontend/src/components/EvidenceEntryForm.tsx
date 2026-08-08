import {useState} from "react";
import type {FormEvent} from "react";

type Props = {indicator:{source_id:number;text:string;evidence_format:string;allows_partial:boolean;category:string;frequency:string|null}; onSaved:()=>void};

export function EvidenceEntryForm({indicator,onSaved}:Props){
 const [status,setStatus]=useState("fully_met"); const [submittedBy,setSubmittedBy]=useState(""); const [payload,setPayload]=useState(""); const [error,setError]=useState("");
 async function submit(e:FormEvent){e.preventDefault();setError("");let body:any={indicator:indicator.source_id,submitted_by:submittedBy,status,payload:{}};
  if(indicator.category==="recurring"&&indicator.frequency!=="as_needed") body.period_label=new Date().toISOString().slice(0,10);
  if(indicator.evidence_format==="structured_form"){try{body.payload=JSON.parse(payload||"{}")}catch{setError("Enter valid JSON fields");return}}
  else body.payload={file_name:payload};
  const form=new FormData();Object.entries(body).forEach(([key,value])=>form.append(key,typeof value==="object"?JSON.stringify(value):String(value)));if(indicator.evidence_format!=="structured_form"){const fileInput=e.currentTarget.querySelector("input[type=file]") as HTMLInputElement;if(fileInput.files?.[0])form.append("attachment",fileInput.files[0])};
  const r=await fetch(`${import.meta.env.VITE_API_URL||"http://localhost:8000/api"}/evidence/records/`,{method:"POST",body:form});if(!r.ok){setError((await r.json()).detail||"Entry could not be saved");return}onSaved();
 }
 return <form className="entry" onSubmit={submit}><h3>Enter evidence · {indicator.source_id}</h3><p className="muted">{indicator.text}</p><div className="entry-grid"><label>Submitted by<input required value={submittedBy} onChange={e=>setSubmittedBy(e.target.value)}/></label><label>Status<select value={status} onChange={e=>setStatus(e.target.value)}><option value="fully_met">Fully met</option>{indicator.allows_partial&&<option value="partially_met">Partially met</option>}<option value="not_met">Not met</option></select></label></div>{indicator.evidence_format==="structured_form"?<label>Structured fields (JSON)<textarea required placeholder="{ &quot;field&quot;: &quot;value&quot; }" value={payload} onChange={e=>setPayload(e.target.value)}/></label>:<label>{indicator.evidence_format} file reference<input required type="file" onChange={e=>setPayload(e.target.files?.[0]?.name||"")}/></label>}{error&&<p className="error">{error}</p>}<button>Save evidence</button></form>;
}
