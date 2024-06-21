#ifndef CHESS_EVALUATION_H
#define CHESS_EVALUATION_H

#include "board.h"
#include <map>
#include <string>


// Main evaluation functions
std::map<std::string, int> analyze_board(const Board& board, Color color);
std::pair<int, int> evaluate_piece_harmony(const Board& board);

// Detailed evaluation functions
int evaluate_material_balance(const std::vector<char>& board);
double evaluate_piece_mobility(std::vector<char>& board, bool original_turn);


double evaluate_piece_coordination(const Board& board);
double evaluate_pawn_structure(const Board& board);
int evaluate_king_safety(const Board& board, Color color);
int evaluate_tactics(const Board& board);
int evaluate_center_control(const Board& board);
int evaluate_piece_activity(const Board& board);
int calculate_pawn_structure_strength(const Board& board, Color color);
int evaluate_piece_position(const Board& board, Color color);
int evaluate_piece_exchanges(const Board& board, Color color);
int calculate_initiative_and_tempo(const Board& board);

// Utility functions
static int piece_value_for_material_balance(char piece);
double calculate_mobility_bonus(const Board& board, const Piece& piece, int square);

int evaluate_king_safety(const std::vector<char>& board, bool color); 
int evaluate_tactics(const std::vector<char>& board);
bool is_open_file(const std::vector<char>& board, int square);

std::pair<int, int> evaluate_piece_harmony(const std::vector<char>& board);
double calculate_mobility_bonus(const std::vector<char>& board, char piece, int square);
std::vector<int> get_attackers(const std::vector<char>& board, bool color, int square);
#endif // CHESS_EVALUATION_H
