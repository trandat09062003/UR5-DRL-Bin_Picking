# Visual Pushing and Grasping (VPG) with CoppeliaSim

This repository provides PyTorch code for training and testing Visual Pushing and Grasping (VPG) policies using deep reinforcement learning in both simulation and real-world settings with a UR5 robot arm. 

We have heavily optimized and refactored this codebase to support **CoppeliaSim V4.7.0+** on modern Linux systems, featuring robust process management, automated scene loading detection, self-healing retries, and stable gripper physics.

---

## 🚀 Key Improvements & Features

* **ZeroMQ Remote API Scene Detection:** Automatically detects when the CoppeliaSim scene is fully loaded and ready by querying the ZeroMQ Remote API (port `23000`), replacing flaky arbitrary timeouts.
* **Self-Healing Grasp Attempts:** If a grasp fails, the system automatically resets the simulation, wipes the workspace, re-spawns objects staggered vertically from scratch, and tries again until a grasp succeeds.
* **10-Second Auto-Shutdown:** Once a grasp succeeds, the program keeps the GUI open for 10 seconds for visual inspection and then automatically exits. No blocking prompts.
* **Reliable Gripper Physics:** Added precise sleep intervals (`time.sleep(0.01)`) in joint actuation and gripper control loops to allow CoppeliaSim's physics engine to process joint state changes without CPU/API starvation.
* **Vertical Spawning Staggering:** Objects are spawned at vertically offset heights (`0.15 + i * 0.05`) with a 3-second settling delay to prevent clipping/flying during initialization.
* **Clean Process Lifecycle:** Automatically terminates lingering CoppeliaSim background processes and port listeners (`19997` and `23000`) on exit or failures to avoid port collision.

---

## 🛠️ Installation & Setup

### 1. Prerequisites
- **OS:** Ubuntu 22.04 LTS (or similar Linux environment)
- **Python Environment:** Conda with Python 3.8+ (named `vpg` in this setup)
- **Simulator:** CoppeliaSim Pro V4.7.0

### 2. Environment Activation
Activate the Conda environment before running any script:
```bash
conda activate vpg
```

---

## 📖 How to Run the Automated Grasping Demo

We provide a fully automated script that launches the simulator, loads the scene, spawns the blocks, performs grasp planning using object coordinates, resets if it fails, and automatically exits after 10 seconds of success.

To run it:
```bash
python run_one_grasp_gui.py
```

### Flow of `run_one_grasp_gui.py`:
1. Launches CoppeliaSim GUI with the scene `simulation/simulation.ttt`.
2. Connects to the **ZeroMQ Remote API (port 23000)** to poll and verify the scene and UR5 robot are fully loaded.
3. Spawns 10 block objects staggered vertically.
4. Pauses for 3.0 seconds to let all objects fall and settle naturally on the workspace surface.
5. Commands the UR5 robot arm to target and grasp an object in the workspace.
6. **If successful:** Prints success, keeps GUI open for 10 seconds, then exits cleanly.
7. **If failed:** Restarts the simulation scene, re-spawns objects from scratch, and retries.

---

## 🏋️ Training VPG from Scratch

To start the full Deep Q-Learning training pipeline:

1. Launch CoppeliaSim and open the scene `simulation/simulation.ttt`.
2. Run the main script in training mode:
```bash
python main.py --is_sim --push_rewards --experience_replay --explore_rate_decay --save_visualizations
```

To plot training results and performance over time:
```bash
python plot.py 'logs/YOUR-SESSION-DIRECTORY-NAME-HERE'
```

---

## 🔍 Troubleshooting & Process Cleanup

If the simulation gets stuck or ports `19997` / `23000` are already in use, clean all lingering python and simulator processes using:

```bash
# Force kill all running python and coppeliaSim processes
kill -9 $(pgrep -f "coppeliaSim") $(pgrep -f "run_one_grasp_gui.py")
```

---

## 📄 Reference
This repository is based on the reference implementation for:
**Learning Synergies between Pushing and Grasping with Self-supervised Deep Reinforcement Learning (IROS 2018)**
[PDF](https://arxiv.org/pdf/1803.09956.pdf) | [Webpage](http://vpg.cs.princeton.edu/)
