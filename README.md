# Simple Chess Engine

<strong>Summary</strong>
<br>

This program plays Chess using the Minimax algorithm with alpha-beta pruning. You can play against the engine, or watch my engine play against the stockfish engine (currently at lowest settings). 
My current evaluation function is a linear combination of the number of white vs. black pieces on board, with weights being relative to the importance of each type of piece. White and Black weights are equal and opposite. 

The Minimax algorithm is a search algorithm for finding the optimal move to make in a two-player zero-sum game with perfect information (such as chess, checkers, tic-tac-toe). The game tree is recursively generated with each level (turn) alternating between players Max and Min. Max will always choose the greatest score out of its children nodes, and vice versa for Min. 

![Minimax Example](https://github.com/tshiels/chess/blob/master/minimax_img.png)
***

<strong>Dependencies</strong>:
* Python-chess (included) : https://python-chess.readthedocs.io/en/latest/#
  * includes modified board printout 
* Stockfish engine in `/usr/games/` (if using `minimax_stockfish.py`)
***
<strong>Run Instructions</strong>:
* (Requires Python3.6 or greater)
* Original evaluation function:
  * `$ python3 chess_minimax.py`
- Updated evaluation function:
  - `$ python3 chess_minimax.py`
- My engine vs. Stockfish engine at lowest settings:
  - `$ python3 minimax_stockfish.py`
