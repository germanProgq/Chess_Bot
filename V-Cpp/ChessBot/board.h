#ifndef BOARD_H
#define BOARD_H

#include <array>
#include <list>
#include <vector>
#include <sstream>
#include <cctype>

enum Color { WHITE, BLACK };

// Constants for piece values
const int PAWN_VALUE = 1;
const int KNIGHT_VALUE = 3;
const int BISHOP_VALUE = 3;
const int ROOK_VALUE = 5;
const int QUEEN_VALUE = 9;

const int BOARD_SIZE = 8;
const std::vector<int> KNIGHT_MOVES = { 15, 17, -15, -17, 10, -10, 6, -6 };
const std::vector<int> KING_MOVES = { 1, -1, 8, -8, 9, -9, 7, -7 };
const std::vector<int> ROOK_MOVES = { 1, -1, 8, -8 };
const std::vector<int> BISHOP_MOVES = { 9, -9, 7, -7 };
const std::vector<int> QUEEN_MOVES = { 1, -1, 8, -8, 9, -9, 7, -7 };

int piece_value_for_material_balance(char piece) {
    switch (piece) {
    case 'P': return PAWN_VALUE; // White Pawn
    case 'N': return KNIGHT_VALUE; // White Knight
    case 'B': return BISHOP_VALUE; // White Bishop
    case 'R': return ROOK_VALUE; // White Rook
    case 'Q': return QUEEN_VALUE; // White Queen
    case 'p': return PAWN_VALUE; // Black Pawn
    case 'n': return KNIGHT_VALUE; // Black Knight
    case 'b': return BISHOP_VALUE; // Black Bishop
    case 'r': return ROOK_VALUE; // Black Rook
    case 'q': return QUEEN_VALUE; // Black Queen
    default: return 0;
    }
}

// Center and key squares
const std::vector<int> CENTER_SQUARES = { 27, 28, 35, 36 }; // D4, E4, D5, E5
const std::vector<int> KEY_SQUARES = { 18, 19, 20, 21, 26, 29, 30, 31, 34, 37, 42, 43, 44, 45 }; // Surrounding center squares

// Define the structure for a chess piece
struct Piece {
    char type; // ' ' for empty square, 'P', 'N', 'B', 'R', 'Q', 'K' for pieces
    bool color; // true for white, false for black
};

// Define the structure for a chessboard
class Board {
private:
    bool turn; // true for white's turn, false for black's turn

public:
    std::array<Piece, 64> squares;
    Board(); // Constructor
    void set_position(const std::string& fen); // Set board position from FEN string
    Piece piece_at(int square) const; // Get piece at a specific square
    Color color_at(int square) const; // Get color at a specific square
    int king(bool color) const; // Find the king's square
    std::list<int> attackers(bool color, int square) const; // Find attackers for a square
};

#endif // BOARD_H
