import traci
import random
import threading
import tkinter as tk

seed = random.randint(0, 2147483647)
traci.start([
    "sumo-gui",
    "-c", "config.sumocfg",
    "--seed", str(seed),
    "--start"
])

tls_id = traci.trafficlight.getIDList()[0]

root = tk.Tk()
root.title("Traffic Control Monitor")
screen_width = root.winfo_screenwidth()
monitor_width = 430
monitor_height = 350
monitor_x = screen_width - monitor_width - 200
monitor_y = 10
root.geometry(f"{monitor_width}x{monitor_height}+{monitor_x}+{monitor_y}")

def hide_monitor():
    root.withdraw()

root.protocol("WM_DELETE_WINDOW", hide_monitor)
frame = tk.Frame(root)
frame.pack(pady=10)
scrollbar = tk.Scrollbar(frame)
log_box = tk.Text(
    frame,
    height=30,
    width=60,
    font=("Arial", 12),
    yscrollcommand=scrollbar.set
)
scrollbar.config(command=log_box.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
log_box.pack(side=tk.LEFT)

def gui_print(text):
    root.after(0, lambda: log_box.insert(tk.END, text + "\n"))
    root.after(0, lambda: log_box.see(tk.END))

manual_window = tk.Toplevel(root)
manual_window.title("Manual Override")
manual_width = 400
manual_height = 150
manual_x = monitor_x
manual_y = monitor_y + monitor_height + 50
manual_window.geometry(f"{manual_width}x{manual_height}+{manual_x}+{manual_y}")

def hide_manual():
    manual_window.withdraw()

manual_window.protocol("WM_DELETE_WINDOW", hide_manual)
buttons = {}
manual_override = None
manual_override_active = None

def set_manual(edge):
    global manual_override, manual_override_active, last_switch_time  
    if edge is None:
        manual_override = None
        for b in buttons.values():
            b.config(bg="SystemButtonFace",activebackground="SystemButtonFace")
        if manual_override_active:
            manual_override_active = None
            last_switch_time = 0 
        gui_print("Manual Override Cancelled")
        gui_print("_____________________________________________")
        return
    manual_override = edge
    for b in buttons.values():
        b.config(bg="SystemButtonFace", activebackground="SystemButtonFace")
    buttons[edge].config(bg="#7CFC00", activebackground="#7CFC00")
    gui_print("Manual Override : " + edge)

buttons["N2J"] = tk.Button(manual_window,text="North",command=lambda:set_manual("N2J"),width=15)
buttons["N2J"].grid(row=0,column=1,pady=10)
buttons["S2J"] = tk.Button(manual_window,text="South",command=lambda:set_manual("S2J"),width=15)
buttons["S2J"].grid(row=2,column=1,pady=10)
buttons["E2J"] = tk.Button(manual_window,text="East",command=lambda:set_manual("E2J"),width=15)
buttons["E2J"].grid(row=1,column=2,padx=10)
buttons["W2J"] = tk.Button(manual_window,text="West",command=lambda:set_manual("W2J"),width=15)
buttons["W2J"].grid(row=1,column=0,padx=10)
cancel_button = tk.Button(manual_window,text="Cancel",command=lambda:set_manual(None),width=15)
cancel_button.grid(row=1,column=1)

edge_to_lanes = {
"N2J":["N2J_0","N2J_1","N2J_2"],
"S2J":["S2J_0","S2J_1","S2J_2"],
"E2J":["E2J_0","E2J_1","E2J_2"],
"W2J":["W2J_0","W2J_1","W2J_2"]
}

camera_to_lane = {
"cam_N2J_0":"N2J_0","cam_N2J_1":"N2J_1","cam_N2J_2":"N2J_2",
"cam_S2J_0":"S2J_0","cam_S2J_1":"S2J_1","cam_S2J_2":"S2J_2",
"cam_E2J_0":"E2J_0","cam_E2J_1":"E2J_1","cam_E2J_2":"E2J_2",
"cam_W2J_0":"W2J_0","cam_W2J_1":"W2J_1","cam_W2J_2":"W2J_2"
}

GREEN_PHASE={"N2J":0,"S2J":2,"E2J":4,"W2J":6}
PHASE_TO_EDGE={v:k for k,v in GREEN_PHASE.items()}

MAX_GREEN=45

current_edge=random.choice(list(GREEN_PHASE.keys()))
current_green_phase=GREEN_PHASE[current_edge]
last_switch_time=traci.simulation.getTime()

edge_last_served = {
    "N2J":0,
    "S2J":0,
    "E2J":0,
    "W2J":0
}
edge_last_served[current_edge] = last_switch_time

manual_override_active=None
emergency_active=None

traci.trafficlight.setPhase(tls_id,current_green_phase)

gui_print("Initial Edge → "+current_edge)
gui_print("_____________________________________________")

def get_edge_density(edge):
    count=0
    for lane in edge_to_lanes[edge]:
        cam_id="cam_"+lane
        try:
            count+=traci.lanearea.getLastStepVehicleNumber(cam_id)
        except:
            pass
    return count

def detect_emergency():
    for cam,lane in camera_to_lane.items():
        try:
            vehicles=traci.lanearea.getLastStepVehicleIDs(cam)
            for v in vehicles:
                if traci.vehicle.getTypeID(v)=="emergency":
                    return lane.split("_")[0]
        except:
            pass
    return None

def run_sim():
    global current_edge,current_green_phase,last_switch_time
    global manual_override,manual_override_active,emergency_active
    while traci.simulation.getMinExpectedNumber()>0:
        traci.simulationStep()
        now=traci.simulation.getTime()
        
        emergency_edge=detect_emergency()
        if emergency_edge:
            if current_edge != emergency_edge:
                current_edge =emergency_edge
                current_green_phase=GREEN_PHASE[current_edge]
                traci.trafficlight.setPhase(tls_id,current_green_phase)
                last_switch_time=now
                emergency_active=current_edge
                edge_last_served[current_edge]=now
                manual_override_active=None
                gui_print("🚑 Emergency → "+current_edge)
                gui_print("Switched Green → "+current_edge)
                gui_print("_____________________________________________")
                continue
        
        if emergency_active and current_edge==emergency_active:
            if now-last_switch_time>=MAX_GREEN:
                emergency_active=None
                last_switch_time=0
    
        if manual_override and not emergency_active and manual_override!=current_edge:
            current_edge=manual_override
            current_green_phase=GREEN_PHASE[current_edge]
            traci.trafficlight.setPhase(tls_id,current_green_phase)
            last_switch_time=now
            manual_override_active=current_edge
            edge_last_served[current_edge]=now
            manual_override=None
            gui_print("Switched Green → "+current_edge)
            gui_print("_____________________________________________")
            continue
    
        if not emergency_active:
            if now-last_switch_time>=MAX_GREEN:
                if manual_override_active:
                    for b in buttons.values():
                        b.config(bg="SystemButtonFace", activebackground="SystemButtonFace")
                    manual_override_active=None
                densities={edge:get_edge_density(edge) for edge in edge_to_lanes}
                gui_print("Traffic densities: "+str(densities))
                max_density = max(densities.values())
                candidates = [edge for edge,d in densities.items() if d==max_density]
                if len(candidates) == 1:
                    next_edge = candidates[0]
                else:
                    next_edge=min(candidates, key=lambda e: edge_last_served[e])
                gui_print("Next edge → "+next_edge)
                current_edge=next_edge
                current_green_phase=GREEN_PHASE[current_edge]
                traci.trafficlight.setPhase(tls_id,current_green_phase)
                last_switch_time=now
                edge_last_served[current_edge]=now
                manual_override_active=None
                gui_print("Switched Green → "+current_edge)
                gui_print("_____________________________________________")

    traci.close()

threading.Thread(target=run_sim,daemon=True).start()
root.mainloop()