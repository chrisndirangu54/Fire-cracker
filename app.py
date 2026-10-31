"""Indoor fire response: simulation-first mission console.

No motor, flight-controller, pyrotechnic, or suppression hardware commands.
Do not use for life-safety decisions without certification and validation.
"""
from __future__ import annotations
import math, os, random, threading, time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from safety import assess
from payload import PodReview
from payload_controller import VirtualPayloadController
from drop_zone_validator import SimulatedZone, validate_zone
from gas_suppression_sim import VirtualGasModule

ROOT=Path(__file__).parent
app=FastAPI(title="Fire Rescue Drone - Simulation Console", version="0.1.0")
app.mount('/static', StaticFiles(directory=ROOT/'static'), name='static')
LOCK=threading.RLock()
GRID_W=36; GRID_H=24

def structure():
    grid=[[0]*GRID_W for _ in range(GRID_H)]
    for y in range(GRID_H):
        for x in range(GRID_W):
            if x in (0,GRID_W-1) or y in (0,GRID_H-1):grid[y][x]=1
            if x==17 and y not in range(9,14):grid[y][x]=1
            if y==11 and x in range(4,12):grid[y][x]=1
            if y==16 and x in range(22,33):grid[y][x]=1
    return grid

@dataclass
class Mission:
    mode:str='SIMULATION'
    mission_status:str='IDLE'
    tick:int=0
    x:float=5.0
    y:float=5.0
    heading:float=0.0
    battery:float=100.0
    link_quality:float=100.0
    temperature:float=31.0
    target_id:int|None=None
    suppression_state:str='SAFE_LOCKED'
    last_notice:str='Hardware output is permanently disabled in this demo.'
    pod:PodReview=field(default_factory=PodReview)
    virtual_payload:VirtualPayloadController=field(default_factory=VirtualPayloadController)
    virtual_gas:VirtualGasModule=field(default_factory=VirtualGasModule)
    grid:list=field(default_factory=structure)
    events:list=field(default_factory=list)
    ros2:dict=field(default_factory=lambda:{'connected':False,'safety':{'advisory':'HOLD','faults':['NO_ROS2_FEED'],'hardware_commands_allowed':False}})
    hotspots:list=field(default_factory=lambda:[{'id':1,'x':27,'y':6,'temperature_c':285.,'confidence':0.96}, {'id':2,'x':9,'y':18,'temperature_c':138.,'confidence':0.81}])
    def log(self, message):
        self.events.insert(0,{'t':time.strftime('%H:%M:%S',time.gmtime()),'message':message})
        self.events=self.events[:30]

state=Mission()
state.log('System initialized. Simulation only; no real actuator connection.')

class SensorSample(BaseModel):
    source:Literal['simulator','test-rig']
    x:float=Field(ge=0,lt=GRID_W)
    y:float=Field(ge=0,lt=GRID_H)
    heading:float=Field(default=0,ge=-360,le=360)
    battery:float=Field(ge=0,le=100)
    link_quality:float=Field(ge=0,le=100)
    temperature_c:float=Field(ge=-40,le=2000)
    # Detected hotspots are observations, not firing instructions.
    hotspots:list[dict]=Field(default_factory=list,max_length=20)

class ROSObservation(BaseModel):
    source:Literal['ros2-readonly']
    clearance_m:float|None=Field(default=None,ge=0,le=1000)
    scan_age_s:float|None=Field(default=None,ge=0,le=10000)
    localization_ok:bool=False
    thermal_max_c:float|None=Field(default=None,ge=-273.15,le=3000)
    map_received:bool=False
    odom_received:bool=False
    odom_m:dict[str,float]|None=None
    safety:dict=Field(default_factory=dict)

class PodReviewRequest(BaseModel):
    reviewer: str = Field(min_length=2,max_length=80)
    confirm_no_people_in_zone: bool = False

class TargetRequest(BaseModel):
    hotspot_id:int

@app.get('/')
def home():return FileResponse(ROOT/'static'/'index.html')

@app.get('/api/state')
def get_state():
    with LOCK:
        return snapshot()

def snapshot():
    if state.ros2.get('connected') and time.time()-state.ros2['received_epoch_s']>3:
        state.ros2['connected']=False
        state.ros2['safety']={'advisory':'HOLD','faults':['STALE_ROS2_FEED'],'hardware_commands_allowed':False}
    return {'mode':state.mode,'mission_status':state.mission_status,'tick':state.tick,
    'drone':{'x':round(state.x,2),'y':round(state.y,2),'heading':round(state.heading,2),
             'battery':round(state.battery,1),'link_quality':round(state.link_quality,1),'temperature_c':round(state.temperature,1)},
    'grid':state.grid,'hotspots':state.hotspots,'target_id':state.target_id,
    'suppression_state':state.suppression_state,'payload':{'status':state.pod.status,'target_id':state.pod.target_id,'audit':state.pod.audit[:12]},'last_notice':state.last_notice,'events':state.events,'ros2':state.ros2,
    'virtual_payload':{'phase':state.virtual_payload.phase,'target_id':state.virtual_payload.target_id,'bay_sensor_closed':state.virtual_payload.bay_sensor_closed,'audit':state.virtual_payload.audit[:30]},
    'capabilities':{'simulation':True,'real_flight':False,'physical_suppression':False}}

def traversable(x,y):
    ix,iy=int(round(x)),int(round(y))
    return 1<=ix<GRID_W-1 and 1<=iy<GRID_H-1 and state.grid[iy][ix]==0

@app.post('/api/sim/start')
def start():
    with LOCK:
        if state.battery<15:raise HTTPException(409,'Battery below demonstration minimum')
        state.mission_status='EXPLORING';state.log('Simulated exploration started.')
        return snapshot()

@app.post('/api/sim/pause')
def pause():
    with LOCK:
        state.mission_status='PAUSED';state.log('Simulation paused.')
        return snapshot()

@app.post('/api/sim/reset')
def reset():
    global state
    with LOCK:
        state=Mission();state.log('Simulation reset.')
        return snapshot()

@app.post('/api/sim/step')
def step():
    with LOCK:
        if state.mission_status=='EXPLORING':
            state.tick+=1
            # Deterministic simulated patrol with wall collision rejection.
            angle=state.tick*0.13
            candidates=[(state.x+math.cos(angle)*0.65,state.y+math.sin(angle)*0.65),
                        (state.x+math.sin(angle)*0.65,state.y-math.cos(angle)*0.65)]
            for nx,ny in candidates:
                if traversable(nx,ny):
                    state.x,state.y=nx,ny;break
            state.heading=(math.degrees(angle)%360)
            state.battery=max(0,state.battery-0.08)
            state.link_quality=max(30,98-0.45*abs(state.x-5))
            state.temperature=31+2*math.sin(state.tick*.15)
            if state.battery<=15:
                state.mission_status='PAUSED';state.log('Low battery: simulated mission paused.')
        return snapshot()

@app.post('/api/target')
def target(req:TargetRequest):
    with LOCK:
        if not any(h['id']==req.hotspot_id for h in state.hotspots):raise HTTPException(404,'Unknown hotspot')
        state.target_id=req.hotspot_id
        state.pod.select(req.hotspot_id)
        state.virtual_payload.select(req.hotspot_id)
        state.suppression_state='REVIEW_ONLY'
        state.last_notice='Target tagged for firefighter review. No discharge is possible.'
        state.log(f'Hotspot #{req.hotspot_id} tagged for human review (no actuation).')
        return snapshot()

@app.post('/api/sim/discharge')
def discharge_sim():
    with LOCK:
        if state.target_id is None:raise HTTPException(409,'Select a target first')
        state.suppression_state='SIMULATED_DISCHARGE'
        state.log(f'Simulated suppressant overlay at hotspot #{state.target_id}; no hardware output.')
        state.last_notice='SIMULATION ONLY: mock suppressant release displayed.'
        return snapshot()

@app.post('/api/observations')
def observations(sample:SensorSample, x_demo_token:str|None=Header(default=None)):
    secret=os.getenv('DEMO_INGEST_TOKEN')
    if not secret or x_demo_token!=secret:raise HTTPException(403,'Set DEMO_INGEST_TOKEN and supply X-Demo-Token')
    if sample.source!='test-rig':raise HTTPException(400,'Only test-rig observations accepted by this endpoint')
    with LOCK:
        state.x=sample.x;state.y=sample.y;state.heading=sample.heading
        state.battery=sample.battery;state.link_quality=sample.link_quality;state.temperature=sample.temperature_c
        clean=[]
        for i,h in enumerate(sample.hotspots):
            try:
                x,y,temp,conf=float(h['x']),float(h['y']),float(h['temperature_c']),float(h['confidence'])
            except (KeyError,ValueError,TypeError):raise HTTPException(422,'Invalid hotspot fields')
            if not (0<=x<GRID_W and 0<=y<GRID_H and -40<=temp<=2000 and 0<=conf<=1):
                raise HTTPException(422,'Out-of-range hotspot observation')
            clean.append({'id':i+1,'x':x,'y':y,'temperature_c':temp,'confidence':conf})
        state.hotspots=clean
        state.mission_status='TEST_RIG_FEED'
        state.log('Received observation from authenticated test rig.')
        return snapshot()

@app.get('/api/health')
def health():return {'ok':True,'hardware_outputs_enabled':False}

@app.post('/api/ros2/observations')
def ros2_observations(obs:ROSObservation,x_demo_token:str|None=Header(default=None)):
    secret=os.getenv('DEMO_INGEST_TOKEN')
    if not secret or x_demo_token!=secret:raise HTTPException(403,'Unauthorized observation')
    # The server computes its own advisory rather than trusting client-provided safety flags.
    advisory=assess(clearance_m=obs.clearance_m, sensor_age_s=obs.scan_age_s,
                    battery=None, link=None, localization_ok=False)
    with LOCK:
        state.ros2={'connected':True,'received_epoch_s':time.time(),
                    'clearance_m':obs.clearance_m,'scan_age_s':obs.scan_age_s,
                    'thermal_max_c':obs.thermal_max_c,'map_received':obs.map_received,
                    'odom_received':obs.odom_received,'odom_m':obs.odom_m,
                    'safety':advisory}
        return snapshot()

# Deliberately simulation-only: no actuator or vehicle command paths.
@app.post('/api/pod/review')
def pod_review(req:PodReviewRequest):
    with LOCK:
        if state.pod.target_id is None:
            raise HTTPException(409,'Select a hotspot first')
        # Synthetic zone model; live telemetry cannot authenticate a safe zone.
        zone_known=state.mission_status in ('IDLE','EXPLORING','PAUSED')
        # No live physical safety guarantees; only synthetic scenario accepted.
        sensor_fresh=state.mode=='SIMULATION' and state.battery>=15 and state.link_quality>=30
        result=state.pod.review(req.reviewer,req.confirm_no_people_in_zone,
                                zone_known=zone_known,sensor_fresh=sensor_fresh)
        state.last_notice=f'Virtual pod safety review: {result}. Confirmation is simulation-only.'
        state.log(f'Pod review: {result}')
        return snapshot()

@app.post('/api/pod/simulate')
def pod_simulate():
    with LOCK:
        try:
            state.pod.simulate(zone_known=state.mission_status in ('IDLE','EXPLORING','PAUSED'),
                               sensor_fresh=state.mode=='SIMULATION' and state.battery>=15 and state.link_quality>=30,
                               human_clear=state.pod.human_clearance_confirmed)
        except ValueError as exc:
            raise HTTPException(409,str(exc))
        state.last_notice='Virtual NON-EXPLOSIVE pod drop shown in simulation. No hardware control.'
        state.log('Virtual pod drop completed; physical release disabled.')
        return snapshot()

@app.post('/api/pod/abort')
def pod_abort():
    with LOCK:
        state.pod.abort()
        state.last_notice='Virtual pod workflow canceled and locked.'
        state.log('Pod workflow aborted.')
        return snapshot()


# Enhanced training scenario: all inputs below are synthetic and client-editable.
# These API routes cannot command a servo, solenoid, vehicle, or suppressant.
class VirtualZoneRequest(BaseModel):
    reviewer:str=Field(min_length=2,max_length=80)
    altitude_m:float=Field(default=2,ge=0,le=20)
    x:float=Field(default=5,ge=0,le=36)
    y:float=Field(default=5,ge=0,le=24)
    scan_age_s:float|None=Field(default=0.2,ge=0)
    clearance_m:float|None=Field(default=2.0,ge=0)
    thermal_age_s:float|None=Field(default=0.2,ge=0)
    thermal_target_confirmed:bool=True
    occupancy_clear:bool|None=None
    human_reviewed:bool=False

def simulated_faults(req:VirtualZoneRequest):
    return validate_zone(SimulatedZone(x=req.x,y=req.y,altitude_m=req.altitude_m,
              scan_age_s=req.scan_age_s,clearance_m=req.clearance_m,
              thermal_age_s=req.thermal_age_s,thermal_target_confirmed=req.thermal_target_confirmed,
              occupancy_clear=req.occupancy_clear),state.battery,state.link_quality,req.human_reviewed)

@app.post('/api/virtual-payload/verify')
def virtual_verify(req:VirtualZoneRequest):
    with LOCK:
        if state.virtual_payload.target_id is None:raise HTTPException(409,'Select a target first')
        faults=simulated_faults(req)
        phase=state.virtual_payload.verify(req.reviewer,faults)
        state.last_notice='Training scenario: '+phase+'; '+(', '.join(faults) if faults else 'synthetic prerequisites passed')
        return {'phase':phase,'faults':faults,'state':snapshot()}

@app.post('/api/virtual-payload/arm')
def virtual_arm(req:VirtualZoneRequest):
    with LOCK:
        try: phase=state.virtual_payload.arm(simulated_faults(req))
        except ValueError as e:raise HTTPException(409,str(e))
        state.last_notice='Virtual pod ARMED for training. NO HARDWARE OUTPUT.'
        return {'phase':phase,'state':snapshot()}

@app.post('/api/virtual-payload/release')
def virtual_release(req:VirtualZoneRequest):
    with LOCK:
        try: phase=state.virtual_payload.release(simulated_faults(req))
        except ValueError as e:raise HTTPException(409,str(e))
        state.last_notice='Virtual servo latch opened/closed. No physical pod dropped.'
        state.log('Simulated sealed non-explosive pod release recorded.')
        return {'phase':phase,'state':snapshot()}

@app.post('/api/virtual-payload/abort')
def virtual_abort():
    with LOCK:
        state.virtual_payload.abort()
        state.last_notice='Training payload safe locked.'
        return snapshot()

@app.get('/api/virtual-payload/audit')
def virtual_audit():
    with LOCK:return {'mode':'SIMULATION_ONLY','hardware_output':False,'records':state.virtual_payload.audit}


class VirtualGasRequest(BaseModel):
    agent:Literal['certified_inert_gas','certified_clean_agent']
    room_enclosed:bool=False
    people_present:bool|None=None
    firefighter_approved:bool=False
    ventilation:Literal['low','moderate','high']='high'
    sensor_status:Literal['valid_simulated','unavailable']='unavailable'
    release_mode:Literal['fixed_or_tethered','dropped']='fixed_or_tethered'

@app.post('/api/virtual-gas/evaluate')
def virtual_gas_evaluate(req:VirtualGasRequest):
    with LOCK:
        result=state.virtual_gas.evaluate(**req.model_dump())
        state.log('Virtual gas scenario: '+result['decision'])
        state.last_notice='Gas-module simulation: '+result['decision']+'; no physical discharge.'
        return result

@app.get('/api/virtual-gas/audit')
def virtual_gas_audit():
    with LOCK:
        return {'mode':'SIMULATION_ONLY','records':state.virtual_gas.log}

# Firefighter rescue supply and PA simulation; no hardware output.
from rescue_assistance import RescueAssistant
RESCUE = RescueAssistant()

class RescueSupplyRequest(BaseModel):
    supply: Literal['certified_escape_hood','heat_resistant_covering']
    firefighter_reviewed: bool = False
    protected_pickup_point: bool = False
    occupant_location_verified: bool = False
    route_verified: bool = False
    hardware_certified: bool = False
    air_monitoring_verified: bool = False

class RescuePARequest(BaseModel):
    message: Literal['stay_calm','do_not_enter_smoke','await_responder']
    approved_by_incident_command: bool = False
    language_confirmed: bool = False
    audibility_reviewed: bool = False

@app.post('/api/rescue/supplies/evaluate')
def rescue_supply_evaluate(req: RescueSupplyRequest):
    with LOCK:
        result = RESCUE.assess_supply(**req.model_dump())
        state.log('Rescue supply scenario: '+result['decision'])
        return result

@app.post('/api/rescue/pa/preview')
def rescue_pa_preview(req: RescuePARequest):
    with LOCK:
        result=RESCUE.assess_pa(**req.model_dump())
        state.log('Public-address preview: '+result['decision'])
        return result

@app.get('/api/rescue/audit')
def rescue_audit():
    with LOCK:
        return {'simulation_only':True,'hardware_outputs_enabled':False,'records':RESCUE.audit}


# Certified handheld extinguisher comparison — TRAINING ONLY.
from certified_extinguisher_adapter import AGENTS, ExtinguisherObservation, review_extinguisher

EXTINGUISHER_DESCRIPTIONS = {
    "water_mist": {"name":"Water mist","benefit":"Cooling and localized Class A suppression where rated","caution":"Weight, water/electricity suitability and discharge reaction"},
    "abc_dry_chemical": {"name":"ABC dry chemical","benefit":"Multi-class rated portable extinguishing","caution":"Poor visibility, residue and respiratory exposure"},
    "clean_agent": {"name":"Clean agent","benefit":"Low-residue candidate for properly rated hazards","caution":"Occupant exposure, fire class and certification limits"},
    "co2": {"name":"Carbon dioxide","benefit":"Low-residue for selected rated hazards","caution":"Asphyxiation, cold discharge and nozzle reaction force"},
}
EXTINGUISHER_EVENTS: list[dict] = []

class ExtinguisherScenario(BaseModel):
    agent: Literal["water_mist","abc_dry_chemical","clean_agent","co2"]
    pressure_ok: bool = False
    mounting_verified: bool = False
    mass_balance_verified: bool = False
    thermal_limits_verified: bool = False
    manufacturer_remote_actuation_approved: bool = False
    qualified_engineer_reviewed: bool = False
    firefighter_approved: bool = False
    people_clear: bool = False
    fresh_sensor_evidence: bool = False
    communication_healthy: bool = False

@app.get("/api/extinguisher/catalog")
def extinguisher_catalog():
    return {"agents":EXTINGUISHER_DESCRIPTIONS,"simulation_only":True,"hardware_release_enabled":False}

@app.post("/api/extinguisher/evaluate")
def extinguisher_evaluate(req: ExtinguisherScenario):
    with LOCK:
        result = review_extinguisher(ExtinguisherObservation(**req.model_dump()))
        # Sensor evidence is displayed, not equated to personnel clearance.
        result["live_observation"] = {
            "ros2_connected":bool(state.ros2.get("connected")),
            "lidar_clearance_m":state.ros2.get("clearance_m"),
            "thermal_max_c":state.ros2.get("thermal_max_c"),
            "target_id":state.target_id,
            "telemetry_advisory":state.ros2.get("safety",{}).get("advisory","HOLD")
        }
        result["agent_profile"] = EXTINGUISHER_DESCRIPTIONS[req.agent]
        result["simulated_discharge_status"] = "reviewed_only"
        EXTINGUISHER_EVENTS.insert(0,result)
        del EXTINGUISHER_EVENTS[100:]
        state.log("Extinguisher advisory reviewed: "+req.agent)
        return result

@app.get("/api/extinguisher/status")
def extinguisher_status():
    with LOCK:
        return {"mode":"SIMULATION_ONLY","hardware_release_enabled":False,
                "latest_review":EXTINGUISHER_EVENTS[0] if EXTINGUISHER_EVENTS else None,
                "events":EXTINGUISHER_EVENTS[:12],
                "ros2_connected":bool(state.ros2.get("connected")),
                "lidar_clearance_m":state.ros2.get("clearance_m"),
                "thermal_max_c":state.ros2.get("thermal_max_c")}
