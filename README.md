# Interactive Conway's Game Of Life (GOL)

This is a simple project recreating [Conway's Game Of Life](https://en.m.wikipedia.org/wiki/Conway%27s_Game_of_Life) the whole set of rules created by [Jonh Horton Conway](https://es.wikipedia.org/wiki/John_Horton_Conway).  
It was a beatiful mechanic of rewind, pause, play and forward.  

## Requirements
- Python 3.10+
- pygame
```bash
pip install pygame
```

## Mouse controls
**Dragging:**  
Dragging through the screen with the right click will move the camera.  
Dragging with the left click will "draw" living cells if the drag starts from a dead cell  
or dead cells if the drag starts from a living cell.
  
**Scroll:**
Scrolling upwards causes the cells to become bigger (zoom effect).  
Scrolling downwards does the opposite.  

## Keybindings
- `q`: Quits the window and terminates the program.
- `escape`: Clears the entire grid.
- `space`: Reproduces the simulation.
- `left`: Moves to the previous generation.
- `right`: Moves to the next generation.
- `down`: Goes to the first generation.
- `up`: Goes to the last generation.
- `+`: Same as scroll upwards.
- `-`: Same as scroll downwards.
- `dot`: Reduces the simulation speed by 1 tick (min 1).
- `comma`: Increase the simulation speed by 1 tick (max 60).

## Conway object representation (COR)
This is a simple format to load easily initial states in the conway world.  
The system has many useful features such as relative coordinates and recursive COR integration.  
  
This is a simple COR file which represents a static block of 2x2:
```
0 0
0 1
1 0
1 1
```