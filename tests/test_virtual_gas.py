from gas_suppression_sim import VirtualGasModule

BASE=dict(agent='certified_clean_agent',room_enclosed=True,people_present=False,firefighter_approved=True,ventilation='low',sensor_status='valid_simulated',release_mode='fixed_or_tethered')

def test_clear_scenario_still_no_discharge():
    x=VirtualGasModule().evaluate(**BASE)
    assert x['decision']=='VIRTUAL_SCENARIO_ACCEPTED'
    assert x['hardware_output'] is False and x['release_performed'] is False

def test_occupied_fails_closed():
    x=VirtualGasModule().evaluate(**(BASE|{'people_present':None}))
    assert 'OCCUPANCY_NOT_CONFIRMED_CLEAR' in x['faults']

def test_dropped_pressurized_payload_denied():
    x=VirtualGasModule().evaluate(**(BASE|{'release_mode':'dropped'}))
    assert x['decision']=='SCENARIO_REJECTED'

def test_high_ventilation_less_retention():
    m=VirtualGasModule()
    a=m.evaluate(**BASE); b=m.evaluate(**(BASE|{'ventilation':'high'}))
    assert b['relative_retention_index'] < a['relative_retention_index']
