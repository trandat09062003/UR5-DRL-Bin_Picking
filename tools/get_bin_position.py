import time
from simulation import vrep

print("Connecting to CoppeliaSim...", flush=True)
sim_client = vrep.simxStart('127.0.0.1', 19997, True, True, 5000, 5)

if sim_client == -1:
    print("Failed to connect!", flush=True)
    exit(1)

# List some key objects in the scene to find their positions
objects_to_find = ['bin', 'Bin', 'workspace', 'Workspace', 'Floor', 'floor', 'Table', 'table', 'UR5']
for name in objects_to_find:
    res, handle = vrep.simxGetObjectHandle(sim_client, name, vrep.simx_opmode_blocking)
    if res == 0:
        res2, pos = vrep.simxGetObjectPosition(sim_client, handle, -1, vrep.simx_opmode_blocking)
        print(f"Object '{name}': handle={handle}, position={pos}", flush=True)
    else:
        # Try to find objects by searching substring
        pass

# Let's get list of all object handles and names
print("Querying all objects in scene...", flush=True)
# We can call a script function to list all object names
# Or we can do it via simxGetObjects
res, handles = vrep.simxGetObjects(sim_client, vrep.sim_handle_all, vrep.simx_opmode_blocking)
if res == 0:
    print(f"Total objects found: {len(handles)}", flush=True)
    # Get names of first 50 objects
    for h in handles[:50]:
        # Legacy remote API doesn't have a direct way to get object name from handle without a script function,
        # but we can try to query position
        res_p, pos = vrep.simxGetObjectPosition(sim_client, h, -1, vrep.simx_opmode_blocking)
        # print(f"Handle: {h}, position={pos}")

vrep.simxFinish(sim_client)
print("Finished!", flush=True)
