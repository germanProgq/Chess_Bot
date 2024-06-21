import chess.engine
import os
from datetime import datetime
import numpy as np
import sys

sys.path.append(r"C:\Users\girsh\Desktop\Personal\Web\Active\Chess_Bot\V-Python")
from Ai.chess_bot import (ChessBot, load_or_create_model, board_to_input, encode_move, result_to_value, train_model, save_game_data, model_path, engine_path)


STOCKFISH_RATING = 2500
INITIAL_BOT_RATING = 1000
K_FACTOR = 32

def play_game(bot1, bot2, game_num, train_data):
    print(f"Game {game_num} started.")
    board = chess.Board()
    game_data = []

    while not board.is_game_over():
        if board.turn == chess.WHITE:  # Bot1's turn
            move = bot1.select_move(board)
        else:  # Bot2's turn
            move = bot2.select_move(board)

        if move is None:
            print(f"Game {game_num} ended due to no available move.")
            break

        board.push(move)
        input_vector = board_to_input(board)
        move_vector = encode_move(move)
        game_data.append((input_vector, move_vector))

    print(f"Game {game_num} finished with result: {board.result()}.")
    result_value = result_to_value(board.result())
    train_data.extend([(input_vector, move_vector, result_value) for input_vector, move_vector in game_data])

def evaluate_bot(model_path, engine_path, num_games=3, bot_rating=INITIAL_BOT_RATING):
    model = load_or_create_model(model_path)
    bot = ChessBot(model)
    
    results = {'1-0': 0, '0-1': 0, '1/2-1/2': 0}
    train_data = []
    stockfish_turn = chess.BLACK
    
    for game_num in range(1, num_games + 1):
        if stockfish_turn == chess.BLACK:
            engine_bot = ChessBot(chess.engine.SimpleEngine.popen_uci(engine_path))
            result = play_game(bot, engine_bot, game_num, train_data)
        else:
            result = play_game(bot, bot, game_num, train_data)

        results[result] += 1
        stockfish_turn = not stockfish_turn

    rating = calculate_elo_rating(results, bot_rating)
    return results, rating

def calculate_elo_rating(results, bot_rating, stockfish_rating=STOCKFISH_RATING, k_factor=K_FACTOR):
    score = results['1-0'] + 0.5 * results['1/2-1/2']
    expected_score = 1 / (1 + 10 ** ((stockfish_rating - bot_rating) / 400))
    new_rating = bot_rating + k_factor * (score - expected_score)
    return new_rating

def save_rating_evaluation(results, rating, filename, folder="info/evaluation"):
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, filename)
    with open(file_path, 'w') as file:
        file.write(f'Rating Evaluation:\n')
        file.write(f'Results: {results}\n')
        file.write(f'Rating: {rating}\n')
        file.write(f'Timestamp: {datetime.now()}\n')

if __name__ == '__main__':
    # Evaluate the bot
    results, rating = evaluate_bot(model_path, engine_path, num_games=3)

    # Save the rating evaluation to a file
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f'rating_{timestamp}.txt'
    save_rating_evaluation(results, rating, filename)

    print(f'Rating evaluation saved to {filename}')
    print(f'Results: {results}, Rating: {rating}')
