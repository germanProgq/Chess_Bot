#include "board.h"

// Constructor definition
Board::Board() {
    // Initialize the board with a default position
    set_position("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR");
}

// Set board position from FEN string
void Board::set_position(const std::string& fen) {
    std::istringstream iss(fen);
    std::string rank;
    int row = 0;

    while (std::getline(iss, rank, '/')) {
        int col = 0;
        for (char c : rank) {
            if (std::isdigit(c)) {
                int empty = c - '0';
                for (int i = 0; i < empty; ++i) {
                    squares[row * 8 + col].type = ' '; // Empty square
                    squares[row * 8 + col].color = WHITE; // Default color for empty square
                    ++col;
                }
            }
            else {
                squares[row * 8 + col].type = c;
                squares[row * 8 + col].color = (std::isupper(c) ? WHITE : BLACK);
                ++col;
            }
        }
        ++row;
    }
}

// Get piece at a specific square
Piece Board::piece_at(int square) const {
    return squares[square];
}

// Get color at a specific square
Color Board::color_at(int square) const {
    return squares[square].color ? WHITE : BLACK;
}

// Find the king's square for a given color
int Board::king(bool color) const {
    char king_char = (color == WHITE ? 'K' : 'k');
    for (int i = 0; i < 64; ++i) {
        if (squares[i].type == king_char) {
            return i;
        }
    }
    return -1; // Return -1 if king not found (though it should always be found)
}

// Find attackers for a given square and color
std::list<int> Board::attackers(bool color, int square) const {
    std::list<int> attacking_pieces;
    for (int i = 0; i < 64; ++i) {
        if (squares[i].type != ' ' && squares[i].color != color) {
            // Check if this piece attacks the square
            switch (squares[i].type) {
            case 'P':
                if (squares[i].color == WHITE) {
                    if (i - 9 >= 0 && (i - 9) % 8 != 7 && i - 9 == square)
                        attacking_pieces.push_back(i);
                    if (i - 7 >= 0 && (i - 7) % 8 != 0 && i - 7 == square)
                        attacking_pieces.push_back(i);
                }
                else {
                    if (i + 9 < 64 && (i + 9) % 8 != 0 && i + 9 == square)
                        attacking_pieces.push_back(i);
                    if (i + 7 < 64 && (i + 7) % 8 != 7 && i + 7 == square)
                        attacking_pieces.push_back(i);
                }
                break;
            case 'N':
                if (i - 17 == square || i - 15 == square || i - 10 == square || i - 6 == square || i + 6 == square || i + 10 == square || i + 15 == square || i + 17 == square)
                    attacking_pieces.push_back(i);
                break;
            case 'B':
                if ((square % 8 - i % 8 == square / 8 - i / 8) || (square % 8 - i % 8 == i / 8 - square / 8))
                    attacking_pieces.push_back(i);
                break;
            case 'R':
                if (square / 8 == i / 8 || square % 8 == i % 8)
                    attacking_pieces.push_back(i);
                break;
            case 'Q':
                if ((square / 8 == i / 8 || square % 8 == i % 8) || (square % 8 - i % 8 == square / 8 - i / 8) || (square % 8 - i % 8 == i / 8 - square / 8))
                    attacking_pieces.push_back(i);
                break;
            case 'K':
                if (abs(square / 8 - i / 8) <= 1 && abs(square % 8 - i % 8) <= 1)
                    attacking_pieces.push_back(i);
                break;
            }
        }
    }
    return attacking_pieces;
}
