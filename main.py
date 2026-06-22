from vpython import *
import random
import math
import pandas as pd

scene = canvas(title="Smart Reservoir Oxygen Balancing Robot System",
width=1200,height=700,background=vector(0.45,0.75,1))

scene.range = 55

# ------------------------------------------------
# LOAD DATASET
# ------------------------------------------------

data = pd.read_csv("dataset.csv")
do_values = data["Dissolved Oxygen (mg/L)"].dropna().tolist()

# ------------------------------------------------
# FISH TYPE INPUT
# ------------------------------------------------

fish_requirements={
"Tilapia":(3,5),
"Carp":(4,6),
"Catfish":(3,5),
"Trout":(6,9)
}

fish_type=input("Enter Fish Type (Tilapia/Carp/Catfish/Trout): ").strip()

if fish_type not in fish_requirements:
    fish_type="Tilapia"

min_do,max_do=fish_requirements[fish_type]

label(pos=vector(0,10,0),
text="Fish: "+fish_type+" | Minimum DO "+str(min_do),
height=20,box=False,color=color.black)

status_label=label(pos=vector(0,8,0),
text="System Initializing",
height=14,box=False,color=color.white)

# ------------------------------------------------
# WATER
# ------------------------------------------------

water=box(pos=vector(0,-2,0),
size=vector(100,4,100),
opacity=0.35,
color=vector(0,0.4,0.85))

floor=box(pos=vector(0,-20,0),
size=vector(100,2,100),
color=vector(0.4,0.3,0.2))

# ------------------------------------------------
# GRID
# ------------------------------------------------

grid=[]
grid_size=10
index=0

for x in range(-40,40,grid_size):
    for z in range(-40,40,grid_size):

        oxygen=do_values[index % len(do_values)]
        index+=1

        if random.random()<0.15:
            oxygen=random.uniform(0.5,min_do*0.5)

        elif random.random()<0.15:
            oxygen=random.uniform(min_do*0.6,min_do)

        cell=box(pos=vector(x,-1.8,z),
        size=vector(grid_size,0.1,grid_size),
        opacity=0.7)

        cell.oxygen=oxygen

        grid.append(cell)

# ------------------------------------------------
# PLANTS
# ------------------------------------------------

plants=[]
for i in range(60):

    p=cylinder(
    pos=vector(random.uniform(-40,40),-20,random.uniform(-40,40)),
    axis=vector(0,6,0),
    radius=0.4,
    color=color.green)

    p.phase=random.uniform(0,6)
    plants.append(p)

# ------------------------------------------------
# FISH
# ------------------------------------------------

class Fish:

    def __init__(self):

        x=random.uniform(-35,35)
        y=random.uniform(-12,-6)
        z=random.uniform(-35,35)

        self.body=ellipsoid(pos=vector(x,y,z),
        length=1.4,height=0.6,width=0.5,
        color=color.orange)

        self.tail=cone(pos=self.body.pos+vector(-0.7,0,0),
        axis=vector(-0.6,0,0),
        radius=0.3,color=color.orange)

        self.v=vector(random.uniform(-0.04,0.04),
        random.uniform(-0.01,0.01),
        random.uniform(-0.04,0.04))

    def get_cell(self):

        for c in grid:
            if mag(c.pos-self.body.pos)<5:
                return c
        return None

    def move(self):

        cell=self.get_cell()

        if cell:
            self.body.color=color.red if cell.oxygen<min_do else color.orange

        self.body.pos+=self.v
        self.tail.pos=self.body.pos+vector(-0.7,0,0)

        if self.body.pos.y>-4 or self.body.pos.y<-15:
            self.v.y*=-1

        if abs(self.body.pos.x)>40:
            self.v.x*=-1

        if abs(self.body.pos.z)>40:
            self.v.z*=-1


fish_list=[Fish() for _ in range(100)]

# ------------------------------------------------
# HELPER
# ------------------------------------------------

def move_assembly(parts,step):
    for p in parts:
        p.pos+=step

# ------------------------------------------------
# SCOUT ROBOT (WITH ANTENNA + DEPTH SENSORS)
# ------------------------------------------------

scout_start=vector(-35,-1,-35)

scout_floatL=box(pos=scout_start+vector(-2,-0.6,0),
size=vector(1,1,6),color=color.gray(0.3))

scout_floatR=box(pos=scout_start+vector(2,-0.6,0),
size=vector(1,1,6),color=color.gray(0.3))

scout_body=box(pos=scout_start+vector(0,0.2,0),
size=vector(3.5,0.8,2.5),color=vector(0.1,0.7,0.9))

scout_antenna=cylinder(
pos=scout_start+vector(0,0.6,0),
axis=vector(0,2,0),
radius=0.08,
color=color.white)

antenna_tip=sphere(
pos=scout_antenna.pos+scout_antenna.axis,
radius=0.2,
color=color.red,
emissive=True)

sensor_stick=cylinder(
pos=scout_start+vector(0,0.2,0),
axis=vector(0,-13,0),
radius=0.12,
color=color.gray(0.7))

sensor_surface=sphere(pos=scout_start+vector(0,-2,0),
radius=0.6,color=color.yellow,emissive=True)

sensor_mid=sphere(pos=scout_start+vector(0,-7,0),
radius=0.6,color=color.green,emissive=True)

sensor_bottom=sphere(pos=scout_start+vector(0,-12,0),
radius=0.6,color=color.red,emissive=True)

scout_all=[
scout_body,
scout_floatL,
scout_floatR,
scout_antenna,
antenna_tip,
sensor_stick,
sensor_surface,
sensor_mid,
sensor_bottom
]

scout_waypoints=[vector(x,-1,z)
for x in range(-35,40,15)
for z in range(-35,40,15)]

random.shuffle(scout_waypoints)

scout_state={
"wp_index":0,
"detected_cell":None
}

# ------------------------------------------------
# BASE ROBOT (AERATOR)
# ------------------------------------------------

base_start=vector(35,-1,35)

base_floatL=box(pos=base_start+vector(-3,-0.7,0),
size=vector(1.4,1.2,7),color=color.gray(0.25))

base_floatR=box(pos=base_start+vector(3,-0.7,0),
size=vector(1.4,1.2,7),color=color.gray(0.25))

base_body=box(pos=base_start+vector(0,0.2,0),
size=vector(5,1.2,4),color=color.yellow)

base_antenna=cylinder(
pos=base_start+vector(0,0.8,0),
axis=vector(0,2.5,0),
radius=0.1,
color=color.white)

antenna_head=sphere(
pos=base_antenna.pos+base_antenna.axis,
radius=0.25,
color=color.green,
emissive=True)

base_paddleL=box(pos=base_start+vector(-4,-1,0),
size=vector(0.6,2.5,3),
color=color.orange)

base_paddleR=box(pos=base_start+vector(4,-1,0),
size=vector(0.6,2.5,3),
color=color.orange)

motor=cylinder(
pos=base_start+vector(0,0.4,-1),
axis=vector(0,0,2),
radius=0.6,
color=color.gray(0.5))

base_all=[
base_body,
base_floatL,
base_floatR,
base_antenna,
antenna_head,
motor,
base_paddleL,
base_paddleR
]

base_state={
"mode":"standby",
"target":None,
"timer":0
}

# ------------------------------------------------
# GRAPH
# ------------------------------------------------

g=graph(title="Reservoir Average DO",
xtitle="Time",ytitle="DO")

curve1=gcurve(color=color.green)

time_step=0

# ------------------------------------------------
# COLOR UPDATE
# ------------------------------------------------

def update_colors():

    for cell in grid:

        if cell.oxygen<min_do*0.6:
            cell.color=vector(0.7,0.9,1)

        elif cell.oxygen<min_do:
            cell.color=vector(0.3,0.6,0.95)

        else:
            cell.color=vector(0,0,0.5)

# ------------------------------------------------
# SCOUT UPDATE
# ------------------------------------------------

def update_scout():

    wp=scout_waypoints[scout_state["wp_index"]%len(scout_waypoints)]

    direction=norm(wp-scout_body.pos)

    step=direction*0.12

    move_assembly(scout_all,step)

    if mag(scout_body.pos-wp)<1.5:

        scout_state["wp_index"]+=1

        for cell in grid:

            if mag(cell.pos-scout_body.pos)<7:

                surface=cell.oxygen+random.uniform(0.3,0.6)
                mid=cell.oxygen
                bottom=cell.oxygen-random.uniform(0.4,0.8)

                avg=(surface+mid+bottom)/3

                if avg<min_do:
                    scout_state["detected_cell"]=cell
                    status_label.text="Scout detected LOW DO"
                    antenna_tip.color=color.red
                    return

# ------------------------------------------------
# BASE UPDATE
# ------------------------------------------------

def update_base():

    if base_state["mode"]=="standby":

        detected=scout_state["detected_cell"]

        if detected and detected.oxygen<min_do:

            base_state["target"]=detected
            base_state["mode"]="moving"

            antenna_head.color=color.red

            scout_state["detected_cell"]=None

    elif base_state["mode"]=="moving":

        direction=norm(base_state["target"].pos-base_body.pos)

        step=direction*0.08

        move_assembly(base_all,step)

        base_paddleL.rotate(angle=0.2,axis=vector(1,0,0),origin=base_body.pos)
        base_paddleR.rotate(angle=0.2,axis=vector(1,0,0),origin=base_body.pos)

        if mag(base_body.pos-base_state["target"].pos)<2:

            base_state["mode"]="aerating"
            base_state["timer"]=0

    elif base_state["mode"]=="aerating":

        base_paddleL.rotate(angle=0.6,axis=vector(1,0,0),origin=base_body.pos)
        base_paddleR.rotate(angle=0.6,axis=vector(1,0,0),origin=base_body.pos)

        base_state["timer"]+=1

        cell=base_state["target"]

        cell.oxygen+=0.05

        if base_state["timer"]>200 or cell.oxygen>=min_do:

            base_state["mode"]="standby"
            base_state["target"]=None

            antenna_head.color=color.green

# ------------------------------------------------
# AVERAGE DO
# ------------------------------------------------

def average_do():

    return sum(c.oxygen for c in grid)/len(grid)

# ------------------------------------------------
# MAIN LOOP
# ------------------------------------------------

t=0

while True:

    rate(40)

    t+=0.05
    time_step+=1

    update_scout()
    update_base()
    update_colors()

    if time_step%5==0:
        curve1.plot(time_step,average_do())

    for p in plants:
        p.axis.x=0.6*math.sin(t+p.phase)

    for f in fish_list:
        f.move()