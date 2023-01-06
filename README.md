# Unbeatable-Tic-tac-toe
An AI script using Minimax algorithm to play Tic-Tac-Toe. The Minimax agent is guranteed a draw at least against Random AI agents and Human Players. From 1000 games with Minimax agent playing as 'O' against a Random agent playing as 'X', Minimax agent won 804 times and tied 196 times. Moreover, when two Minimax agents play aginst each other, a draw is the game result every time due to the deterministic nature of Minimax.

## Deployment

To deploy this project run

```bash
  python run.py arg1 arg2
```
where arg1 represents the X player and arg2 represents the O player.
To choose a human player, type in 'h'. To choose a minimax player,
type in 'm'. To choose a random player, type in any character. As
an example, 

```bash
python run.py h m 
```
initiates a game where X is a human player and O is a minimax player.