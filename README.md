# Chess Engine + Django Web App

<strong>Summary</strong>
<br>
The Minimax algorithm is a search algorithm for finding the optimal move to make in a two-player zero-sum game with perfect information (such as chess, checkers, tic-tac-toe). The game tree is recursively generated with each level (turn) alternating between players "Max" and "Min". Max will always try to maximize the score, and vice versa for Min. A score for any given board state will be evaluated at either the terminal game states, or a predeterined depth if the game tree is too large. 

<p align="center">
    <img src="https://github.com/tshiels/chess/blob/master/imgs/minimax_img.png">
</p>

Alpha-Beta Pruning is an optimization for the Minimax algorithm that drastically improves performance. It eliminates nodes that will not have an effect on the outcome of the game. The "best-move-so-far" is saved for both Max and Min, and is tracked for a given level of the game tree. For example, if there is a Min node with 2 child Max nodes, and the first move for Max node 2 is better (greater) than the best move of Max node 1, it will definitely not be chosen by the parent Min node (who will want to minimize the score), so all subsequent Max node 2 moves will be unnecessary to search. 

<p align="center">
    <img src="https://github.com/tshiels/chess/blob/master/imgs/ab_img1.jpg">
</p>

This program plays Chess using the Minimax algorithm with alpha-beta pruning. You can play against the engine, or watch my engine play against the stockfish engine. 
My current evaluation function is a weighted sum based on the relative strength of the pieces remaining on the board, and the number of moves each piece can make.  

***

<strong>Dependencies</strong>:
* Python-chess (included) : https://python-chess.readthedocs.io/en/latest/#
  * uses modified board printout 
* Stockfish engine in `/usr/games/` (if using `minimax_stockfish.py`)
  * Can modify `minimax_stockfish.py` to look for stockfish in custom directory 
* Python django (if using web GUI)
***
<strong>Run Instructions</strong>:
* (Requires Python3.6 or greater)
- To run using <strong>web app GUI</strong> locally:
  - `$ cd chessts`
  - `$ python3 manage.py runserver`
  - open web browser and type `127.0.0.1:8000` into address bar (do not type localhost)
* Minimax:
  * `$ python3 minimax.py`
- Minimax with Alpha-Beta Pruning:
  - `$ python3 alpha_beta.py`
- My engine vs. Stockfish engine at lowest settings:
  - `$ python3 minimax_stockfish.py`

***
<strong>Source Code Locations:</strong>
- Updated CSS and Javascript is located in `chessts/game/static/game/`
- Updated HTML is located in `chessts/game/templates/game/`
- Updated minimax and alpha-beta algorithm located in `alpha_beta` directory
***
<strong>Known Bugs</strong>:
- Loading animation appears indefinitely when white wins by checkmate
- Limited minimax search results in some moves being scored equally, resulting in the 
  same move being repeated back and forth
- game allows player to make moves after draw by threefold repitition
- right-clicking and left-clicking can allow piece to be placed incorrectly
***
<strong>To Do</strong>
- make end-game popup and replay button
- leaderboard
- randomize moves of same score
- difficulty settings / game options
- disable right-click on board
