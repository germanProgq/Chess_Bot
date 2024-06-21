import chess
from chess import Board
from chess_bot import create_model
from chess_bot import ChessBot  # Import your ChessBot class from your bot script

def main():
    model = create_model()
    # Initialize board and bot
    board = Board()
    bot = ChessBot(model)  # Initialize your ChessBot instance

    # Main game loop
    while not board.is_game_over():
        print(board)  # Display the current board
        if board.turn == chess.WHITE:
            move = input("Enter your move (in algebraic notation): ")
            try:
                # Apply the user's move to the board
                board.push_san(move)
            except ValueError:
                print("Invalid move. Please enter a valid move in algebraic notation.")
                continue
        else:
            # Let the bot select its move
            bot_move = bot.select_move(board)
            board.push(bot_move)
            print(f"Bot's move: {bot_move}")

    # Display the final outcome of the game
    print("Game over!")
    print("Result:", board.result())

if __name__ == "__main__":
    main()
