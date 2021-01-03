# QTicTacToe (under development)
Tic Tac Toe game that learns its moves via Q-Learning using a tkinter UI

![QTicTacToe Screenshot](https://github.com/tonda-che/QTicTacToe/blob/main/readme_pics/screenshot.jpg?raw=true)

The main idea is to apply Q-Learning to an interactive TicTacToe Game while seeing the players decision as an inherent part of the environment. The Algorithm always considers the smartest possible move from the player.

The weights are saved into a json file, making them easy to understand and readable.

On the first level we have the states in a serialized format and ordered in a dictionary for the number of moves played in the game.

For any state there is a number of possible actions that might be played with the corresponding q-value.

JSON
----

```json
"7": {
  "XXO\n--O\nOXX":{
     "cl":{
          "q_value":0.5,
          "future_states":["..."]
     },
     "cm":{
         "q_value":0.5,
         "future_states":["..."]
      }
  }
}
```

In this case both q-values in the displayed part of the json are 0.5 which means they would result in a draw.

The game also offers the functionality to play against itself to further train the weights.

Tested on Mac only as of now.
