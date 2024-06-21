#include "chess_evaluation.h"
#include "board.h"
#include <algorithm>
#include <iostream>
#include <cmath>
#include <vector>
#include <cctype>

std::map<std::string, int> analyze_board(const Board& board, Color color) {
    int material_balance = evaluate_material_balance(board);
    double piece_mobility = evaluate_piece_mobility(board);
    double piece_coordination = evaluate_piece_coordination(board);
    double pawn_structure = evaluate_pawn_structure(board);
    int king_safety = evaluate_king_safety(board, color);
    int control_of_center = evaluate_center_control(board);
    int piece_activity = evaluate_piece_activity(board);
    int space_control = 0; // Placeholder for evaluate_space_control(board)
    int pawn_structure_strength = calculate_pawn_structure_strength(board, color);
    int piece_placement = evaluate_piece_position(board, color);
    int piece_exchange = evaluate_piece_exchanges(board, color);
    int tempo = calculate_initiative_and_tempo(board);

    if (color == BLACK) {
        material_balance = -material_balance;
        piece_mobility = -piece_mobility;
        piece_coordination = -piece_coordination;
        pawn_structure = -pawn_structure;
        control_of_center = -control_of_center;
        piece_activity = -piece_activity;
        tempo = -tempo;
    }

    return {
        {"material_balance", material_balance},
        {"piece_mobility", static_cast<int>(piece_mobility)},
        {"piece_coordination", static_cast<int>(piece_coordination)},
        {"pawn_structure", static_cast<int>(pawn_structure)},
        {"king_safety", king_safety},
        {"control_of_center", control_of_center},
        {"piece_activity", piece_activity},
        {"space_control", space_control},
        {"pawn_structure_strength", pawn_structure_strength},
        {"piece_placement", piece_placement},
        {"piece_exchange", piece_exchange},
        {"tempo", tempo}
    };
}


//Main
int evaluate_material_balance(const std::vector<char>& board) {
    int white_material = 0;
    int black_material = 0;

    for (int square = 0; square < board.size(); ++square) {
        char piece = board[square];
        if (piece != ' ') {
            if (isupper(piece)) {
                white_material += piece_value_for_material_balance(piece);
            }
            else {
                black_material += piece_value_for_material_balance(piece);
            }
        }
    }

    int material_balance_score = white_material - black_material;

    return material_balance_score;
}
double evaluate_piece_mobility(std::vector<char>& board, bool original_turn) {
    // 1. Number of legal moves for each side
    int white_mobility = count_legal_moves(board, true);  // Implement count_legal_moves for white
    int black_mobility = count_legal_moves(board, false); // Implement count_legal_moves for black
    int mobility_score = white_mobility - black_mobility;

    // 2. Centralization of pieces
    int white_centralization = 0;
    int black_centralization = 0;
    for (int square = 0; square < board.size(); ++square) {
        char piece = board[square];
        if (piece != ' ') {
            if (isupper(piece) && std::find(CENTER_SQUARES.begin(), CENTER_SQUARES.end(), square) != CENTER_SQUARES.end()) {
                white_centralization++;
            }
            else if (islower(piece) && std::find(CENTER_SQUARES.begin(), CENTER_SQUARES.end(), square) != CENTER_SQUARES.end()) {
                black_centralization++;
            }
        }
    }
    int centralization_score = white_centralization - black_centralization;

    // 3. Control over important squares
    int white_control_center = 0;
    int black_control_center = 0;
    for (int square : CENTER_SQUARES) {
        if (isupper(board[square])) {
            white_control_center++;
        }
        else if (islower(board[square])) {
            black_control_center++;
        }
    }
    int center_control_score = white_control_center - black_control_center;

    // 4. Piece coordination and potential for piece exchanges
    int white_piece_coordination = 0;
    int black_piece_coordination = 0;
    for (int square = 0; square < board.size(); ++square) {
        char piece = board[square];
        if (piece != ' ') {
            if (isupper(piece)) {
                white_piece_coordination++;
            }
            else {
                black_piece_coordination++;
            }
        }
    }
    int piece_coordination_score = white_piece_coordination - black_piece_coordination;

    // 5. Pawn structure and its impact on piece mobility
    int white_pawn_structure = 0;
    int black_pawn_structure = 0;
    for (int square = 0; square < board.size(); ++square) {
        char piece = board[square];
        if (piece != ' ') {
            if (piece == 'P') {
                white_pawn_structure++;
            }
            else if (piece == 'p') {
                black_pawn_structure++;
            }
        }
    }
    int pawn_structure_score = white_pawn_structure - black_pawn_structure;

    // 6. Open lines and diagonals for rooks, bishops, and queens
    int white_open_lines = 0;
    int black_open_lines = 0;
    for (int square = 0; square < board.size(); ++square) {
        char piece = board[square];
        if (piece != ' ') {
            if (isupper(piece) && (piece == 'R' || piece == 'B' || piece == 'Q') && is_open_file(board, square)) {
                white_open_lines++;
            }
            else if (islower(piece) && (piece == 'r' || piece == 'b' || piece == 'q') && is_open_file(board, square)) {
                black_open_lines++;
            }
        }
    }
    int open_lines_score = white_open_lines - black_open_lines;

    // 7. Connectivity between pieces and king safety
    int white_king_safety = evaluate_king_safety(board, true);
    int black_king_safety = evaluate_king_safety(board, false);
    int connectivity_score = white_king_safety - black_king_safety;

    // 8. Tactical threats and opportunities
    int white_tactics = evaluate_tactics(board);
    std::vector<char> mirrored_board = mirror_board(board);  // Implement mirror_board function
    int black_tactics = evaluate_tactics(mirrored_board);
    int tactics_score = white_tactics - black_tactics;

    // Combine all scores with appropriate weights
    double total_score = (
        0.2 * mobility_score +
        0.1 * centralization_score +
        0.1 * center_control_score +
        0.1 * piece_coordination_score +
        0.1 * pawn_structure_score +
        0.1 * open_lines_score +
        0.15 * connectivity_score +
        0.15 * tactics_score
        );

    return static_cast<int>(total_score);
}
double evaluate_piece_coordination(const std::vector<char>& board) {
    double white_coordination = 0.0;
    double black_coordination = 0.0;

    // Evaluate piece harmony
    std::pair<int, int> harmony_scores = evaluate_piece_harmony(board);
    int white_harmony = harmony_scores.first;
    int black_harmony = harmony_scores.second;

    white_coordination += white_harmony;
    black_coordination += black_harmony;

    // Iterate through all squares
    for (int square = 0; square < board.size(); ++square) {
        char piece = board[square];
        if (piece != ' ') {
            // Find attackers and defenders
            bool piece_color = isupper(piece);
            std::vector<int> attackers = get_attackers(board, piece_color, square);
            std::vector<int> defenders = get_attackers(board, !piece_color, square);

            // Calculate support value based on number of attackers and defenders
            double support_value = attackers.size() - defenders.size();

            // Bonus for centralized pieces
            if (std::find(CENTER_SQUARES.begin(), CENTER_SQUARES.end(), square) != CENTER_SQUARES.end()) {
                support_value += 0.5;
            }

            // Bonus for control of key squares
            if (std::find(KEY_SQUARES.begin(), KEY_SQUARES.end(), square) != KEY_SQUARES.end()) {
                support_value += 0.5;
            }

            // Penalty for being attacked
            if (!attackers.empty() && defenders.empty()) {
                support_value -= 0.5;
            }

            // Additional bonus for future mobility potential
            double mobility_bonus = calculate_mobility_bonus(board, piece, square);
            support_value += mobility_bonus;

            // Update coordination score based on piece color
            if (piece_color) {
                white_coordination += support_value;
            }
            else {
                black_coordination += support_value;
            }
        }
    }

    // Normalize coordination scores
    double max_score = std::max(white_coordination, black_coordination);
    if (max_score != 0) {
        white_coordination /= max_score;
        black_coordination /= max_score;
    }

    return white_coordination - black_coordination;
}









static int piece_value_for_material_balance(char piece) {
    switch (piece) {
    case 'P': case 'p': return PAWN_VALUE;
    case 'N': case 'n': return KNIGHT_VALUE;
    case 'B': case 'b': return BISHOP_VALUE;
    case 'R': case 'r': return ROOK_VALUE;
    case 'Q': case 'q': return QUEEN_VALUE;
    default: return 0;
    }
}

std::pair<int, int> evaluate_piece_harmony(const Board& board) {
    int white_harmony_score = 0;
    int black_harmony_score = 0;

    white_harmony_score += calculate_color_coordination(board, WHITE);
    black_harmony_score += calculate_color_coordination(board, BLACK);
    white_harmony_score += calculate_key_square_control(board, WHITE);
    black_harmony_score += calculate_key_square_control(board, BLACK);
    white_harmony_score += calculate_central_support(board, WHITE);
    black_harmony_score += calculate_central_support(board, BLACK);
    white_harmony_score += calculate_rook_coordination(board, WHITE);
    black_harmony_score += calculate_rook_coordination(board, BLACK);
    white_harmony_score += evaluate_pawn_structure_score(board, WHITE);
    black_harmony_score += evaluate_pawn_structure_score(board, BLACK);
    white_harmony_score += calculate_threat_coordination(board, WHITE);
    black_harmony_score += calculate_threat_coordination(board, BLACK);
    white_harmony_score += calculate_mobility_coordination(board, WHITE);
    black_harmony_score += calculate_mobility_coordination(board, BLACK);
    white_harmony_score += calculate_piece_value_awareness(board, WHITE);
    black_harmony_score += calculate_piece_value_awareness(board, BLACK);
    white_harmony_score += calculate_positional_features(board, WHITE);
    black_harmony_score += calculate_positional_features(board, BLACK);
    white_harmony_score += calculate_tactical_utilization(board, WHITE);
    black_harmony_score += calculate_tactical_utilization(board, BLACK);

    return { white_harmony_score, black_harmony_score };
}





std::vector<char> mirror_board(const std::vector<char>& board) {
    std::vector<char> mirrored_board(board.size());
    for (int i = 0; i < board.size(); ++i) {
        int mirrored_index = board.size() - 1 - i;
        char piece = board[i];
        if (piece != ' ') {
            if (isupper(piece)) {
                mirrored_board[mirrored_index] = tolower(piece);
            }
            else {
                mirrored_board[mirrored_index] = toupper(piece);
            }
        }
        else {
            mirrored_board[mirrored_index] = ' ';
        }
    }
    return mirrored_board;
}

// Convert board position to 1D index
int to_index(int row, int col) {
    return row * BOARD_SIZE + col;
}

// Check if a position is within the board
bool is_within_board(int row, int col) {
    return row >= 0 && row < BOARD_SIZE && col >= 0 && col < BOARD_SIZE;
}

// Check if a position is within the board (1D version)
bool is_within_board(int index) {
    return index >= 0 && index < BOARD_SIZE * BOARD_SIZE;
}

// Generate all possible moves for a piece
std::vector<int> generate_moves(const std::vector<char>& board, int square) {
    std::vector<int> moves;
    char piece = board[square];
    int row = square / BOARD_SIZE;
    int col = square % BOARD_SIZE;

    if (toupper(piece) == 'N') {
        for (int move : KNIGHT_MOVES) {
            int new_square = square + move;
            if (is_within_board(new_square) && (board[new_square] == ' ' || isupper(board[new_square]) != isupper(piece))) {
                moves.push_back(new_square);
            }
        }
    }
    else if (toupper(piece) == 'K') {
        for (int move : KING_MOVES) {
            int new_square = square + move;
            if (is_within_board(new_square) && (board[new_square] == ' ' || isupper(board[new_square]) != isupper(piece))) {
                moves.push_back(new_square);
            }
        }
    }
    else if (toupper(piece) == 'R') {
        for (int move : ROOK_MOVES) {
            int new_square = square + move;
            while (is_within_board(new_square) && board[new_square] == ' ') {
                moves.push_back(new_square);
                new_square += move;
            }
            if (is_within_board(new_square) && isupper(board[new_square]) != isupper(piece)) {
                moves.push_back(new_square);
            }
        }
    }
    else if (toupper(piece) == 'B') {
        for (int move : BISHOP_MOVES) {
            int new_square = square + move;
            while (is_within_board(new_square) && board[new_square] == ' ') {
                moves.push_back(new_square);
                new_square += move;
            }
            if (is_within_board(new_square) && isupper(board[new_square]) != isupper(piece)) {
                moves.push_back(new_square);
            }
        }
    }
    else if (toupper(piece) == 'Q') {
        for (int move : QUEEN_MOVES) {
            int new_square = square + move;
            while (is_within_board(new_square) && board[new_square] == ' ') {
                moves.push_back(new_square);
                new_square += move;
            }
            if (is_within_board(new_square) && isupper(board[new_square]) != isupper(piece)) {
                moves.push_back(new_square);
            }
        }
    }
    else if (toupper(piece) == 'P') {
        int direction = isupper(piece) ? -1 : 1;
        int start_row = isupper(piece) ? 6 : 1;
        int end_row = isupper(piece) ? 0 : 7;
        int move_one = square + direction * BOARD_SIZE;
        int move_two = square + direction * 2 * BOARD_SIZE;

        // Single move forward
        if (is_within_board(move_one) && board[move_one] == ' ') {
            moves.push_back(move_one);
            // Double move forward
            if ((row == start_row) && board[move_two] == ' ') {
                moves.push_back(move_two);
            }
        }

        // Capture moves
        int capture_left = square + direction * (BOARD_SIZE - 1);
        int capture_right = square + direction * (BOARD_SIZE + 1);
        if (is_within_board(capture_left) && board[capture_left] != ' ' && isupper(board[capture_left]) != isupper(piece)) {
            moves.push_back(capture_left);
        }
        if (is_within_board(capture_right) && board[capture_right] != ' ' && isupper(board[capture_right]) != isupper(piece)) {
            moves.push_back(capture_right);
        }
    }

    return moves;
}

// Function to simulate a move on the board
std::vector<char> simulate_move(const std::vector<char>& board, int from_square, int to_square) {
    std::vector<char> new_board = board;
    new_board[to_square] = new_board[from_square];
    new_board[from_square] = ' ';
    return new_board;
}

// Function to find the king's position
static int find_king(const std::vector<char>& board, bool color) {
    char king = color ? 'K' : 'k';
    for (int i = 0; i < board.size(); ++i) {
        if (board[i] == king) {
            return i;
        }
    }
    return -1; // King not found
}

// Function to check if a square is attacked
static bool is_square_attacked(const std::vector<char>& board, int square, bool color) {
    for (int i = 0; i < board.size(); ++i) {
        char piece = board[i];
        if (piece != ' ' && isupper(piece) != color) {
            std::vector<int> attacks = generate_moves(board, i);
            if (std::find(attacks.begin(), attacks.end(), square) != attacks.end()) {
                return true;
            }
        }
    }
    return false;
}

// Check if a move is legal
static bool is_legal_move(const std::vector<char>& board, int from_square, int to_square, bool color) {
    std::vector<char> new_board = simulate_move(board, from_square, to_square);
    int king_pos = find_king(new_board, color);
    if (king_pos == -1 || is_square_attacked(new_board, king_pos, !color)) {
        return false;
    }
    return true;
}

// Function to count legal moves for a given color
static int count_legal_moves(const std::vector<char>& board, bool color) {
    int legal_moves_count = 0;
    for (int square = 0; square < board.size(); ++square) {
        char piece = board[square];
        if (piece != ' ' && (isupper(piece) == color)) {
            std::vector<int> moves = generate_moves(board, square);
            for (int move : moves) {
                if (is_legal_move(board, square, move, color)) {
                    ++legal_moves_count;
                }
            }
        }
    }
    return legal_moves_count;
};