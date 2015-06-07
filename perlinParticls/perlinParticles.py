import rhinoscriptsyntax as rs
import perlin

mesh = rs.GetObject("select mesh", 32)
sn = perlin.SimplexNoise()

meshNorms = rs.MeshFaceNormals(mesh)

def constrainVec(inVec):
    if abs(inVec[0]) > abs(inVec[1]) and abs(inVec[0]) > abs(inVec[2]):
        inVec[1] = 0
        inVec[2] = 0
    if abs(inVec[1]) > abs(inVec[0]) and abs(inVec[1]) > abs(inVec[2]):
        inVec[0] = 0
        inVec[2] = 0
    if abs(inVec[2]) > abs(inVec[1]) and abs(inVec[2]) > abs(inVec[0]):
        inVec[1] = 0
        inVec[0] = 0
    
    inVec = rs.VectorUnitize(inVec)
    return inVec

class agent:
    
    def __init__(self, inPos):
        self.pos = inPos
        self.oldPos = inPos
        self.res = 5
        self.noiseScale = .001
    
    def update(self):
        self.oldPos = self.pos
        acc = [0,0,0]
        #get a value from 0 - 1 from perlin noise field
        per = sn.noise3(self.pos[0]*self.noiseScale, self.pos[1]*self.noiseScale, self.pos[2]*self.noiseScale)
        per = per*360
        perVec = [1,0,0]
        
        #find the normal at the closest point on the mesh
        closePoint = rs.MeshClosestPoint(mesh, self.pos) 
        rotAxis = meshNorms[closePoint[1]]
        
        perVec = rs.VectorRotate(perVec, per, rotAxis)
        perVec = rs.VectorUnitize(perVec)
        
        #add perlin vector to acc
        acc = rs.VectorAdd(acc, perVec)
        acc = constrainVec(acc)
        #scale acc by agent resolution and add to pos
        acc = rs.VectorUnitize(acc)
        acc = rs.VectorScale(acc, self.res)
        self.pos = rs.VectorAdd(acc, self.pos)
        
        closePoint = rs.MeshClosestPoint(mesh, self.pos)
        self.pos = closePoint[0]
        
        
    def render(self):
        dis = rs.Distance(self.pos, self.oldPos)
        if dis > 0:
            rs.AddLine(self.pos, self.oldPos)



mV = rs.MeshVertices(mesh)
agents = []

for i in range(len(mV)):
    newAgent = agent(mV[i])
    agents.append(newAgent)

for j in range(20):
    for i in range(len(agents)):
        agents[i].update()
        agents[i].render()