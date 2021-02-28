# tetris-neat

A mediocre ai that uses python-neat to evolve a neural network for playing tetris.

The project includes:
* The game itself
* A script to train a new model
* A script to test existing models

The models can usually clear ~5 lines per game. A different approach to evolving the network or some other changes might end up yielding better results.



![screenshot of the game](https://raw.githubusercontent.com/MilanFIN/tetris-neat/main/screenshot.png)



**How it works**

The ai plays by evaluating the possible placements for the next shape and choosing the one that gets the highest score from the neural network.
The placement options include each x coordinate for each orientation.

When training a new model, fitness is evaluated based on amount of blocks placed per game and the amount of lines cleared. Each block grants 1 point and a line clear 1000. Lines cleared wasn't enough on it's own, as early during training the model won't be clearing lines. Score by amount of blocks favors models that are capable of surviving longer until a line clear is achieved.

There are 3 versions of the model. 

The first one (small) only uses an input vector size of 5. The values correspond to different properties of the gamestate after a simulated placement. These include:
* amount of height added compared to last state
* amount of holes added, these include all locations, which are shadowed by a block from above
* lines that are created by the placement
* roughness, which is the sum of height differences between adjacent columns
* amount of blocks that the shape is touching after it is placed (includes borders)

The second model (big) uses an input vector size of 200. Each element corresponds to a coordinate on the board and has a value of 0 or 1 depending on if that coordinate has a block in it.

The third model (superbig) uses a input vector size of 205, which is made of the combination of the small and big input vectors.

**Running it**

Testing a model: run `python3 test.py <version>` where <version> is either small/big/superbig corresponding to the version of the model.
  
Playing the game: run `python3 play.py` 

Generate a model: run `python3 multi.py`

**Training a new model**

New models can be trained by using the multi.py, script. In the beginning of the file the constants written in ALLCAPS, can be used to modify training parameters. Also the corresponding config file under /config can be modified.

