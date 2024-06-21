#include "chess_evaluation.h"
#include "board.h"
#include <iostream>

int main() {
    // Initialize a board
    Board board;
    // Assume the board is initialized with pieces...

    // Analyze the board for white pieces
    auto evaluation = analyze_board(board, WHITE);

    // Print out the evaluation results
    std::cout << "Evaluation for White:" << std::endl;
    std::cout << "Material Balance: " << evaluation["material_balance"] << std::endl;
    std::cout << "Piece Mobility: " << evaluation["piece_mobility"] << std::endl;
    std::cout << "Piece Coordination: " << evaluation["piece_coordination"] << std::endl;
    std::cout << "Pawn Structure: " << evaluation["pawn_structure"] << std::endl;
    std::cout << "King Safety: " << evaluation["king_safety"] << std::endl;
    std::cout << "Control of Center: " << evaluation["control_of_center"] << std::endl;
    std::cout << "Piece Activity: " << evaluation["piece_activity"] << std::endl;
    std::cout << "Space Control: " << evaluation["space_control"] << std::endl;
    std::cout << "Pawn Structure Strength: " << evaluation["pawn_structure_strength"] << std::endl;
    std::cout << "Piece Placement: " << evaluation["piece_placement"] << std::endl;
    std::cout << "Piece Exchange: " << evaluation["piece_exchange"] << std::endl;
    std::cout << "Tempo: " << evaluation["tempo"] << std::endl;

    // Evaluate piece harmony separately
    auto harmony_scores = evaluate_piece_harmony(board);
    std::cout << "White Harmony Score: " << harmony_scores.first << std::endl;
    std::cout << "Black Harmony Score: " << harmony_scores.second << std::endl;

    return 0;
}
