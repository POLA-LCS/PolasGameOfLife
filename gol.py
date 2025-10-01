import os
import pygame as pg
from sys import argv

Color = tuple[int, int, int]  # (R, G, B)
Coord = tuple[int, int]       # (y, x)
Grid = set[Coord]

# ==========================
# CONFIGURATION CONSTANTS
# ==========================

SCREEN_WIDTH: int = 720
SCREEN_HEIGHT: int = 720
FPS: int = 60

INITIAL_CELL_SIZE: int = 10
MIN_CELL_SIZE: int = 1
MAX_CELL_SIZE: int = 100

GRID_COLOR: Color = (30, 30, 30)
ALIVE_COLOR: Color = (255, 255, 255)
BG_COLOR: Color = (18, 18, 18)

INITIAL_SIM_SPEED = 7  # ticks per generation
MIN_SIM_SPEED = 1
MAX_SIM_SPEED = 60

# ==========================
# INITIALIZATION
# ==========================

pg.init()
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption("Game of Life - Interactive")
clock = pg.time.Clock()

# ==========================
# GLOBAL STATE
# ==========================

generationsGrid: list[Grid] = [Grid()]
actualGeneration: int = 0
originalGrid = Grid()  # For reset

cameraOffsetX: int = 0
cameraOffsetY: int = 0
cellSize: int = INITIAL_CELL_SIZE
isSimulating: bool = False
internalTick: int = 0
simulationSpeed: int = INITIAL_SIM_SPEED

dragging: bool = False
lastMousePos: Coord = (0, 0)

drawing: bool = False
drawingAlive: bool = True

# ==========================
# UTILITY FUNCTIONS
# ==========================

def worldToScreen(x: int, y: int) -> Coord:
    return (x * cellSize - cameraOffsetX, y * cellSize - cameraOffsetY)

def screenToWorld(x: int, y: int) -> Coord:
    return ((x + cameraOffsetX) // cellSize, (y + cameraOffsetY) // cellSize)

def countAliveNeighbors(y: int, x: int) -> int:
    count = 0
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy == 0 and dx == 0:
                continue
            if (y + dy, x + dx) in generationsGrid[actualGeneration]:
                count += 1
    return count

def nextGeneration() -> Grid:
    newGrid = Grid()
    toCheck = Grid()
    for y, x in generationsGrid[actualGeneration]:
        toCheck.add((y, x))
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                toCheck.add((y + dy, x + dx))
    for y, x in toCheck:
        neighbors = countAliveNeighbors(y, x)
        alive = (y, x) in generationsGrid[actualGeneration]
        if (alive and neighbors in {2, 3}) or (not alive and neighbors == 3):
            newGrid.add((y, x))
    return newGrid

def drawGrid(screen) -> None:
    screen.fill(BG_COLOR)
    startX: int = cameraOffsetX // cellSize
    startY: int = cameraOffsetY // cellSize
    endX: int = (cameraOffsetX + SCREEN_WIDTH) // cellSize + 1
    endY: int = (cameraOffsetY + SCREEN_HEIGHT) // cellSize + 1

    for y, x in generationsGrid[actualGeneration]:
        if startX <= x <= endX and startY <= y <= endY:
            sx, sy = worldToScreen(x, y)
            pg.draw.rect(screen, ALIVE_COLOR, (sx, sy, cellSize, cellSize))

    if cellSize >= 6:
        for x in range(startX, endX):
            sx, _ = worldToScreen(x, 0)
            pg.draw.line(screen, GRID_COLOR, (sx, 0), (sx, SCREEN_HEIGHT))
        for y in range(startY, endY):
            _, sy = worldToScreen(0, y)
            pg.draw.line(screen, GRID_COLOR, (0, sy), (SCREEN_WIDTH, sy))

def getFileContent(filePath: str) -> str:
    with open(filePath, 'r') as f:
        return f.read()

# ==========================
# FILE LOADING SYSTEM
# ==========================

def loadConwayFile(path: str, offsetX: int = 0, offsetY: int = 0) -> Grid:
    cells = Grid()
    if not os.path.isfile(path):
        print(f"[WARNING] File not found: {path}")
        return cells

    for rawLine in getFileContent(path).splitlines():
        line: str = rawLine.strip()
        if not line or line.startswith('#'):
            continue

        if line.startswith('[') and line.endswith(']'):
            subPath: str = line[1:-1]
            cells |= loadConwayFile(subPath, offsetX, offsetY)
            continue

        partsList: list[str] = [part.strip() for part in line.split(';')]

        for part in partsList:
            if not part:
                continue
            tokens: list[str] = part.split()
            if len(tokens) < 2:
                print(f"[WARNING] Invalid Coordinate segment in {path}: {part}")
                continue
            try:
                y = int(tokens[0]) + offsetY
                x = int(tokens[1]) + offsetX
            except ValueError:
                print(f"[WARNING] Invalid Coordinates in {path}: {part}")
                continue

            if len(tokens) == 2:
                cells.add((y, x))
            elif len(tokens) == 3 and tokens[2].startswith('[') and tokens[2].endswith(']'):
                subPath: str = tokens[2][1:-1]
                cells |= loadConwayFile(subPath, x, y)
            else:
                print(f"[WARNING] Unrecognized format in {path}: {part}")

    return cells

# ==========================
# INPUT HANDLING
# ==========================

def handleKeyUp(eventKey):
    global isSimulating, cellSize, cameraOffsetX, cameraOffsetY, generationsGrid, actualGeneration, internalTick, simulationSpeed

    if eventKey == pg.K_SPACE:
        isSimulating = not isSimulating
    
    elif eventKey == pg.K_ESCAPE:
        generationsGrid.clear()
        actualGeneration = 0
    
    elif eventKey == pg.K_EQUALS or eventKey == pg.K_PLUS:
        cellSize = min(cellSize + 1, MAX_CELL_SIZE)
    
    elif eventKey == pg.K_MINUS or eventKey == pg.K_KP_MINUS:
        cellSize = max(cellSize - 1, MIN_CELL_SIZE)
    
    elif eventKey == pg.K_c:
        cameraOffsetX = 0
        cameraOffsetY = 0
    
    elif eventKey == pg.K_LEFT:
        actualGeneration = max(0, actualGeneration - 1)
    
    elif eventKey == pg.K_RIGHT:
        isSimulating = False
        if actualGeneration >= len(generationsGrid) - 1:
            generationsGrid.append(nextGeneration())
        actualGeneration += 1
    
    elif eventKey == pg.K_UP:
        isSimulating = False
        actualGeneration = len(generationsGrid) - 1
    
    elif eventKey == pg.K_DOWN:
        isSimulating = False
        actualGeneration = 0
    
    elif eventKey == pg.K_r:
        isSimulating = False
        generationsGrid.clear()
        generationsGrid.append(originalGrid.copy())
        actualGeneration = 0
        print("[INFO] Simulation reset to original state.")
    
    elif eventKey == pg.K_q:
        pass
    
    elif eventKey == pg.K_COMMA:
        simulationSpeed = min(simulationSpeed + 1, MAX_SIM_SPEED)
        print(f"[INFO] Simulation speed: {simulationSpeed} ticks per generation")
    
    elif eventKey == pg.K_PERIOD:
        simulationSpeed = max(simulationSpeed - 1, MIN_SIM_SPEED)
        print(f"[INFO] Simulation speed: {simulationSpeed} ticks per generation")

# ==========================
# MAIN LOOP
# ==========================

def simulate(screen, clock):
    global generationsGrid, actualGeneration, cameraOffsetX, cameraOffsetY, cellSize, isSimulating, internalTick
    global dragging, lastMousePos, simulationSpeed, drawingAlive, drawing

    running = True

    while running:
        dt = clock.tick(FPS)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            elif event.type == pg.KEYUP:
                if event.key == pg.K_q:
                    running = False
                else:
                    handleKeyUp(event.key)

            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click: start drawing
                    drawing = True
                    mouse_x, mouse_y = event.pos
                    world_x, world_y = screenToWorld(mouse_x, mouse_y)
                    drawingAlive = (world_y, world_x) not in generationsGrid[actualGeneration]

                elif event.button == 3:  # Right click drag start (camera move)
                    dragging = True
                    lastMousePos = event.pos

                elif event.button == 4:  # Scroll up
                    cellSize = min(cellSize + 1, MAX_CELL_SIZE)

                elif event.button == 5:  # Scroll down
                    cellSize = max(cellSize - 1, MIN_CELL_SIZE)

            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    drawing = False
                elif event.button == 3:
                    dragging = False

            elif event.type == pg.MOUSEMOTION:
                if dragging:
                    dx = event.pos[0] - lastMousePos[0]
                    dy = event.pos[1] - lastMousePos[1]
                    cameraOffsetX -= dx
                    cameraOffsetY -= dy
                    lastMousePos = event.pos

                elif drawing:
                    mouse_x, mouse_y = event.pos
                    world_x, world_y = screenToWorld(mouse_x, mouse_y)
                    cell = (world_y, world_x)
                    if drawingAlive:
                        generationsGrid[actualGeneration].add(cell)
                    else:
                        generationsGrid[actualGeneration].discard(cell)

        if isSimulating:
            if internalTick >= FPS // simulationSpeed:
                if actualGeneration >= len(generationsGrid) - 1:
                    generationsGrid.append(nextGeneration())
                actualGeneration += 1
                internalTick = 0
            internalTick += 1

        drawGrid(screen)
        pg.display.update()

    pg.quit()

# ==========================
# MAIN ENTRY POINT
# ==========================

def main():
    global grid, originalGrid

    if len(argv) == 0:
        print("Usage: python game_of_life.py [pattern_file1] [pattern_file2] ...")
        return

    for arg in argv[1:]:
        loadedCells = loadConwayFile(arg)
        generationsGrid[actualGeneration].update(loadedCells)

    originalGrid = generationsGrid[actualGeneration].copy()
    simulate(screen, clock)

if __name__ == "__main__":
    main()
