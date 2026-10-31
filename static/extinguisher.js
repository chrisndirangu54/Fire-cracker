/* Certified extinguisher review — advisory, no physical hardware action. */
(()=>{
const panel=document.createElement("section");panel.className="panel";panel.style.marginTop="17px";
panel.innerHTML=`<h2>Certified Extinguisher — simulated evaluation</h2>
<p class="muted">Compare portable agents, then review safety gates. No discharge commands.</p>
<label>Agent <select id="extagent">
<option value="water_mist">Water mist</option><option value="abc_dry_chemical">ABC dry chemical</option><option value="clean_agent">Clean agent</option><option value="co2">CO₂</option></select></label>
<p id="extdesc" class="muted"></p>
<div id="extchecks"></div>
<button id="extreview">Evaluate tabletop scenario</button>
<pre id="extresult" style="white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px" aria-live="polite"></pre>
<p id="exttelemetry" class="muted">Observation status unknown</p>
<p class="muted">Occupant detection cannot certify an empty area. All simulated authorizations require independent human checks.</p>`;
const aside=document.querySelector("main aside");if(!aside)return;
aside.insertBefore(panel,aside.firstChild);
const $e=id=>document.getElementById(id);
const checks={
pressure_ok:"Pressure indicated normal (synthetic)",
mounting_verified:"Mount inspection signed off",
mass_balance_verified:"Payload balance independently verified",
thermal_limits_verified:"Operating temperature limits reviewed",
manufacturer_remote_actuation_approved:"Manufacturer authorization documented",
qualified_engineer_reviewed:"Qualified engineering review",
firefighter_approved:"Firefighter approval",
people_clear:"Area independently reviewed for people",
fresh_sensor_evidence:"Fresh LiDAR/thermal evidence confirmed",
communication_healthy:"Command communications verified"};
Object.entries(checks).forEach(([id,label])=>{
const row=document.createElement("p"),l=document.createElement("label"),c=document.createElement("input");
c.type="checkbox";c.id="ext_"+id;l.append(c,document.createTextNode(" "+label));row.append(l);$e("extchecks").append(row);
});
let catalog={};
fetch("/api/extinguisher/catalog").then(r=>r.json()).then(j=>{catalog=j.agents;updateDesc()}).catch(()=>{});
function updateDesc(){const d=catalog[$e("extagent").value];$e("extdesc").textContent=d?(d.benefit+" — Caution: "+d.caution):"Awaiting agent catalog";}
$e("extagent").addEventListener("change",updateDesc);
$e("extreview").addEventListener("click",async()=>{
const body={agent:$e("extagent").value};Object.keys(checks).forEach(k=>body[k]=$e("ext_"+k).checked);
try{const r=await fetch("/api/extinguisher/evaluate",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
const j=await r.json();if(!r.ok)throw Error(JSON.stringify(j));
$e("extresult").textContent=JSON.stringify({tabletop_ready:j.tabletop_ready,failed_gates:j.failed_gates,simulated_discharge_status:j.simulated_discharge_status,hardware_release_enabled:j.hardware_release_enabled,agent_profile:j.agent_profile},null,2);
}catch(e){$e("extresult").textContent=String(e);}
});
async function monitor(){try{const r=await fetch("/api/extinguisher/status");const s=await r.json();$e("exttelemetry").textContent=`LiDAR clearance: ${s.lidar_clearance_m??"unavailable"} m · Thermal: ${s.thermal_max_c??"unavailable"}°C · ROS 2: ${s.ros2_connected?"connected":"offline"} · Release: DISABLED · Reviews: ${s.events.length}`;}catch(e){$e("exttelemetry").textContent="Status unavailable";}}
monitor();setInterval(monitor,3000);
})();
