import chess
import chess.engine
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Conv2D, Flatten, Reshape, Add, Attention, LSTM, Dropout
from tensorflow.keras.optimizers import Adam
import os
import keras_tuner as kt
import sys
import random

sys.path.append(r"C:\Users\girsh\Desktop\Personal\Web\Active\Chess_Bot\V-Python")
from Ai.eval import analyze_board

# Define the path to the Stockfish engine
engine_path = r"C:\Users\girsh\Desktop\Personal\Web\Active\stockfish\stockfish-windows-x86-64-avx2.exe"
# Define the path to save the model
model_path = 'Ai/bot/chess_model.h5'
# Define the folder to save game data
game_data_folder = 'game_data'

def get_next_game_num(folder):
    files = os.listdir(folder)
    if not files:
        return 0
    game_nums = [int(file.split('_')[1].split('.')[0]) for file in files if file.startswith('game_')]
    return max(game_nums) + 1

def save_game_data(game_data, game_num, result, folder=game_data_folder):
    os.makedirs(folder, exist_ok=True)
    file_name = os.path.join(folder, f'game_{game_num:04d}.npz')
    input_vectors, move_vectors = zip(*game_data)
    np.savez(file_name, input_vectors=input_vectors, move_vectors=move_vectors, result=result)

def board_to_input(board):
    input_vector = np.zeros(64)
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            input_vector[square] = piece_value(piece)
    return input_vector

def piece_value(piece):
    piece_type = piece.piece_type
    color = 1 if piece.color == chess.WHITE else -1
    values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0
    }
    return values[piece_type] * color

def encode_move(move):
    from_square = move.from_square
    to_square = move.to_square
    move_vector = np.zeros(64 * 64)
    move_vector[from_square * 64 + to_square] = 1
    return move_vector

def decode_move(prediction, board):
    legal_moves = list(board.legal_moves)
    move_scores = {move: prediction[encode_move(move).argmax()] for move in legal_moves}
    best_move = max(legal_moves, key=lambda move: move_scores[move])
    return best_move

class ChessBot:
    def __init__(self, model):
        self.model = model
        self.is_ai_model = isinstance(model, tf.keras.Model)

    def select_move(self, board):
        if self.is_ai_model:
            input_vector = board_to_input(board)
            prediction = self.model.predict(np.array([input_vector]))[0]
            move = decode_move(prediction, board)
        else:
            result = self.model.play(board, chess.engine.Limit(time=0.1))
            move = result.move
        
        return move

def result_to_value(result):
    if result == "1-0":
        return 1.0
    elif result == "0-1":
        return -1.0
    elif result == "1/2-1/2":
        return 0.0
    else:
        return 0.0

class BahdanauAttention(tf.keras.layers.Layer):
    def __init__(self, units):
        super(BahdanauAttention, self).__init__()
        self.W1 = tf.keras.layers.Dense(units)
        self.W2 = tf.keras.layers.Dense(units)
        self.V = tf.keras.layers.Dense(1)

    def call(self, query, values):
        # query shape == (batch_size, hidden_size)
        # values shape == (batch_size, max_len, hidden_size)
        # Adding time axis to query
        query_with_time_axis = tf.expand_dims(query, 1)

        # Calculating score
        score = self.V(tf.nn.tanh(self.W1(query_with_time_axis) + self.W2(values)))

        # Calculating attention weights
        attention_weights = tf.nn.softmax(score, axis=1)

        # Context vector
        context_vector = attention_weights * values
        context_vector = tf.reduce_sum(context_vector, axis=1)

        return context_vector, attention_weights

def create_policy_model():
    inputs = tf.keras.layers.Input(shape=(64,))
    reshaped_inputs = tf.keras.layers.Reshape((8, 8, 1))(inputs)
    conv1 = tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same')(reshaped_inputs)
    conv2 = tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same')(conv1)
    conv3 = tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same')(conv2)
    conv4 = tf.keras.layers.Conv2D(256, (3, 3), activation='relu', padding='same')(conv3)
    lstm_output = tf.keras.layers.LSTM(128, return_sequences=True, dropout=0.5)(conv4)

    # Compute query and values for BahdanauAttention
    query = lstm_output  # Query is the output of the LSTM layer
    values = conv4       # Values are the output of the last Conv2D layer

    # Apply BahdanauAttention
    context_vector, attention_weights = BahdanauAttention(128)(query, values)  # Provide query and values as a list

    # Flatten and Dense layers
    flattened = tf.keras.layers.Flatten()(context_vector)
    dense1 = tf.keras.layers.Dense(256, activation='relu')(flattened)
    dropout = tf.keras.layers.Dropout(0.5)(dense1)
    outputs = tf.keras.layers.Dense(64 * 64, activation='softmax')(dropout)

    model = tf.keras.Model(inputs=inputs, outputs=outputs)
    return model

def train_policy_model(model, states, actions, rewards, metrics_list, optimizer):
    with tf.GradientTape() as tape:
        loss = 0
        for state, action, reward, metrics in zip(states, actions, rewards, metrics_list):
            state = np.array([state])
            action = np.array([action])
            prediction = model(state)
            log_prob = tf.math.log(tf.reduce_sum(prediction * action))
            # Ensure metrics is a scalar value before addition
            scalar_metrics = sum(metrics.values()) / len(metrics)
            loss -= log_prob * (reward + scalar_metrics)
    grads = tape.gradient(loss, model.trainable_variables)
    optimizer.apply_gradients(zip(grads, model.trainable_variables))

def play_game(model, color):
    board = chess.Board()
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)
    
    all_states, all_actions, all_rewards, all_metrics = [], [], [], []
    
    while not board.is_game_over():
        if (board.turn == chess.WHITE and color == chess.WHITE) or (board.turn == chess.BLACK and color == chess.BLACK):
            input_vector = board_to_input(board)
            move = ChessBot(model).select_move(board)
            board.push(move)
            action_vector = encode_move(move)
            all_states.append(input_vector)
            all_actions.append(action_vector)
            print(board)
        else:
            result = engine.play(board, chess.engine.Limit(time=0.1))
            board.push(result.move)
            print()
            print(board)
    
    result = board.result()
    reward = result_to_value(result)
    rewards = [reward] * len(all_states)
    metrics = analyze_board(board, color)
    all_metrics.append(metrics)  # Collect metrics for this game

    # Calculate additional evaluation metrics
    train_policy_model(model, all_states, all_actions, rewards, all_metrics, optimizer)
    engine.quit()

    # Save the game data
    save_game_data(list(zip(all_states, all_actions)), get_next_game_num(game_data_folder), result)
    
    return all_states, all_actions, rewards, all_metrics  # Return all variables collected during the game

def hypermodel_builder(hp):
    inputs = tf.keras.layers.Input(shape=(64,))
    reshaped_inputs = tf.keras.layers.Reshape((8, 8, 1))(inputs)
    conv1 = tf.keras.layers.Conv2D(
        filters=hp.Int('filters_1', min_value=32, max_value=128, step=32),
        kernel_size=hp.Choice('kernel_size_1', values=[3, 5]),
        activation='relu',
        padding='same'
    )(reshaped_inputs)
    conv2 = tf.keras.layers.Conv2D(
        filters=hp.Int('filters_2', min_value=64, max_value=256, step=64),
        kernel_size=hp.Choice('kernel_size_2', values=[3, 5]),
        activation='relu',
        padding='same'
    )(conv1)
    conv3 = tf.keras.layers.Conv2D(
        filters=hp.Int('filters_3', min_value=64, max_value=256, step=64),
        kernel_size=hp.Choice('kernel_size_3', values=[3, 5]),
        activation='relu',
        padding='same'
    )(conv2)
    conv4 = tf.keras.layers.Conv2D(
        filters=hp.Int('filters_4', min_value=128, max_value=512, step=128),
        kernel_size=hp.Choice('kernel_size_4', values=[3, 5]),
        activation='relu',
        padding='same'
    )(conv3)

    # Reshape conv4 output for LSTM input
    conv4_reshaped = tf.keras.layers.Reshape((8 * 8, -1))(conv4)

    # LSTM layer
    lstm_output = tf.keras.layers.LSTM(
        units=hp.Int('lstm_units', min_value=64, max_value=256, step=64),
        return_sequences=True
    )(conv4_reshaped)

    # BahdanauAttention
    query = tf.keras.layers.Lambda(lambda x: x[:, -1, :])(lstm_output)  # Last output of LSTM
    context_vector, attention_weights = BahdanauAttention(128)(query, lstm_output)

    # Flatten and Dense layers
    flattened = tf.keras.layers.Flatten()(context_vector)
    dense1 = tf.keras.layers.Dense(
        units=hp.Int('dense_units', min_value=64, max_value=512, step=64),
        activation='relu'
    )(flattened)
    dropout = tf.keras.layers.Dropout(
        rate=hp.Float('dropout_rate', min_value=0.1, max_value=0.5, step=0.1)
    )(dense1)
    outputs = tf.keras.layers.Dense(64 * 64, activation='softmax')(dropout)

    model = tf.keras.Model(inputs=inputs, outputs=outputs)

    model.compile(
        optimizer=tf.keras.optimizers.Adam(
            learning_rate=hp.Choice('learning_rate', values=[1e-4, 1e-3, 1e-2])
        ),
        loss='categorical_crossentropy'
    )

    return model





# Hyperparameter tuning with Keras Tuner
tuner = kt.Hyperband(
    hypermodel_builder,
    objective='val_loss',
    max_epochs=10,
    factor=3,
    directory='hyperband',
    project_name='chess_ai'
)

# Main training loop
# Load or create the model using the best hyperparameters
tuner.search_space_summary()
tuner.search(
    x=np.zeros((1, 64)),  # Dummy data for search
    y=np.zeros((1, 64 * 64)),  # Dummy data for search
    epochs=5,
    validation_data=(np.zeros((1, 64)), np.zeros((1, 64 * 64)))
)
best_hps = tuner.get_best_hyperparameters(num_trials=1)[0]
model = tuner.hypermodel.build(best_hps)

optimizer = Adam(learning_rate=best_hps.get('learning_rate'))

# Accumulate data from all games across all epochs
all_states, all_actions, all_rewards, all_metrics = [], [], [], []

for epoch in range(10):  # Train for 10 epochs
    for _ in range(10):  # Play 10 games per epoch
        color = random.choice([chess.WHITE, chess.BLACK])  # Randomly choose color for each game
        states, actions, rewards, metrics = play_game(model, color)
        all_states.extend(states)
        all_actions.extend(actions)
        all_rewards.extend(rewards)
        all_metrics.extend(metrics)

    # Print or save additional evaluation metrics if needed
    # For example:
    avg_material_balance = np.mean([metrics['material_balance'] for metrics in all_metrics])
    avg_piece_mobility = np.mean([metrics['piece_mobility'] for metrics in all_metrics])
    avg_piece_coordination = np.mean([metrics['piece_coordination'] for metrics in all_metrics])
    print(f"Epoch {epoch+1}: Average Material Balance: {avg_material_balance}, Average Piece Mobility: {avg_piece_mobility}, Average Piece Coordination: {avg_piece_coordination}")

    # Train the model on collected data after each epoch
    train_policy_model(model, all_states, all_actions, all_rewards, all_metrics, optimizer)

# Save the trained model
model.save(model_path)
print("Training completed.")