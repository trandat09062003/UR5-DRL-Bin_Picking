import time
import os
from simulation import vrep

print("Connecting to CoppeliaSim...", flush=True)
sim_client = vrep.simxStart('127.0.0.1', 19997, True, True, 5000, 5)

if sim_client == -1:
    print("Failed to connect!", flush=True)
    exit(1)

# Import a shape first to get its handle
print("Calling importShape script function...", flush=True)
obj_mesh_dir = os.path.abspath('objects/blocks')
mesh_list = os.listdir(obj_mesh_dir)
curr_mesh_file = os.path.join(obj_mesh_dir, mesh_list[0])
curr_shape_name = 'shape_00'
object_position = [-0.5, 0.0, 0.15]
object_orientation = [0.0, 0.0, 0.0]
object_color = [1.0, 0.0, 0.0]

ret_resp, ret_ints, ret_floats, ret_strings, ret_buffer = vrep.simxCallScriptFunction(
    sim_client, 
    'remoteApiCommandServer', 
    vrep.sim_scripttype_childscript, 
    'importShape', 
    [0,0,255,0], 
    object_position + object_orientation + object_color, 
    [curr_mesh_file, curr_shape_name], 
    bytearray(), 
    vrep.simx_opmode_blocking
)

print(f"importShape returned: res={ret_resp}, ints={ret_ints}", flush=True)
if ret_resp == 0 and len(ret_ints) > 0:
    handle = ret_ints[0]
    print(f"Imported shape handle: {handle}", flush=True)
    
    # Get position
    res, pos = vrep.simxGetObjectPosition(sim_client, handle, -1, vrep.simx_opmode_blocking)
    print(f"Position of shape {handle}: res={res}, pos={pos}", flush=True)
    
    # Let's start the simulation to see if the shape moves/falls!
    print("Starting simulation...", flush=True)
    vrep.simxStartSimulation(sim_client, vrep.simx_opmode_blocking)
    
    # Wait a few seconds and check position again
    for t in range(5):
        time.sleep(1.0)
        res, pos = vrep.simxGetObjectPosition(sim_client, handle, -1, vrep.simx_opmode_blocking)
        print(f"  t={t+1}s: Position of shape: res={res}, pos={pos}", flush=True)
        
    print("Stopping simulation...", flush=True)
    vrep.simxStopSimulation(sim_client, vrep.simx_opmode_blocking)
else:
    print("Failed to import shape!", flush=True)

vrep.simxFinish(sim_client)
print("Finished!", flush=True)
