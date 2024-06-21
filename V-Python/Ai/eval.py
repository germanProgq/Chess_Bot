import chess
import chess.engine
import numpy as np

CENTER_SQUARES = [chess.A4, chess.B4, chess.C4, chess.D4, chess.E4, chess.F4, chess.G4, chess.H4,
                  chess.A5, chess.B5, chess.C5, chess.D5, chess.E5, chess.F5, chess.G5, chess.H5,
                  chess.A3, chess.B3, chess.C3, chess.D3, chess.E3, chess.F3, chess.G3, chess.H3,
                  chess.A6, chess.B6, chess.C6, chess.D6, chess.E6, chess.F6, chess.G6, chess.H6]

def analyze_board(board, color):
    material_balance = evaluate_material_balance(board) #Done
    piece_mobility = evaluate_piece_mobility(board) #Done
    piece_coordination = evaluate_piece_coordination(board) #Progress
    pawn_structure = evaluate_pawn_structure(board) #Done
    king_safety = evaluate_king_safety(board, color) #Done
    control_of_center = evaluate_center_control(board) #Done
    piece_activity = evaluate_piece_activity(board) #Done
    space_control =  0 #evaluate_space_control(board)#Progress
    pawn_structure_strength = calculate_pawn_structure_strength(board, color) #Done
    piece_placement = evaluate_piece_position(board, color) #Done
    piece_exchange = evaluate_piece_exchanges(board, color) #Done
    tempo = calculate_initiative_and_tempo(board) #Done

    if (color == chess.BLACK):
        material_balance = - (material_balance)
        piece_mobility = - (piece_mobility)
        piece_coordination = - (piece_coordination)
        pawn_structure = - (pawn_structure)
        control_of_center = - (control_of_center)
        piece_activity = - (piece_activity)
        tempo = - (tempo)
    
    return {
        'material_balance': material_balance,
        'piece_mobility': piece_mobility,
        'piece_coordination': piece_coordination,
        'pawn_structure': pawn_structure,
        'king_safety': king_safety,
        'control_of_center': control_of_center,
        'piece_activity': piece_activity,
        'space_control': space_control,
        'pawn_structure_strength': pawn_structure_strength,
        'piece_placement': piece_placement,
        'piece_exchange': piece_exchange,
        'tempo': tempo
    }


#Main Functions
def evaluate_material_balance(board):
    """
    Evaluate the material balance on the board along with other factors.
    
    Factors Considered:
    1. Total material count for each side.
    2. Piece values: Pawn = 1, Knight = 3, Bishop = 3, Rook = 5, Queen = 9.
    3. Piece positioning: Centralization and mobility.
    4. Pawn structure: Doubled, isolated, and backward pawns.
    5. King safety: Presence of pawn shield and open files around the king.
    6. Potential threats: Active pieces and attacking opportunities.
    
    Positive scores indicate a material advantage for white,
    negative scores indicate a material advantage for black.
    """
    white_material = 0
    black_material = 0
    
    # Count material for each side
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            if piece.color == chess.WHITE:
                white_material += piece_value_for_material_balance(piece)
            else:
                black_material += piece_value_for_material_balance(piece)
    
    # Calculate material balance score
    material_balance_score = white_material - black_material
    
    return material_balance_score

def evaluate_piece_mobility(board):
    """
    Evaluate the piece mobility on the board.
    
    Factors Considered:
    1. Number of legal moves for each side.
    2. Centralization of pieces.
    3. Control over important squares (e.g., center).
    4. Piece coordination and potential for piece exchanges.
    5. Pawn structure and its impact on piece mobility.
    6. Open lines and diagonals for rooks, bishops, and queens.
    7. Connectivity between pieces and king safety.
    8. Tactical threats and opportunities.
    
    Positive scores indicate better mobility for white,
    negative scores indicate better mobility for black.
    """
    original_turn = board.turn

    # 1. Number of legal moves for each side
    white_mobility = len(list(board.legal_moves))
    board.turn = chess.BLACK
    black_mobility = len(list(board.legal_moves))
    board.turn = original_turn

    mobility_score = white_mobility - black_mobility

    # 2. Centralization of pieces
    white_centralization = sum(1 for square in chess.SQUARES if board.piece_at(square) and board.piece_at(square).color == chess.WHITE and square in CENTER_SQUARES)
    black_centralization = sum(1 for square in chess.SQUARES if board.piece_at(square) and board.piece_at(square).color == chess.BLACK and square in CENTER_SQUARES)
    centralization_score = white_centralization - black_centralization

    # 3. Control over important squares
    white_control_center = sum(1 for square in CENTER_SQUARES if board.color_at(square) == chess.WHITE)
    black_control_center = sum(1 for square in CENTER_SQUARES if board.color_at(square) == chess.BLACK)
    center_control_score = white_control_center - black_control_center

    # 4. Piece coordination and potential for piece exchanges
    white_piece_coordination = sum(1 for square in chess.SQUARES if board.piece_at(square) and board.piece_at(square).color == chess.WHITE)
    black_piece_coordination = sum(1 for square in chess.SQUARES if board.piece_at(square) and board.piece_at(square).color == chess.BLACK)
    piece_coordination_score = white_piece_coordination - black_piece_coordination

    # 5. Pawn structure and its impact on piece mobility
    white_pawn_structure = sum(1 for square in chess.SQUARES if board.piece_at(square) and board.piece_at(square).color == chess.WHITE and board.piece_at(square).piece_type == chess.PAWN)
    black_pawn_structure = sum(1 for square in chess.SQUARES if board.piece_at(square) and board.piece_at(square).color == chess.BLACK and board.piece_at(square).piece_type == chess.PAWN)
    pawn_structure_score = white_pawn_structure - black_pawn_structure

    # 6. Open lines and diagonals for rooks, bishops, and queens
    white_open_lines = sum(1 for square in chess.SQUARES if board.piece_at(square) and board.piece_at(square).color == chess.WHITE and board.piece_at(square).piece_type in [chess.ROOK, chess.BISHOP, chess.QUEEN] and is_open_file(board, square))
    black_open_lines = sum(1 for square in chess.SQUARES if board.piece_at(square) and board.piece_at(square).color == chess.BLACK and board.piece_at(square).piece_type in [chess.ROOK, chess.BISHOP, chess.QUEEN] and is_open_file(board, square))
    open_lines_score = white_open_lines - black_open_lines

    # 7. Connectivity between pieces and king safety
    white_king_safety = evaluate_king_safety(board, chess.WHITE)
    black_king_safety = evaluate_king_safety(board, chess.BLACK)
    connectivity_score = white_king_safety - black_king_safety

    # 8. Tactical threats and opportunities
    white_tactics = evaluate_tactics(board)
    black_tactics = evaluate_tactics(board.mirror())
    tactics_score = white_tactics - black_tactics

    # Combine all scores with appropriate weights
    total_score = (
        0.2 * mobility_score +
        0.1 * centralization_score +
        0.1 * center_control_score +
        0.1 * piece_coordination_score +
        0.1 * pawn_structure_score +
        0.1 * open_lines_score +
        0.15 * connectivity_score +
        0.15 * tactics_score
    )

    return total_score

def evaluate_king_safety(board, color):
    """
    Evaluate the safety of the king on the board.
    
    Factors Considered:
    1. Pawn cover around the king.
    2. Presence of attackers near the king.
    3. Open files in front of the king.
    4. Strength of the pawn shield in front of the king.
    5. Mobility of the king.
    
    Higher scores indicate a safer king position.
    """
    king_square = board.king(color)  # Get the square of the king for the given color

    # Factors Considered:
    pawn_cover_score = evaluate_pawn_cover(board, king_square)
    attackers_score = evaluate_attackers(board, king_square)  # Ensure this function is defined
    open_files_score = evaluate_open_files(board, king_square)
    pawn_shield_score = evaluate_pawn_shield(board, king_square)
    king_mobility_score = evaluate_king_mobility(board, king_square)

    # Combine individual scores to get the overall safety score
    safety_score = (pawn_cover_score + attackers_score + open_files_score +
                    pawn_shield_score + king_mobility_score)

    return safety_score

def evaluate_pawn_structure(board):
    """
    Evaluate the pawn structure on the board.
    """
    white_pawn_structure_score = evaluate_pawn_structure_score(board, chess.WHITE)
    black_pawn_structure_score = evaluate_pawn_structure_score(board, chess.BLACK)
    pawn_structure_score = white_pawn_structure_score - black_pawn_structure_score
    
    # Additional complexity
    white_pawn_structure_strength = calculate_pawn_structure_strength(board, chess.WHITE)
    black_pawn_structure_strength = calculate_pawn_structure_strength(board, chess.BLACK)
    pawn_structure_strength = white_pawn_structure_strength - black_pawn_structure_strength
    
    white_pawn_mobility = calculate_pawn_mobility(board, chess.WHITE)
    black_pawn_mobility = calculate_pawn_mobility(board, chess.BLACK)
    pawn_mobility = white_pawn_mobility - black_pawn_mobility
    
    white_pawn_breaks = calculate_pawn_breaks(board, chess.WHITE)
    black_pawn_breaks = calculate_pawn_breaks(board, chess.BLACK)
    pawn_breaks = white_pawn_breaks - black_pawn_breaks

    evaluation =   0.4 * pawn_structure_score + 0.3 * pawn_structure_strength +0.2 * pawn_mobility + 0.1 * pawn_breaks
    
    return evaluation

def eval_passed_pawns(board, color):
    """
    Determine passed pawns for the given color on the board.
    """
    passed_pawn_count = 0
    
    for square in chess.scan_reversed(chess.PAWN & board.occupied_co[color]):
        if color == chess.WHITE:
            target_rank = chess.square_rank(square) + 1
        else:
            target_rank = chess.square_rank(square) - 1
        
        target_squares = chess.SquareSet(chess.SQUARES_180[8 * target_rank:8 * (target_rank + 1)])
        
        if not target_squares & board.pawns:
            passed_pawn_count += 1
    
    return passed_pawn_count

def evaluate_center_control(board):
    """
    Evaluate the control of center squares on the board.
    More control over central squares results in a higher score.
    """
    white_control = 0
    black_control = 0
    
    # Central squares
    center_squares = [chess.E4, chess.D4, chess.E5, chess.D5]
    
    # Adjacent squares
    adjacent_squares = [chess.C3, chess.E3, chess.C4, chess.C5, chess.E4, chess.C5, chess.C6, chess.E6]
    
    # Piece activity and coordination around center squares
    for square in center_squares:
        white_attackers = board.attackers_mask(chess.WHITE, square)
        black_attackers = board.attackers_mask(chess.BLACK, square)
        
        # Count white pieces attacking center squares
        white_control += bin(white_attackers).count('1') * 0.5
        
        # Count black pieces attacking center squares
        black_control += bin(black_attackers).count('1') * 0.5
    
    # Check control of central squares and adjacent squares
    for square in center_squares + adjacent_squares:
        if board.attackers_mask(chess.WHITE, square):
            white_control += 1
        elif board.attackers_mask(chess.BLACK, square):
            black_control += 1
    
    # Evaluate pawn structure around center squares
    for square in center_squares:
        if board.piece_at(square) and board.piece_at(square).piece_type == chess.PAWN:
            if board.piece_at(square).color == chess.WHITE:
                white_control += 0.25  # Increase control score for each white pawn on center square
            else:
                black_control += 0.25  # Increase control score for each black pawn on center square
    
    # Evaluate potential future control over center squares
    # Analyze which pieces see which squares around the center
    for square in center_squares:
        piece = board.piece_at(square)
        if piece:
            attackers = board.attackers_mask(not piece.color, square)
            if attackers:
                if piece.color == chess.WHITE:
                    white_control += 0.5  # Increase control score for white pieces under attack
                else:
                    black_control += 0.5  # Increase control score for black pieces under attack
    
    return white_control - black_control

def evaluate_piece_activity(board):
    """
    Evaluate piece activity and mobility.
    
    Factors Considered:
    1. Number of legal moves for each side.
    2. Centralization of pieces.
    3. Control over important squares (e.g., center).
    """
    original_turn = board.turn
    
    # Number of legal moves for each side
    white_mobility = len(list(board.legal_moves))
    board.turn = chess.BLACK
    black_mobility = len(list(board.legal_moves))
    board.turn = original_turn
    
    mobility_score = white_mobility - black_mobility

    # Centralization of pieces
    center_squares = [chess.E4, chess.D4, chess.E5, chess.D5]
    white_centralization = sum(1 for square in chess.SQUARES if board.piece_at(square) and board.piece_at(square).color == chess.WHITE and square in center_squares)
    black_centralization = sum(1 for square in chess.SQUARES if board.piece_at(square) and board.piece_at(square).color == chess.BLACK and square in center_squares)
    centralization_score = white_centralization - black_centralization

    # Control over important squares
    white_control_center = sum(1 for square in center_squares if board.color_at(square) == chess.WHITE)
    black_control_center = sum(1 for square in center_squares if board.color_at(square) == chess.BLACK)
    center_control_score = white_control_center - black_control_center

    return mobility_score * 0.5 + centralization_score * 0.3 + center_control_score * 0.2

def evaluate_piece_coordination(board):
    """
    Evaluate the coordination between pieces on the board.
    Higher scores indicate better coordination and mutual support among pieces.
    """
    key_squares = list(chess.SquareSet(chess.BB_RANK_4 | chess.BB_RANK_5 | chess.BB_RANK_6))
    white_coordination = 0
    black_coordination = 0
    
    # Evaluate piece harmony
    white_harmony, black_harmony = evaluate_piece_harmony(board)
    white_coordination += white_harmony
    black_coordination += black_harmony
    
    # Iterate through all squares
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            # Find attackers and defenders
            attackers = list(board.attackers(piece.color, square))
            defenders = list(board.attackers(not piece.color, square))
            
            # Calculate support value based on number of attackers and defenders
            support_value = len(attackers) - len(defenders)
            
            # Bonus for centralized pieces
            if square in CENTER_SQUARES:
                support_value += 0.5
            
            # Bonus for control of key squares
            if square in key_squares:
                support_value += 0.5
            
            # Penalty for being attacked
            if attackers and not defenders:
                support_value -= 0.5
            
            # Additional bonus for future mobility potential
            mobility_bonus = calculate_mobility_bonus(board, piece, square)
            support_value += mobility_bonus
            
            # Update coordination score based on piece color
            if piece.color == chess.WHITE:
                white_coordination += support_value
            else:
                black_coordination += support_value
    
    # Normalize coordination scores
    max_score = max(white_coordination, black_coordination)
    if max_score != 0:
        white_coordination /= max_score
        black_coordination /= max_score
    
    return white_coordination - black_coordination



#Additional Calculation functions

def evaluate_piece_harmony(board):
    """
    Evaluate the harmony and coordination between pieces on the board.
    
    Factors Considered:
    1. Coordination between pieces of the same color.
    2. Control of key squares and lines by coordinated pieces.
    3. Support of central squares by minor pieces.
    4. Coordination between rooks on open files or ranks.
    5. Harmony in pawn structure and piece placement.
    6. Coordination between major and minor pieces for potential threats.
    7. Evaluation of piece activity and mobility in relation to coordination.
    8. Awareness of piece values and imbalances.
    9. Analysis of positional features such as outposts and weak squares.
    10. Utilization of tactical patterns within coordinated piece setups.
    
    Higher scores indicate better harmony and coordination between pieces.
    """
    white_harmony_score = 0
    black_harmony_score = 0
    
    # 1. Coordination between pieces of the same color
    white_harmony_score += calculate_color_coordination(board, chess.WHITE)
    black_harmony_score += calculate_color_coordination(board, chess.BLACK)
    
    # 2. Control of key squares and lines by coordinated pieces
    white_harmony_score += calculate_key_square_control(board, chess.WHITE)
    black_harmony_score += calculate_key_square_control(board, chess.BLACK)
    
    # 3. Support of central squares by minor pieces
    white_harmony_score += calculate_central_support(board, chess.WHITE)
    black_harmony_score += calculate_central_support(board, chess.BLACK)
    
    # 4. Coordination between rooks on open files or ranks
    white_harmony_score += calculate_rook_coordination(board, chess.WHITE)
    black_harmony_score += calculate_rook_coordination(board, chess.BLACK)
    
    # 5. Harmony in pawn structure and piece placement
    white_harmony_score += evaluate_pawn_structure_score(board, chess.WHITE)
    black_harmony_score += evaluate_pawn_structure_score(board, chess.BLACK)
    
    # 6. Coordination between major and minor pieces for potential threats
    white_harmony_score += calculate_threat_coordination(board, chess.WHITE)
    black_harmony_score += calculate_threat_coordination(board, chess.BLACK)
    
    # 7. Evaluation of piece activity and mobility in relation to coordination
    white_harmony_score += calculate_mobility_coordination(board, chess.WHITE)
    black_harmony_score += calculate_mobility_coordination(board, chess.BLACK)
    
    # 8. Awareness of piece values and imbalances
    white_harmony_score += calculate_piece_value_awareness(board, chess.WHITE)
    black_harmony_score += calculate_piece_value_awareness(board, chess.BLACK)
    
    # 9. Analysis of positional features such as outposts and weak squares
    white_harmony_score += calculate_positional_features(board, chess.WHITE)
    black_harmony_score += calculate_positional_features(board, chess.BLACK)
    
    # 10. Utilization of tactical patterns within coordinated piece setups
    white_harmony_score += calculate_tactical_utilization(board, chess.WHITE)
    black_harmony_score += calculate_tactical_utilization(board, chess.BLACK)
    
    return white_harmony_score, black_harmony_score

def is_pinned(board, square, color):
    # Check if there's a piece on the square
    piece = board.piece_at(square)
    if piece is None:
        return False

    # Check if the piece is pinned by a rook or a queen
    for direction in [1, -1, 8, -8]:
        target = square + direction
        while 0 <= target < 64:
            if board.piece_at(target) is not None:
                if board.piece_at(target).color != color:
                    if board.piece_at(target).piece_type in [chess.ROOK, chess.QUEEN]:
                        return True
                    else:
                        break
                else:
                    break
            target += direction

    # Check if the piece is pinned by a bishop or a queen
    for direction in [9, -9, 7, -7]:
        target = square + direction
        while 0 <= target < 64:
            if board.piece_at(target) is not None:
                if board.piece_at(target).color != color:
                    if board.piece_at(target).piece_type in [chess.BISHOP, chess.QUEEN]:
                        return True
                    else:
                        break
                else:
                    break
            target += direction

    return False

def calculate_tactical_utilization(board, color):
    tactical_utilization = 0

    # Look for attacks and threats on the board
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is not None and piece.color == color:
            # Check for attacks on opponent's pieces
            attackers = board.attackers(not color, square)
            if attackers:
                tactical_utilization += 0.2  # Increment for each attacked opponent piece

            # Check for pinned pieces
            if is_pinned(board, square, color):
                tactical_utilization += 0.3  # Increment for each pinned piece

            # Check for potential forks and skewers
            moves = board.attacks(square)
            for move in moves:
                attacked_piece = board.piece_at(move)
                if attacked_piece is None or attacked_piece.color != color:
                    tactical_utilization += 0.4  # Increment for each potential fork or skewer

    # Check for checks and checkmates
    if board.is_checkmate():
        tactical_utilization += 1
    elif board.is_check():
        tactical_utilization += 0.5  # Increment for checks

    return tactical_utilization

def calculate_positional_features(board, color):
    features = 0

    # Material
    material = board.piece_map()
    white_material = 0
    black_material = 0
    for piece in material.values():
        if piece.color == chess.WHITE:
            white_material += piece.piece_type
        else:
            black_material += piece.piece_type
    features += white_material - black_material

    # Piece square tables
    pst_values = {
        chess.PAWN: [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [50, 50, 50, 50, 50, 50, 50, 50],
            [10, 10, 20, 30, 30, 20, 10, 10],
            [5, 5, 10, 25, 25, 10, 5, 5],
            [0, 0, 0, 20, 20, 0, 0, 0],
            [5, -5, -10, 0, 0, -10, -5, 5],
            [5, 10, 10, -20, -20, 10, 10, 5],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ],
        chess.KNIGHT: [
            [-50, -40, -30, -30, -30, -30, -40, -50],
            [-40, -20, 0, 0, 0, 0, -20, -40],
            [-30, 0, 10, 15, 15, 10, 0, -30],
            [-30, 5, 15, 20, 20, 15, 5, -30],
            [-30, 0, 15, 20, 20, 15, 0, -30],
            [-30, 5, 10, 15, 15, 10, 5, -30],
            [-40, -20, 0, 5, 5, 0, -20, -40],
            [-50, -40, -30, -30, -30, -30, -40, -50]
        ],
        # Add tables for other pieces
    }

    piece_values = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        # Add values for other pieces
    }

    for piece_type, pst in pst_values.items():
        pieces_on_board = board.pieces(piece_type, color)
        if pieces_on_board:  # Check if there are pieces of this type on the board
            for square in pieces_on_board:
                if color == chess.WHITE:
                    features += pst[square // 8][square % 8] * piece_values[piece_type] / len(pieces_on_board)
                else:
                    features -= pst[square // 8][7 - square % 8] * piece_values[piece_type] / len(pieces_on_board)

    return features

def calculate_mobility_coordination(board, color):
    """
    Calculate the coordination of mobility for the given color on the board.

    Parameters:
    board (chess.Board): The chess board.
    color (bool): The color of the player (chess.WHITE or chess.BLACK).

    Returns:
    float: The mobility coordination score for the specified color.
    """
    mobility_coordination_score = 0

    # Factor 1: Piece Mobility
    for piece_type in [chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
        for square in board.pieces(piece_type, color):
            piece = board.piece_at(square)
            # Increase score based on the number of legal moves available to the piece
            mobility_coordination_score += len(board.attacks(square))

    # Factor 2: Piece Placement
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.color == color:
            # Reward pieces in central squares or controlling key squares
            if square in [chess.D4, chess.E4, chess.D5, chess.E5]:
                mobility_coordination_score += 0.5
            elif square in [chess.C4, chess.F4, chess.C5, chess.F5]:
                mobility_coordination_score += 0.3
            elif square in [chess.D3, chess.E3, chess.D6, chess.E6]:
                mobility_coordination_score += 0.3

    # Factor 3: Piece Synergy
    # Assess how well pieces work together, rewarding coordination between pieces of the same color
    # You can consider factors like knight and bishop pairs, rook support, etc.

    # Factor 4: Pawn Structure
    # Evaluate how pawn structure influences piece mobility and coordination

    # Factor 5: Potential Threats
    # Consider potential threats created by mobile pieces, such as forks, pins, and skewers

    return mobility_coordination_score

def calculate_piece_value_awareness(board, color):
    """
    Calculate the piece value awareness for the given color on the board.

    Parameters:
    board (chess.Board): The chess board.
    color (bool): The color of the player (chess.WHITE or chess.BLACK).

    Returns:
    float: The piece value awareness score for the specified color.
    """
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0  # King value is not counted
    }

    awareness_score = 0

    # Evaluate the awareness of each piece's value
    for piece_type, value in piece_values.items():
        for square in board.pieces(piece_type, color):
            piece = board.piece_at(square)
            # Reward pieces that are in positions to capture higher value pieces
            opponents = board.pieces(piece_type, not color)
            for opp_square in opponents:
                if piece and opp_square:
                    opp_piece = board.piece_at(opp_square)
                    if opp_piece:
                        # Weight captures based on the relative value of the pieces
                        awareness_score += piece_values[opp_piece.piece_type] - piece_values[piece.piece_type]
                        
                        # Reward pieces that are central or control key squares
                        if opp_square in [chess.D4, chess.E4, chess.D5, chess.E5]:
                            awareness_score += 0.5
                        # Penalize pieces that are less active or restricted in mobility
                        if piece.piece_type == chess.KNIGHT:
                            # Penalize knights on the edge of the board
                            if opp_square in [chess.A1, chess.A8, chess.H1, chess.H8]:
                                awareness_score -= 0.5
                        elif piece.piece_type == chess.BISHOP:
                            # Penalize bishops blocked by their own pawns
                            if board.is_pinned(color, square):
                                awareness_score -= 0.5
                        elif piece.piece_type == chess.ROOK:
                            # Reward rooks on open files
                            if is_open_file(board, square):
                                awareness_score += 0.5
                            # Penalize rooks trapped behind their own pawns
                            if board.is_pinned(color, square):
                                awareness_score -= 0.5
                        elif piece.piece_type == chess.QUEEN:
                            # Reward queens in central squares
                            if square in [chess.D4, chess.E4, chess.D5, chess.E5]:
                                awareness_score += 1
                            # Penalize queens overextended or exposed to attacks
                            if board.is_attacked_by(not color, square):
                                awareness_score -= 1

    return awareness_score

def calculate_rook_coordination(board, color):
    """
    Calculate the coordination of rooks for the given color on the board, considering various factors.

    Parameters:
    board (chess.Board): The chess board.
    color (bool): The color of the player (chess.WHITE or chess.BLACK).

    Returns:
    float: The coordination score for rooks of the specified color.
    """
    coordination_score = 0

    # Define squares where rooks can be ideally placed for coordination
    ideal_rook_squares = [chess.square(2, 0), chess.square(5, 0), chess.square(2, 7), chess.square(5, 7)]

    # Evaluate coordination based on the presence of rooks on ideal squares
    for square in ideal_rook_squares:
        piece = board.piece_at(square)
        if piece and piece.piece_type == chess.ROOK and piece.color == color:
            coordination_score += 1  # Increment coordination score for each rook on an ideal square

    # Consider control of key files
    for file in range(8):
        rook_on_file = False
        for rank in [0, 1, 6, 7]:  # Numeric values for ranks
            square = chess.square(file, rank)
            piece = board.piece_at(square)
            if piece and piece.piece_type == chess.ROOK and piece.color == color:
                rook_on_file = True
                break
        if rook_on_file:
            coordination_score += 0.5  # Increment coordination score for each rook controlling a key file

    # Consider support for pawn breaks
    pawn_break_squares = [chess.B4, chess.C4, chess.D4, chess.E4, chess.B5, chess.C5, chess.D5, chess.E5,
                          chess.B5, chess.C5, chess.D5, chess.E5, chess.B6, chess.C6, chess.D6, chess.E6,
                          chess.B3, chess.C3, chess.D3, chess.E3, chess.B6, chess.C6, chess.D6, chess.E6]
    for square in pawn_break_squares:
        piece = board.piece_at(square)
        if piece and piece.piece_type == chess.PAWN and piece.color == color:
            coordination_score += 0.2  # Increment coordination score for each rook supporting a potential pawn break

    # Consider the potential to create threats
    for move in board.legal_moves:
        if move.piece == chess.ROOK and move.from_square in ideal_rook_squares:
            coordination_score += 0.5  # Increment coordination score for each rook threatening an opponent's piece

    # Consider rook safety
    for square in ideal_rook_squares:
        if board.is_attacked_by(not color, square):
            coordination_score -= 0.5  # Decrement coordination score if rook is under threat

    return coordination_score

def calculate_threat_coordination(board, color):
    """
    Calculate the coordination of threats for the given color on the board.

    Parameters:
    board (chess.Board): The chess board.
    color (bool): The color of the player (chess.WHITE or chess.BLACK).

    Returns:
    float: The threat coordination score for the specified color.
    """
    threat_coordination_score = 0

    # Factor 1: Piece activity and control over key squares
    for piece_type in [chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
        for square in board.pieces(piece_type, color):
            # Increase score for pieces in the center or controlling key squares
            if square in [chess.D4, chess.E4, chess.D5, chess.E5]:
                threat_coordination_score += 0.5
            elif square in [chess.C4, chess.F4, chess.C5, chess.F5]:
                threat_coordination_score += 0.3
            elif square in [chess.D3, chess.E3, chess.D6, chess.E6]:
                threat_coordination_score += 0.3

    # Factor 2: Evaluation of pawn structures supporting piece coordination
    for file in range(8):
        for rank in range(8):
            square = chess.square(file, rank)
            if board.piece_at(square) == chess.PAWN and board.color_at(square) == color:
                # Add score for pawns supporting pieces in the center or key squares
                if chess.square_file(square) in [2, 3, 4, 5] and chess.square_rank(square) in [3, 4, 5, 6]:
                    threat_coordination_score += 0.2
                # Add score for advanced pawns controlling enemy territory
                elif chess.square_rank(square) >= 5:
                    threat_coordination_score += 0.1

    # Factor 3: Assessment of threats in short-term and long-term contexts
    # This can involve evaluating potential tactics, checks, and mating threats

    return threat_coordination_score

def calculate_utilization_of_initiative(board, color):
    """
    Calculate the utilization of initiative for the given color on the board.

    Parameters:
    board (chess.Board): The chess board.
    color (bool): The color of the player (chess.WHITE or chess.BLACK).

    Returns:
    float: The utilization of initiative score for the specified color.
    """
    initiative_score = 0

    # Evaluate piece activity and coordination
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.color == color:
            legal_moves = len(list(board.legal_moves))
            initiative_score += legal_moves * 0.1  # Increment score based on legal moves
            
            # Check if the piece is well-coordinated with other pieces
            piece_coordination = 0
            for other_square in chess.SQUARES:
                other_piece = board.piece_at(other_square)
                if other_piece and other_piece.color == color and other_piece != piece:
                    piece_coordination += 0.1  # Increment score for each well-coordinated piece
            initiative_score += piece_coordination

    # Evaluate threats to opponent's pieces and king safety
    opponent_color = not color
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.color == opponent_color:
            if board.is_attacked_by(color, square):
                initiative_score += 0.5  # Increase score for threatening opponent pieces
            if board.is_attacked_by(color, chess.E8 if color == chess.WHITE else chess.E1):
                initiative_score += 1  # Increase score for attacking opponent king

    # Evaluate control of center and development advantage
    center_squares = [chess.D4, chess.E4, chess.D5, chess.E5]
    for square in center_squares:
        piece = board.piece_at(square)
        if piece and piece.color == color:
            initiative_score += 0.5  # Increment score for controlling the center

    # Evaluate tempo and pawn structure
    tempo = 0
    for move in board.legal_moves:
        board.push(move)
        if board.turn == color:
            tempo += 0.1  # Increment score for gaining tempo
        board.pop()
    initiative_score += tempo

    return initiative_score

def calculate_color_coordination(board, color):
    """
    Calculate the coordination among the pieces of a given color on the board.

    Parameters:
    board (chess.Board): The chess board.
    color (bool): The color of the player (chess.WHITE or chess.BLACK).

    Returns:
    float: The coordination score for the specified color.
    """
    # Piece values for weighting coordination
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0
    }

    # Center squares
    center_squares = [chess.D4, chess.D5, chess.E4, chess.E5]

    # Key squares for control (example: 4th to 6th ranks)
    key_squares = list(chess.SquareSet(chess.BB_RANK_4 | chess.BB_RANK_5 | chess.BB_RANK_6))

    # Calculate the coordination score
    coordination_score = 0

    # Iterate over all squares on the board
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.color == color:
            piece_type = piece.piece_type
            piece_value = piece_values[piece_type]

            # Get all the squares attacked by the piece
            attacks = board.attacks(square)

            for target_square in attacks:
                target_piece = board.piece_at(target_square)

                # Check if the target square is occupied by a friendly piece
                if target_piece and target_piece.color == color:
                    target_piece_value = piece_values[target_piece.piece_type]

                    # Add to the coordination score based on piece values
                    coordination_score += piece_value * target_piece_value

            # Add proximity factor (pieces closer to each other coordinate better)
            for other_square in chess.SQUARES:
                other_piece = board.piece_at(other_square)
                if other_piece and other_piece.color == color and other_square != square:
                    distance = chess.square_distance(square, other_square)
                    proximity_factor = 1 / (distance + 1)
                    coordination_score += piece_value * proximity_factor

            # Add centralization factor
            if square in center_squares:
                coordination_score += piece_value * 0.5

            # Add control of key squares
            if square in key_squares:
                coordination_score += piece_value * 0.3

            # Add piece activity (more active pieces contribute more)
            activity_factor = len(attacks) / 8.0
            coordination_score += piece_value * activity_factor

    # Normalize the coordination score based on the number of pieces
    num_pieces = len([piece for piece in board.piece_map().values() if piece.color == color])
    if num_pieces > 1:
        coordination_score /= num_pieces

    return coordination_score

def calculate_central_support(board, color):
    """
    Calculate the central support for the given color on the board.

    Parameters:
    board (chess.Board): The chess board.
    color (bool): The color of the player (chess.WHITE or chess.BLACK).

    Returns:
    float: The central support score for the specified color.
    """
    # Piece values for weighting central support
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0
    }

    # Central squares and their weights (strategic importance)
    central_squares = {
        chess.D4: 1.5,
        chess.D5: 1.5,
        chess.E4: 1.5,
        chess.E5: 1.5,
        chess.C4: 1.0,
        chess.C5: 1.0,
        chess.F4: 1.0,
        chess.F5: 1.0
    }

    central_support_score = 0

    for square, weight in central_squares.items():
        # Check which pieces control the central square
        attackers = board.attackers(color, square)
        defenders = board.attackers(not color, square)

        # Calculate control of central square
        for attacker_square in attackers:
            piece = board.piece_at(attacker_square)
            if piece and piece.color == color:
                piece_type = piece.piece_type
                piece_value = piece_values[piece_type]
                # Add distance factor (closer pieces have more influence)
                distance_factor = 1 / (1 + chess.square_distance(attacker_square, square))
                central_support_score += piece_value * weight * distance_factor

        # Calculate defense of central square
        for defender_square in defenders:
            piece = board.piece_at(defender_square)
            if piece and piece.color == color:
                piece_type = piece.piece_type
                piece_value = piece_values[piece_type]
                # Add distance factor (closer pieces have more influence)
                distance_factor = 1 / (1 + chess.square_distance(defender_square, square))
                central_support_score += piece_value * weight * distance_factor * 0.5  # Defending is less valuable than controlling

        # Add piece coordination factor
        for attacker_square in attackers:
            for other_attacker_square in attackers:
                if attacker_square != other_attacker_square:
                    piece1 = board.piece_at(attacker_square)
                    piece2 = board.piece_at(other_attacker_square)
                    if piece1 and piece2 and piece1.color == color and piece2.color == color:
                        # Add coordination value based on the types of pieces
                        coord_value = (piece_values[piece1.piece_type] + piece_values[piece2.piece_type]) * 0.1
                        central_support_score += coord_value

    return central_support_score

def calculate_key_square_control(board, color):
    """
    Calculate the control over key squares for a given board and color.
    
    Parameters:
    board (chess.Board): The chess board.
    color (bool): The color of the player (chess.WHITE or chess.BLACK).
    
    Returns:
    float: The control score for the specified color.
    """
    # Define key squares with weights based on strategic importance
    key_squares = {
        chess.E4: 1.0, chess.D4: 1.0, chess.E5: 1.0, chess.D5: 1.0,  # Central squares
        chess.F2: 0.5, chess.G2: 0.5, chess.F3: 0.5, chess.G3: 0.5,  # Squares near white king
        chess.F7: 0.5, chess.G7: 0.5, chess.F6: 0.5, chess.G6: 0.5,  # Squares near black king
        chess.C4: 0.8, chess.C5: 0.8, chess.F4: 0.8, chess.F5: 0.8,  # Important pawn break squares
        chess.D3: 0.7, chess.D6: 0.7, chess.E3: 0.7, chess.E6: 0.7,  # Near center control squares
    }
    
    # Piece weights
    piece_weights = {
        chess.PAWN: 0.1,
        chess.KNIGHT: 0.3,
        chess.BISHOP: 0.3,
        chess.ROOK: 0.5,
        chess.QUEEN: 0.9,
        chess.KING: 0.2
    }
    
    control_score = 0
    
    for square, square_weight in key_squares.items():
        # Get attackers for the square from both colors
        attackers_white = board.attackers(chess.WHITE, square)
        attackers_black = board.attackers(chess.BLACK, square)
        
        # Calculate control by white pieces
        if color == chess.WHITE:
            for attacker in attackers_white:
                piece = board.piece_at(attacker)
                control_score += piece_weights[piece.piece_type] * square_weight
        
        # Calculate control by black pieces
        if color == chess.BLACK:
            for attacker in attackers_black:
                piece = board.piece_at(attacker)
                control_score += piece_weights[piece.piece_type] * square_weight
    
    return control_score

def calculate_mobility_bonus(board, piece, square):
    """
    Calculate a mobility bonus for a piece based on potential future mobility.
    """
    mobility_bonus = 0
    
    # Check if the piece is a knight
    if piece.piece_type == chess.KNIGHT:
        # Knights have high mobility potential, especially if they control many empty squares around them
        mobility_bonus += len(list(board.attacks(square))) * 0.1
        
    # Check if the piece is a bishop
    elif piece.piece_type == chess.BISHOP:
        # Bishops have higher mobility potential if they control long diagonals
        mobility_bonus += len(list(board.attacks(square))) * 0.05
    
    # Check if the piece is a rook
    elif piece.piece_type == chess.ROOK:
        # Rooks have higher mobility potential if they control open files or ranks
        mobility_bonus += len(list(board.attacks(square))) * 0.03
    
    # Check if the piece is a queen
    elif piece.piece_type == chess.QUEEN:
        # Queens have high mobility potential, especially if they control many squares around them
        mobility_bonus += len(list(board.attacks(square))) * 0.07
    
    # Check if the piece is a pawn
    elif piece.piece_type == chess.PAWN:
        # Pawns have limited mobility, but if they have the potential to advance, they gain a mobility bonus
        if piece.color == chess.WHITE:
            if square in list(chess.SquareSet(chess.BB_RANK_4)):
                mobility_bonus += 0.5
        else:
            if square in list(chess.SquareSet(chess.BB_RANK_5)):
                mobility_bonus += 0.5
    
    return mobility_bonus

def evaluate_piece_activity_and_coordination(board):
    """
    Evaluate the activity and coordination of pieces on the board.
    Higher scores indicate better activity and coordination among pieces.
    """
    white_activity = 0
    black_activity = 0
    
    # Iterate through all squares
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            # Calculate activity value based on piece mobility and coordination
            activity_value = 1
            
            # Bonus for centralized pieces
            if square in CENTER_SQUARES:
                activity_value += 0.5
            
            # Bonus for control of key squares
            if square in chess.BB_SQUARES:
                activity_value += 0.5
            
            # Update activity score based on piece color
            if piece.color == chess.WHITE:
                white_activity += activity_value
            else:
                black_activity += activity_value
    
    # Normalize activity scores
    max_score = max(white_activity, black_activity)
    if max_score != 0:
        white_activity /= max_score
        black_activity /= max_score
    
    return white_activity - black_activity

def evaluate_defensive_offensive_tactics(board):
    """
    Evaluate the balance between defensive and offensive tactics.
    
    Factors Considered:
    1. Presence of pieces defending the king.
    2. Presence of pieces attacking the opponent's king.
    3. Pawn structure around kings.
    4. Control of center squares.
    5. Piece activity and mobility.
    
    Higher positive scores indicate a stronger offensive position, while higher negative scores indicate a stronger defensive position.
    """
    # Evaluate defensive tactics
    defensive_score = evaluate_defensive_tactics(board)
    
    # Evaluate offensive tactics
    offensive_score = evaluate_offensive_tactics(board)
    
    # Evaluate pawn structure around kings
    pawn_structure_score = evaluate_pawn_structure(board)
    
    # Evaluate control of center squares
    center_control_score = evaluate_center_control(board)
    
    # Evaluate piece activity and mobility
    piece_activity_score = evaluate_piece_activity(board)
    
    # Combine scores with weights
    total_score = offensive_score * 0.4 - defensive_score * 0.3 + pawn_structure_score * 0.1 + center_control_score * 0.1 + piece_activity_score * 0.1
    
    return total_score

def is_open_file(board, square):
    """
    Check if the file of the given square is open (no pawns).
    """
    file = chess.square_file(square)
    for rank in range(8):
        if board.piece_at(chess.square(file, rank)) is not None and \
           board.piece_at(chess.square(file, rank)).piece_type == chess.PAWN:
            return False
    return True
 
def is_open_diagonal(board, square):
    """
    Check if the diagonal containing the given square is open.

    Args:
    - board: The chess board.
    - square: The square to check.

    Returns:
    - True if the diagonal is open, False otherwise.
    """
    file, rank = chess.square_file(square), chess.square_rank(square)
    directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]  # Directions for the four diagonals
    for direction in directions:
        file_dir, rank_dir = direction
        file_pos, rank_pos = file + file_dir, rank + rank_dir
        while 0 <= file_pos < 8 and 0 <= rank_pos < 8:
            if board.piece_at(chess.square(file_pos, rank_pos)):
                # If there is a piece on any square of the diagonal, the diagonal is not open
                return False
            file_pos += file_dir
            rank_pos += rank_dir
    return True

def piece_value_for_material_balance(piece):
    """
    Get the value of a chess piece.
    """
    values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9
    }
    return values.get(piece.piece_type, 0) * (1 if piece.color == chess.WHITE else -1)

def evaluate_pawn_structure_score(board, color):
    """
    Evaluate pawn structures on the chessboard for the given color.

    Returns:
    - Positive score for favorable pawn structures
    - Negative score for unfavorable pawn structures
    """
    # Initialize score for pawn structures
    pawn_structure_score = 0

    pawn_ranks = {
        chess.WHITE: [1, 2, 3, 4, 5],
        chess.BLACK: [1, 2, 3, 4, 5]
    }

    for rank in pawn_ranks[color]:
        for file in range(8):
            square = chess.square(file, rank)
            piece = board.piece_at(square)
            if piece and piece.piece_type == chess.PAWN:
                # Check for isolated pawns
                isolated_pawns = 0
                if is_isolated_pawn(board, color, square):
                    isolated_pawns = 1

                # Check for doubled pawns
                doubled_pawns = count_doubled_pawns(board, color, rank)

                # Check for backward pawns
                backward_pawns = count_backward_pawns(board, color, rank)

                pawn_structure_score -= isolated_pawns + doubled_pawns + backward_pawns

    return pawn_structure_score

def calculate_pawn_structure_strength(board, color):
    """
    Calculate the pawn structure strength for the specified color.
    """
    pawn_structure_strength = 0
    
    # Evaluate pawn chains
    pawn_chains = get_pawn_chains(board, color)
    for chain in pawn_chains:
        chain_length = len(chain)
        pawn_structure_strength += chain_length
    
    return pawn_structure_strength

def get_pawn_chains(board, color):
    """
    Identify and return pawn chains for the given color.
    """
    chains = []
    visited = set()

    def explore_chain(row, col, chain):
        """
        Explore pawn chain recursively on the chessboard.

        Args:
        - row: Current row to explore.
        - col: Current column to explore.
        - chain: List to store squares in the chain.

        Returns:
        - None
        """
        if not (0 <= row < 8 and 0 <= col < 8):
            return  # Ensure the square is within the board boundaries

        square_index = row * 8 + col  # Convert (row, col) tuple to single integer index

        if (
            square_index in visited or
            not board.piece_at(square_index) or
            board.piece_at(square_index).piece_type != chess.PAWN or
            board.piece_at(square_index).color != color
        ):
            return

        visited.add(square_index)
        chain.append(square_index)

        # Define the adjacent squares (diagonals, vertical, and horizontal)
        adjacent_squares = [
            (row + dx, col + dy) 
            for dx in [-1, 0, 1] 
            for dy in [-1, 0, 1] 
            if (dx != 0 or dy != 0)
        ]
        
        for adj_row, adj_col in adjacent_squares:
            explore_chain(adj_row, adj_col, chain)

    # Iterate through all squares on the board
    for square_index in chess.SQUARES:
        row, col = divmod(square_index, 8)  # Convert square index to (row, col) tuple
        if (
            board.piece_at(square_index) and
            board.piece_at(square_index).piece_type == chess.PAWN and
            board.piece_at(square_index).color == color and
            square_index not in visited
        ):
            chain = []
            explore_chain(row, col, chain)
            if chain:
                chains.append(chain)

    return chains

def calculate_pawn_mobility(board, color):
    """
    Calculate the pawn mobility score for the specified color.
    """
    pawn_mobility = 0
    
    for square in board.pieces(chess.PAWN, color):
        pawn_mobility += len(list(board.attacks(square)))
    
    return pawn_mobility

def calculate_pawn_breaks(board, color):
    """
    Calculate the pawn breaks for the specified color.
    """
    pawn_breaks = 0
    
    pawn_direction = 1 if color == chess.WHITE else -1
    starting_rank = 1 if color == chess.WHITE else 6

    for square in board.pieces(chess.PAWN, color):
        # Check if the pawn is on its starting rank and can move two squares forward
        if chess.square_rank(square) == starting_rank and \
           board.is_pseudo_legal(chess.Move(square, square + pawn_direction * 16)):
            pawn_breaks += 1
    
    return pawn_breaks

def evaluate_tactics(board):
    """
    Evaluate the tactical opportunities and threats on the board.
    
    Factors Considered:
    1. Number of hanging pieces.
    2. Potential for forks, pins, skewers, and discovered attacks.
    3. Threats to opponent's pieces and king.
    4. Opportunities for captures and checks.
    5. Defensive and offensive tactics, including deflections, decoys, and interference.
    6. Control of key squares, files, diagonals, and ranks.
    7. Evaluation of pawn structures for pawn breaks and weaknesses.
    8. Evaluation of piece activity and coordination.
    9. Calculation of initiative and tempo.
    10. Analysis of material imbalances and piece values.
    
    Positive scores indicate better tactical opportunities for white,
    negative scores indicate better tactical opportunities for black.
    """
    # Initialize tactic scores
    white_tactics_score = 0
    black_tactics_score = 0
    
    # Count hanging pieces
    white_hanging_pieces = sum(1 for square in chess.SQUARES if board.piece_at(square) and board.piece_at(square).color == chess.WHITE and board.is_attacked_by(chess.BLACK, square))
    black_hanging_pieces = sum(1 for square in chess.SQUARES if board.piece_at(square) and board.piece_at(square).color == chess.BLACK and board.is_attacked_by(chess.WHITE, square))
    
    # Evaluate forks, pins, skewers, discovered attacks
    for square in chess.SQUARES:        
        piece = board.piece_at(square)
        if piece:
            attackers = board.attackers(not piece.color, square)
            defenders = board.attackers(piece.color, square)
            if len(attackers) > 1:
                if len(defenders) == 0:
                    if piece.color == chess.WHITE:
                        white_tactics_score += 1  # Fork opportunity
                    else:
                        black_tactics_score += 1
                elif len(defenders) == 1:
                    if piece.piece_type == chess.KING:
                        if piece.color == chess.WHITE:
                            white_tactics_score += 1  # King in danger of a fork
                        else:
                            black_tactics_score += 1
                    else:
                        pinned_piece = board.piece_at(defenders.pop())
                        if pinned_piece.piece_type != chess.KING:
                            if piece.color == chess.WHITE:
                                white_tactics_score += 1  # Pin opportunity
                            else:
                                black_tactics_score += 1
            elif len(attackers) == 1 and len(defenders) > 1:
                if piece.color == chess.WHITE:
                    white_tactics_score += 1  # Skewer opportunity
                else:
                    black_tactics_score += 1
            elif len(attackers) == 1 and len(defenders) == 0:
                if piece.color == chess.WHITE:
                    white_tactics_score += 1  # Discovered attack opportunity
                else:
                    black_tactics_score += 1
    
    # Evaluate threats to opponent's pieces and king
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.color == chess.WHITE:
            attackers = board.attackers(chess.BLACK, square)
            if attackers:
                white_tactics_score += len(attackers)  # Threats to opponent's pieces
                if board.is_checkmate():
                    white_tactics_score += 10  # Checkmate threat
        elif piece and piece.color == chess.BLACK:
            attackers = board.attackers(chess.WHITE, square)
            if attackers:
                black_tactics_score += len(attackers)  # Threats to opponent's pieces
                if board.is_checkmate():
                    black_tactics_score += 10  # Checkmate threat
    
    # Evaluate opportunities for captures and checks
    white_tactics_score += len(list(board.legal_moves))
    black_tactics_score += len(list(board.legal_moves))
    
    # Evaluate defensive and offensive tactics, including deflections, decoys, and interference
    white_tactics_score += evaluate_defensive_offensive_tactics(board)
    black_tactics_score += evaluate_defensive_offensive_tactics(board)
    
    # Evaluate control of key squares, files, diagonals, and ranks
    white_tactics_score += evaluate_control_of_key_squares_files_diagonals_ranks(board)
    black_tactics_score += evaluate_control_of_key_squares_files_diagonals_ranks(board)
    
    # Evaluate pawn structures for pawn breaks and weaknesses
    white_tactics_score += evaluate_pawn_structure(board)
    black_tactics_score += evaluate_pawn_structure(board)
    
    # Evaluate piece activity and coordination
    white_tactics_score += evaluate_piece_activity_and_coordination(board)
    black_tactics_score += evaluate_piece_activity_and_coordination(board)
    
    # Calculate initiative and tempo
    white_tactics_score += calculate_initiative_and_tempo(board)
    black_tactics_score += calculate_initiative_and_tempo(board)
    
    # Analyze material imbalances and piece values
    white_tactics_score += analyze_material_imbalances_and_piece_values(board)
    black_tactics_score += analyze_material_imbalances_and_piece_values(board)
    
    # Calculate tactic scores
    white_tactics_score += white_hanging_pieces
    black_tactics_score += black_hanging_pieces
    
    return white_tactics_score - black_tactics_score

def is_isolated_pawn(board, color, square):
    """
    Check if the pawn at the specified square is isolated.
    """
    file_idx = chess.square_file(square)
    rank_idx = chess.square_rank(square)

    # Check if there are no friendly pawns on adjacent files
    if file_idx == 0:
        right_square = chess.square(file_idx + 1, rank_idx)
        return not board.piece_at(right_square) or board.piece_at(right_square).color != color
    elif file_idx == 7:
        left_square = chess.square(file_idx - 1, rank_idx)
        return not board.piece_at(left_square) or board.piece_at(left_square).color != color
    else:
        left_square = chess.square(file_idx - 1, rank_idx)
        right_square = chess.square(file_idx + 1, rank_idx)
        return (not board.piece_at(left_square) or board.piece_at(left_square).color != color) and \
               (not board.piece_at(right_square) or board.piece_at(right_square).color != color)

def analyze_material_imbalances_and_piece_values(board):
    """
    Analyze material imbalances and evaluate the relative values of pieces.
    
    Factors Considered:
    1. Total material count for each side.
    2. Presence of material imbalances (e.g., more or fewer pieces of certain types).
    3. Evaluation of piece values based on the current board position.
    4. Positional significance of specific pieces (e.g., active bishops, centralized knights).
    5. Potential for piece exchanges and simplification of the position.
    6. Impact of material imbalances on pawn structure and king safety.
    
    Higher positive scores indicate favorable material imbalances and piece values for white,
    while higher negative scores indicate favorable conditions for black.
    """
    white_material_score = 0
    black_material_score = 0
    
    # 1. Total material count for each side
    white_material_score += calculate_total_material(board, chess.WHITE)
    black_material_score += calculate_total_material(board, chess.BLACK)
    
    # 2. Presence of material imbalances
    white_material_score += evaluate_material_imbalances(board, chess.WHITE)
    black_material_score += evaluate_material_imbalances(board, chess.BLACK)
    
    # 3. Evaluation of piece values based on the current board position
    white_material_score += evaluate_piece_values(board, chess.WHITE)
    black_material_score += evaluate_piece_values(board, chess.BLACK)
    
    # 4. Positional significance of specific pieces
    white_material_score += evaluate_piece_position(board, chess.WHITE)
    black_material_score += evaluate_piece_position(board, chess.BLACK)
    
    # 5. Potential for piece exchanges and simplification of the position
    white_material_score += evaluate_piece_exchanges(board, chess.WHITE)
    black_material_score += evaluate_piece_exchanges(board, chess.BLACK)
    
    # 6. Impact of material imbalances on pawn structure and king safety
    white_material_score += evaluate_material_impact(board, chess.WHITE)
    black_material_score += evaluate_material_impact(board, chess.BLACK)
    
    return white_material_score - black_material_score

def evaluate_material_impact(board, color):
    """
    Evaluate the impact of material on the board for the given color.

    Parameters:
    board (chess.Board): The chess board.
    color (bool): The color of the player (chess.WHITE or chess.BLACK).

    Returns:
    float: The evaluation score for material impact.
    """
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 200,
    }

    material_impact_score = 0

    # Evaluate material impact based on piece mobility, control of key squares, pawn structure, piece coordination, and king safety
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.color == color:
            # Evaluate the mobility of each piece
            mobility_score = len(board.attacks(square))
            
            # Evaluate the control of key squares
            control_score = 0
            for target_square in board.attacks(square):
                if board.piece_at(target_square) is None:
                    control_score += 1

            # Evaluate pawn structure
            pawn_structure_score = evaluate_pawn_structure(board)

            # Evaluate piece coordination
            piece_coordination_score = evaluate_piece_coordination(board)

            # Evaluate king safety
            king_safety_score = evaluate_king_safety(board, color)

            # Adjust material impact based on various factors
            material_impact_score += piece_values[piece.piece_type] + mobility_score + control_score + \
                                      pawn_structure_score + piece_coordination_score + king_safety_score

    return material_impact_score

def evaluate_piece_position(board, color):
    """
    Evaluate the positional advantage of each piece for the given color.

    Parameters:
    board (chess.Board): The chess board.
    color (bool): The color of the player (chess.WHITE or chess.BLACK).

    Returns:
    float: The total positional advantage score for the specified color.
    """
    piece_position_scores = {
        chess.PAWN: 1,    # Example scores, adjust as needed
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0  # King positional advantage is not considered
    }

    position_score = 0

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.color == color:
            piece_type = piece.piece_type
            position_score += piece_position_scores[piece_type]

            # You can add more complex logic to assign scores based on piece positioning

    return position_score

def calculate_initiative_and_tempo(board):
    """
    Evaluate the initiative and tempo in the current board position.
    
    Factors Considered:
    1. Development advantage and piece activity.
    2. Ability to control key squares and lines.
    3. Presence of threats and forcing moves.
    4. Flexibility in piece placement and future plans.
    5. King safety and defensive solidity.
    6. Pawn structure and potential pawn breaks.
    7. Utilization of initiative to dictate the pace of the game.
    8. Tempo advantage in terms of forcing responses from the opponent.
    
    Higher scores indicate a stronger initiative and tempo advantage.
    """
    white_initiative_score = 0
    black_initiative_score = 0
    
    # 1. Development advantage and piece activity
    white_initiative_score += calculate_development_advantage(board, chess.WHITE)
    black_initiative_score += calculate_development_advantage(board, chess.BLACK)
    
    # 2. Ability to control key squares and lines
    white_initiative_score += calculate_key_square_control(board, chess.WHITE)
    black_initiative_score += calculate_key_square_control(board, chess.BLACK)
    
    # 3. Presence of threats and forcing moves
    white_initiative_score += calculate_threat_presence(board, chess.WHITE)
    black_initiative_score += calculate_threat_presence(board, chess.BLACK)
    
    # 4. Flexibility in piece placement and future plans
    white_initiative_score += calculate_flexibility(board, chess.WHITE)
    black_initiative_score += calculate_flexibility(board, chess.BLACK)
    
    # 5. King safety and defensive solidity
    white_initiative_score += evaluate_king_safety(board, chess.WHITE)
    black_initiative_score += evaluate_king_safety(board, chess.BLACK)
    
    # 6. Pawn structure and potential pawn breaks
    white_initiative_score += evaluate_pawn_structure_score(board, chess.WHITE)
    black_initiative_score += evaluate_pawn_structure_score(board, chess.BLACK)
    
    # 7. Utilization of initiative to dictate the pace of the game
    white_initiative_score += calculate_utilization_of_initiative(board, chess.WHITE)
    black_initiative_score += calculate_utilization_of_initiative(board, chess.BLACK)
    
    # 8. Tempo advantage in terms of forcing responses from the opponent
    white_initiative_score += calculate_tempo_advantage(board, chess.WHITE)
    black_initiative_score += calculate_tempo_advantage(board, chess.BLACK)
    
    return white_initiative_score - black_initiative_score

def evaluate_piece_exchanges(board, color):
    """
    Evaluate the potential gains or losses from piece exchanges for the given color.

    Parameters:
    board (chess.Board): The chess board.
    color (bool): The color of the player (chess.WHITE or chess.BLACK).

    Returns:
    float: The evaluation score for potential piece exchanges.
    """
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0  # The king's value is not counted for total material
    }

    exchange_score = 0

    # Iterate over all squares
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.color == color:
            # Evaluate potential piece exchanges for each piece
            for target_square in board.attacks(square):
                target_piece = board.piece_at(target_square)
                if target_piece:
                    # Calculate the difference in piece values
                    exchange_value = piece_values[target_piece.piece_type] - piece_values[piece.piece_type]
                    
                    # Adjust exchange value based on piece mobility and positional advantages
                    if piece.piece_type == chess.PAWN:
                        # Pawns in the center have higher mobility
                        if square in [chess.D4, chess.E4, chess.D5, chess.E5]:
                            exchange_value += 0.5
                    elif piece.piece_type == chess.KNIGHT:
                        # Knights in advanced positions are more active
                        if square in [chess.C6, chess.F6, chess.C3, chess.F3]:
                            exchange_value += 0.5
                    elif piece.piece_type == chess.BISHOP:
                        # Bishops controlling key diagonals are more valuable
                        if square in [chess.B2, chess.G2, chess.B7, chess.G7]:
                            exchange_value += 0.5
                    elif piece.piece_type == chess.ROOK:
                        # Rooks on open files are more powerful
                        if is_open_file(board, square):
                            exchange_value += 1
                    elif piece.piece_type == chess.QUEEN:
                        # Queens in central squares exert more influence
                        if square in [chess.D4, chess.E4, chess.D5, chess.E5]:
                            exchange_value += 1
                    
                    exchange_score += exchange_value

    return exchange_score

def evaluate_piece_values(board, color):
    """
    Evaluate the worth of each piece based on its location for the given color on the board.

    Parameters:
    board (chess.Board): The chess board.
    color (bool): The color of the player (chess.WHITE or chess.BLACK).

    Returns:
    float: The total value of pieces based on their location.
    """
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0  # The king's value is not counted for total material
    }

    total_value = 0

    # Evaluate the worth of each piece based on its location
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.color == color:
            piece_type = piece.piece_type
            total_value += piece_values[piece_type]

    return total_value

def evaluate_material_imbalances(board, color):
    """
    Evaluate material imbalances for the given color on the board.

    Parameters:
    board (chess.Board): The chess board.
    color (bool): The color of the player (chess.WHITE or chess.BLACK).

    Returns:
    float: The material imbalance score for the specified color.
    """
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0
    }

    # Calculate total material for both colors
    total_material_color = calculate_total_material(board, color)
    total_material_opponent = calculate_total_material(board, not color)

    # Calculate material imbalance score
    material_imbalance = total_material_color - total_material_opponent

    return material_imbalance

def calculate_total_material(board, color):
    """
    Calculate the total material score for the given color on the board.

    Parameters:
    board (chess.Board): The chess board.
    color (bool): The color of the player (chess.WHITE or chess.BLACK).

    Returns:
    float: The total material score for the specified color.
    """
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0
    }

    total_material_score = 0

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.color == color:
            total_material_score += piece_values[piece.piece_type]

    return total_material_score

def calculate_tempo_advantage(board, color):
    """
    Calculate the tempo advantage for the given color on the board.

    Parameters:
    board (chess.Board): The chess board.
    color (bool): The color of the player (chess.WHITE or chess.BLACK).

    Returns:
    float: The tempo advantage score for the specified color.
    """
    tempo_advantage = 0

    # Evaluate rapid development and active piece play
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.color == color:
            legal_moves = len(list(board.legal_moves))
            tempo_advantage += legal_moves * 0.1  # Increment score based on legal moves
            
            # Check if the piece is well-placed for rapid development
            if piece.piece_type == chess.PAWN and (square == chess.E2 if color == chess.WHITE else chess.E7):
                tempo_advantage += 0.5  # Increment score for central pawn advancement
            elif piece.piece_type == chess.KNIGHT and (square == chess.G1 if color == chess.WHITE else chess.G8):
                tempo_advantage += 0.5  # Increment score for knight development to the kingside
            elif piece.piece_type == chess.BISHOP and (square == chess.F1 if color == chess.WHITE else chess.F8):
                tempo_advantage += 0.5  # Increment score for bishop development to the kingside
            elif piece.piece_type == chess.QUEEN and (square == chess.D1 if color == chess.WHITE else chess.D8):
                tempo_advantage += 0.5  # Increment score for queen development to the central file
            elif piece.piece_type == chess.ROOK and (square == chess.H1 if color == chess.WHITE else chess.H8):
                tempo_advantage += 0.5  # Increment score for rook development to the kingside
            
            # Check if the piece is actively involved in threats or control
            active_play = 0
            for target_square in board.attackers(color, square):
                if board.piece_at(target_square) and board.piece_at(target_square).color != color:
                    active_play += 0.1  # Increment score for threatening opponent pieces
                else:
                    active_play += 0.05  # Increment score for controlling squares
            tempo_advantage += active_play

    # Additional factors
    # Evaluate pawn structure, piece mobility, king safety, space control, and material balance
    
    # Add enhancements here
    
    return tempo_advantage

def calculate_flexibility(board, color):
    """
    Calculate the flexibility for the given color on the board.

    Parameters:
    board (chess.Board): The chess board.
    color (bool): The color of the player (chess.WHITE or chess.BLACK).

    Returns:
    float: The flexibility score for the specified color.
    """
    flexibility_score = 0

    # Evaluate piece mobility and coordination
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.color == color:
            mobility = len(board.attacks(square))
            flexibility_score += mobility

            # Check piece coordination with same color pieces
            coordination_bonus = 0
            for adjacent_square in board.attacks(square):
                if board.piece_at(adjacent_square) and board.piece_at(adjacent_square).color == color:
                    coordination_bonus += 0.5  # Increase flexibility for coordinated pieces
            flexibility_score += coordination_bonus

    # Evaluate control of key squares
    key_squares = [chess.E4, chess.D4, chess.E5, chess.D5]  # Example: Central squares
    for square in key_squares:
        if board.piece_at(square) and board.piece_at(square).color == color:
            flexibility_score += 1  # Increase flexibility for controlling key squares

    # Evaluate pawn structure stability
    pawns = board.pieces(chess.PAWN, color)
    for pawn_square in pawns:
        pawn_file = chess.square_file(pawn_square)
        adjacent_files = [pawn_file - 1, pawn_file + 1]
        for file in adjacent_files:
            if 0 <= file < 8:
                square = chess.square(file, chess.square_rank(pawn_square))
                if board.piece_at(square) is None:
                    flexibility_score += 0.5  # Minor score for potential pawn advances

    return flexibility_score

def count_doubled_pawns(board, color, rank):
    """
    Count the number of doubled pawns on the specified rank for the given color.
    """
    doubled_pawns_count = 0
    pawn_files = set()  # Keep track of files where pawns are found

    # Find all pawns on the specified rank and record their file positions
    for file in range(8):
        piece = board.piece_at(chess.square(file, rank))
        if piece and piece.piece_type == chess.PAWN and piece.color == color:
            pawn_files.add(file)

    # Check if there are multiple pawns on the same file
    for file in pawn_files:
        # If there is another pawn of the same color on the same file, it's a doubled pawn
        if sum(1 for f in pawn_files if f == file) > 1:
            doubled_pawns_count += 1

    return doubled_pawns_count

def count_backward_pawns(board, color, rank):
    """
    Count the number of backward pawns on the specified rank for the given color.
    """
    backward_pawns_count = 0

    # Iterate over the files on the specified rank
    for file in range(8):
        piece = board.piece_at(chess.square(file, rank))
        if piece and piece.piece_type == chess.PAWN and piece.color == color:
            # Check if there is no friendly pawn on an adjacent file and a higher rank
            if (file == 0 or not board.piece_at(chess.square(file - 1, rank + 1)) or board.piece_at(chess.square(file - 1, rank + 1)).color != color) \
                and (file == 7 or not board.piece_at(chess.square(file + 1, rank + 1)) or board.piece_at(chess.square(file + 1, rank + 1)).color != color):
                backward_pawns_count += 1

    return backward_pawns_count

def evaluate_defensive_activity(board, color):
    """
    Evaluate the defensive activity of the given color on the chessboard.

    Higher positive scores indicate stronger defensive activity.
    """
    # Initialize defensive activity score
    defensive_activity_score = 0
    
    # Evaluate piece placement and control of key squares
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is not None and piece.color == color:
            # Evaluate the placement of defensive pieces
            piece_value = piece_value_score(piece)
            defensive_activity_score += piece_value
            
            # Evaluate control of key squares around the king
            if piece.piece_type == chess.ROOK:
                # Bonus for rooks on open files
                if is_open_file(board, square):
                    defensive_activity_score += 0.5
                # Bonus for rooks on the 7th rank
                if chess.square_rank(square) == 6 and color == chess.WHITE:
                    defensive_activity_score += 0.5
                elif chess.square_rank(square) == 1 and color == chess.BLACK:
                    defensive_activity_score += 0.5
            elif piece.piece_type == chess.KNIGHT:
                # Bonus for knights in the center
                if chess.square_file(square) in [2, 3, 4, 5] and chess.square_rank(square) in [2, 3, 4, 5]:
                    defensive_activity_score += 0.5
            elif piece.piece_type == chess.BISHOP:
                # Bonus for bishops controlling long diagonals
                if is_open_diagonal(board, square):
                    defensive_activity_score += 0.5
            elif piece.piece_type == chess.QUEEN:
                # Bonus for queens on open files or long diagonals
                if is_open_file(board, square) or \
                   is_open_diagonal(board, square):
                    defensive_activity_score += 0.5

    # Evaluate pawn structure for defensive stability
    pawn_structure_score = evaluate_pawn_structure(board)
    defensive_activity_score += pawn_structure_score

    return defensive_activity_score

def piece_value_score(piece):
    """
    Assign a score based on the value of the piece.

    Returns:
    - Higher score for major pieces (queen, rook)
    - Medium score for minor pieces (bishop, knight)
    - Lower score for pawns
    """
    if piece.piece_type == chess.QUEEN:
        return 5
    elif piece.piece_type == chess.ROOK:
        return 3
    elif piece.piece_type == chess.BISHOP or piece.piece_type == chess.KNIGHT:
        return 2
    elif piece.piece_type == chess.PAWN:
        return 1
    else:
        return 0

def evaluate_offensive_tactics(board):
    """
    Evaluate offensive tactics on the chessboard.

    Higher positive scores indicate stronger offensive tactics.
    """
    # Initialize offensive tactics score
    offensive_tactics_score = 0
    
    # Evaluate piece activity and control of key squares
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is not None and piece.color == board.turn:
            # Evaluate the activity of offensive pieces
            piece_value = piece_value_score(piece)
            offensive_tactics_score += piece_value
            
            # Evaluate control of key squares around the opponent's king
            if piece.piece_type == chess.ROOK:
                # Bonus for rooks on open files
                if is_open_file(board, chess.square_file(square)):
                    offensive_tactics_score += 0.5
                # Bonus for rooks on the 7th rank
                if chess.square_rank(square) == 6 and piece.color == chess.WHITE:
                    offensive_tactics_score += 0.5
                elif chess.square_rank(square) == 1 and piece.color == chess.BLACK:
                    offensive_tactics_score += 0.5
            elif piece.piece_type == chess.KNIGHT:
                # Bonus for knights in the center
                if chess.square_file(square) in [2, 3, 4, 5] and chess.square_rank(square) in [2, 3, 4, 5]:
                    offensive_tactics_score += 0.5
            elif piece.piece_type == chess.BISHOP:
                # Bonus for bishops controlling long diagonals
                if is_open_diagonal(board, square):
                    offensive_tactics_score += 0.5
            elif piece.piece_type == chess.QUEEN:
                # Bonus for queens on open files or long diagonals
                if is_open_file(board, chess.square_file(square)) or \
                is_open_diagonal(board, square):
                    offensive_tactics_score += 0.5

    # Evaluate pawn structure for offensive possibilities
    pawn_structure_score = evaluate_pawn_structures(board, board.turn)
    offensive_tactics_score += pawn_structure_score

    return offensive_tactics_score

def evaluate_defensive_tactics(board):
    """
    Evaluate the defensive tactics of a given chess position.

    Factors Considered:
    1. Presence of pieces defending the king.
    2. Activity of defensive pieces.
    3. Pawn structure around the king.
    4. Safety of the king.
    5. Potential threats from the opponent.

    Higher positive scores indicate stronger defensive positions.
    """
    # Initialize defensive score
    defensive_score = 0
    
    # Get the current player's color
    color = board.turn
    
    # Find the square of the king
    king_square = board.king(color)
    
    # Evaluate the presence of pieces defending the king
    defenders_score = evaluate_defenders(board, king_square, color)
    defensive_score += defenders_score
    
    # Evaluate the activity of defensive pieces
    activity_score = evaluate_defensive_activity(board, color)
    defensive_score += activity_score
    
    # Evaluate pawn structure around the king
    pawn_structure_score = evaluate_pawn_structure(board)
    defensive_score += pawn_structure_score
    
    # Evaluate the safety of the king
    king_safety_score = evaluate_king_safety(board, color)
    defensive_score += king_safety_score
    
    # Evaluate potential threats from the opponent
    threats_score = evaluate_threats(board, king_square, color)
    defensive_score += threats_score
    
    return defensive_score

def calculate_threat_presence(board, color):
    """
    Calculate the threat presence for the given color on the board.

    Parameters:
    board (chess.Board): The chess board.
    color (bool): The color of the player (chess.WHITE or chess.BLACK).

    Returns:
    float: The threat presence score for the specified color.
    """
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0  # King threats are not considered in terms of material value
    }

    opponent_color = not color
    threat_score = 0

    # Evaluate attacked squares
    for square in chess.SQUARES:
        attackers = board.attackers(color, square)
        if attackers:
            for attacker in attackers:
                threat_score += 0.1  # Minor score for attacking any square

    # Evaluate threats to opponent pieces
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.color == opponent_color:
            attackers = board.attackers(color, square)
            if attackers:
                for attacker in attackers:
                    threat_score += piece_values[piece.piece_type] * 0.2  # Higher score for threatening valuable pieces

    # Evaluate potential tactics (forks, pins, skewers)
    for move in board.legal_moves:
        if board.color_at(move.from_square) == color:
            board.push(move)
            if board.is_check():
                threat_score += 2  # Significant score for giving check
            board.pop()

            if board.is_attacked_by(color, move.to_square):
                attacking_piece = board.piece_at(move.to_square)
                if attacking_piece and attacking_piece.piece_type in [chess.KNIGHT, chess.ROOK, chess.QUEEN]:
                    threat_score += 1  # Significant score for tactical threats

    return threat_score

def calculate_development_advantage(board, color):
    """
    Calculate the development advantage for the given color on the board.

    Parameters:
    board (chess.Board): The chess board.
    color (bool): The color of the player (chess.WHITE or chess.BLACK).

    Returns:
    float: The development advantage score for the specified color.
    """
    piece_values = {
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0
    }

    development_squares = {
        chess.KNIGHT: [chess.D2, chess.D7, chess.E2, chess.E7, chess.C3, chess.C6, chess.F3, chess.F6],
        chess.BISHOP: [chess.C1, chess.F1, chess.C8, chess.F8, chess.B2, chess.G2, chess.B7, chess.G7],
        chess.ROOK: [chess.A1, chess.H1, chess.A8, chess.H8],
        chess.QUEEN: [chess.D1, chess.D8],
        chess.KING: [chess.C1, chess.G1, chess.C8, chess.G8]
    }

    open_file_squares = [
        chess.A1, chess.A8, chess.B1, chess.B8, chess.C1, chess.C8, chess.D1, chess.D8, chess.E1, chess.E8, chess.F1, chess.F8, chess.G1, chess.G8, chess.H1, chess.H8
    ]

    development_score = 0

    # Evaluate piece development
    for piece_type in [chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
        for square in development_squares[piece_type]:
            piece = board.piece_at(square)
            if piece and piece.piece_type == piece_type and piece.color == color:
                if piece_type in [chess.KNIGHT, chess.BISHOP]:
                    development_score += piece_values[piece_type] * 0.5  # Partially developed
                else:
                    development_score += piece_values[piece_type]  # Fully developed

    # Evaluate rook activation on open or semi-open files
    for square in open_file_squares:
        piece = board.piece_at(square)
        if piece and piece.piece_type == chess.ROOK and piece.color == color:
            if is_open_file(board, chess.square_file(square)):
                development_score += piece_values[chess.ROOK] * 1.5
            elif is_semi_open_file(board, color, chess.square_file(square)):
                development_score += piece_values[chess.ROOK] * 1.0

    # Evaluate king safety (castling)
    if board.turn == color and any(move.castling() for move in board.legal_moves):
        development_score += 5  # Safe castling bonus

    # Evaluate piece coordination
    pieces = list(board.pieces(chess.KNIGHT, color)) + list(board.pieces(chess.BISHOP, color))
    for i, piece1 in enumerate(pieces):
        for j, piece2 in enumerate(pieces):
            if i < j:
                # Add coordination value based on the types of pieces
                coord_value = (piece_values[board.piece_type_at(piece1)] + piece_values[board.piece_type_at(piece2)]) * 0.1
                development_score += coord_value

    return development_score

def is_semi_open_file(board, color, file):
    """
    Check if a file is semi-open for the specified color.

    Parameters:
    board (chess.Board): The chess board.
    color (bool): The color of the player (chess.WHITE or chess.BLACK).
    file (int): The file to check (0-7 representing a-h).

    Returns:
    bool: True if the file is semi-open for the specified color, False otherwise.
    """
    opposite_color = not color
    for square in chess.SQUARES:
        if chess.square_file(square) == file and board.piece_at(square) and board.piece_at(square).color == opposite_color:
            return False
    return True

def evaluate_pawn_cover(board, king_square):
    """
    Evaluate the pawn cover around the king.
    More pawns providing cover result in a higher score.
    """
    pawn_cover_score = 0
    king_file, king_rank = chess.square_file(king_square), chess.square_rank(king_square)
    
    # Check the squares surrounding the king
    for i in range(-1, 2):
        for j in range(-1, 2):
            # Skip the king's square
            if i == 0 and j == 0:
                continue
            
            square = chess.square(king_file + i, king_rank + j)
            # Ensure the square is on the board
            if not chess.square_file(square) in range(8) or not chess.square_rank(square) in range(8):
                continue
            
            piece = board.piece_at(square)
            if piece is not None and piece.color == chess.WHITE and piece.piece_type == chess.PAWN:
                pawn_cover_score += 1
    
    return pawn_cover_score

def evaluate_attackers(board, king_square):
    """
    Evaluate the presence of attackers near the king.
    
    Factors Considered:
    1. Number of enemy pieces attacking squares adjacent to the king.
    
    Higher scores indicate a higher number of attackers near the king.
    """
    # Get squares adjacent to the king
    adjacent_squares = chess.SquareSet(_sliding_attacks(board, king_square))
    
    # Count the number of attackers on adjacent squares
    attackers_count = sum(1 for square in adjacent_squares if board.is_attacked_by(chess.BLACK, square))
    
    return attackers_count

def evaluate_defenders(board, king_square, color):
    """
    Evaluate the presence of pieces defending the king.

    Higher positive scores indicate more defenders around the king.
    """
    # Initialize defenders score
    defenders_score = 0
    
    # Check for pieces defending the king
    attackers = board.attackers(not color, king_square)
    num_defenders = len(attackers)
    
    # Increase the score based on the number of defenders
    defenders_score += num_defenders
    
    return defenders_score

def _sliding_attacks(board, square):
    """
    Calculate the squares attacked by sliding pieces (bishop, rook, queen) from a given square.
    """
    attacks = chess.SquareSet()
    piece = board.piece_at(square)
    
    if piece is None:
        return attacks
    
    directions = []
    if piece.piece_type == chess.BISHOP or piece.piece_type == chess.QUEEN:
        # Bishop directions: diagonals
        directions.extend([(-1, -1), (-1, 1), (1, -1), (1, 1)])
    if piece.piece_type == chess.ROOK or piece.piece_type == chess.QUEEN:
        # Rook directions: vertical and horizontal
        directions.extend([(-1, 0), (1, 0), (0, -1), (0, 1)])
    
    for dx, dy in directions:
        for i in range(1, 8):
            f, r = chess.square_file(square) + i * dx, chess.square_rank(square) + i * dy
            if 0 <= f < 8 and 0 <= r < 8:
                target_square = chess.square(f, r)
                attacks.add(target_square)
                if board.piece_at(target_square) is not None:
                    break
            else:
                break
    
    return attacks

def evaluate_open_files(board, king_square):
    """
    Evaluate the presence of open files in front of the king.
    Open files increase the vulnerability of the king.
    """
    open_files_score = 0
    king_file = chess.square_file(king_square)
    
    # Check the files in front of the king
    for file in range(8):
        if file != king_file and all(board.piece_at(chess.square(file, rank)) is None for rank in range(8)):
            open_files_score -= 1
    
    return open_files_score

def evaluate_pawn_shield(board, king_square):
    """
    Evaluate the strength of the pawn shield in front of the king.
    A stronger pawn shield provides better protection for the king.
    """
    pawn_shield_score = 0
    king_file, king_rank = chess.square_file(king_square), chess.square_rank(king_square)
    
    # Check the squares in front of the king
    front_squares = []
    for i in range(-1, 2):
        file_index = king_file + i
        rank_index = king_rank + 1
        # Ensure the square is within the board boundaries
        if 0 <= file_index < 8 and 0 <= rank_index < 8:
            front_squares.append(chess.square(file_index, rank_index))
    
    for square in front_squares:
        piece_type = board.piece_type_at(square)
        color = board.color_at(square)
        
        if piece_type == chess.PAWN and color == chess.WHITE:
            pawn_shield_score += 1
    
    return pawn_shield_score

def evaluate_king_mobility(board, king_square):
    """
    Evaluate the mobility of the king.
    A king with limited mobility is more vulnerable.
    """
    king_mobility_score = 0
    
    # Check the squares where the king can move
    mobility_squares = [square for square in chess.SQUARES if square != king_square and
                        chess.square_distance(square, king_square) <= 2]
    
    # Limit the maximum number of iterations to avoid potential recursion issues
    max_iterations = min(len(mobility_squares), 5)  # Set a reasonable maximum
    
    for square in mobility_squares:
        move = chess.Move(king_square, square)
        if board.is_pseudo_legal(move) and not board.is_into_check(move):
            king_mobility_score += 1

        
        # Break the loop if the king's mobility score is already high enough
        if king_mobility_score >= max_iterations:
            break
    
    return king_mobility_score

def evaluate_threats(board, king_square, color):
    """
    Evaluate potential threats from the opponent.

    Higher positive scores indicate more threats to the opponent's king.
    """
    # Initialize threats score
    threats_score = 0
    
    # Find the opponent's king square
    opponent_king_square = board.king(not color)
    
    # Evaluate threats to the opponent's king
    num_attacks = len(board.attacks(opponent_king_square))
    
    # Increase the score based on the number of attacks
    threats_score += num_attacks
    
    # Evaluate the strength and proximity of attacks
    for attack_square in board.attacks(opponent_king_square):
        # Get the piece attacking the opponent's king
        attacking_piece = board.piece_at(attack_square)
        if attacking_piece is not None and attacking_piece.color != color:
            # Evaluate the strength of the attacking piece
            piece_value = piece_value_score(attacking_piece)
            
            # Evaluate the proximity of the attacking piece to the opponent's king
            proximity_score = proximity_to_king_score(attack_square, opponent_king_square)
            
            # Adjust the threats score based on the strength and proximity of the attack
            threats_score += piece_value * proximity_score
    
    return threats_score

def piece_value_score(piece):
    """
    Assign a score based on the value of the attacking piece.

    Returns:
    - High score for major pieces (queen, rook)
    - Medium score for minor pieces (bishop, knight)
    - Low score for pawns
    """
    if piece.piece_type == chess.QUEEN:
        return 5
    elif piece.piece_type == chess.ROOK:
        return 3
    elif piece.piece_type == chess.BISHOP or piece.piece_type == chess.KNIGHT:
        return 2
    elif piece.piece_type == chess.PAWN:
        return 1
    else:
        return 0

def evaluate_control_of_key_squares_files_diagonals_ranks(board):
    """
    Evaluate the control of key squares, files, diagonals, and ranks.
    
    Factors Considered:
    1. Control of open files and important diagonals by rooks, bishops, and queens.
    2. Presence of pawns controlling files and diagonals.
    3. Piece activity and positioning.
    """
    white_control = 0
    black_control = 0

    # Evaluate control of files
    for file_idx in range(8):
        file_squares = chess.BB_FILES[file_idx]
        white_pawns_on_file = sum(1 for sq in chess.SQUARES if (file_squares & chess.BB_SQUARES[sq]) and board.piece_at(sq) == chess.PAWN and board.color_at(sq) == chess.WHITE)
        black_pawns_on_file = sum(1 for sq in chess.SQUARES if (file_squares & chess.BB_SQUARES[sq]) and board.piece_at(sq) == chess.PAWN and board.color_at(sq) == chess.BLACK)
        white_control += white_pawns_on_file
        black_control += black_pawns_on_file

        white_rooks_on_file = sum(1 for sq in chess.SQUARES if (file_squares & chess.BB_SQUARES[sq]) and board.piece_at(sq) == chess.ROOK and board.color_at(sq) == chess.WHITE)
        black_rooks_on_file = sum(1 for sq in chess.SQUARES if (file_squares & chess.BB_SQUARES[sq]) and board.piece_at(sq) == chess.ROOK and board.color_at(sq) == chess.BLACK)
        white_control += white_rooks_on_file * 2
        black_control += black_rooks_on_file * 2

    # Evaluate control of diagonals
    def get_diagonal_squares(square):
        file, rank = chess.square_file(square), chess.square_rank(square)
        diagonals = []

        # Top right and bottom left diagonals
        for i in range(-min(file, rank), 8 - max(file, rank)):
            diagonals.append(chess.square(file + i, rank + i))

        # Top left and bottom right diagonals
        for i in range(-min(7 - file, rank), min(7 - rank, file) + 1):
            diagonals.append(chess.square(file - i, rank + i))

        return set(diagonals)

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            diagonals = get_diagonal_squares(square)
            white_pieces_on_diag = sum(1 for sq in diagonals if board.color_at(sq) == chess.WHITE)
            black_pieces_on_diag = sum(1 for sq in diagonals if board.color_at(sq) == chess.BLACK)
            if piece.color == chess.WHITE:
                white_control += white_pieces_on_diag
            else:
                black_control += black_pieces_on_diag

    # Evaluate piece activity and positioning
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            if piece.color == chess.WHITE:
                white_control += 1
            else:
                black_control += 1

    return white_control - black_control

def evaluate_pawn_structures(board, color):
    """
    Evaluate pawn structures on the chessboard for the given color.

    Returns:
    - Positive score for favorable pawn structures
    - Negative score for unfavorable pawn structures
    """
    # Initialize score for pawn structures
    pawn_structure_score = 0

    # Get pawns of the given color
    pawns = board.pieces(chess.PAWN, color)

    # Doubled pawns penalty
    file_counts = [0] * 8  # Initialize list to count pawns on each file
    for sq in pawns:
        file_counts[chess.square_file(sq)] += 1
    doubled_pawns_count = sum(count - 1 for count in file_counts if count > 1)
    pawn_structure_score -= doubled_pawns_count * 0.5  # Each doubled pawn reduces the score

    # Isolated pawns penalty
    isolated_pawns_count = 0
    for sq in pawns:
        file_idx = chess.square_file(sq)
        if file_idx > 0 and file_idx < 7:  # Exclude pawns on A and H files
            if board.piece_at(sq - 1) is None and board.piece_at(sq + 1) is None:
                isolated_pawns_count += 1
    pawn_structure_score -= isolated_pawns_count * 0.5  # Each isolated pawn reduces the score

    # Passed pawns bonus
    passed_pawns = eval_passed_pawns(board, color)
    pawn_structure_score += passed_pawns * 0.5  # Each passed pawn increases the score

    # Pawn mobility
    mobility_score = 0
    for sq in pawns:
        mobility_score += len(board.attacks(sq))
    pawn_structure_score += mobility_score * 0.1  # Increase score based on pawn mobility

    # Pawn structure near kings
    king_sq = board.king(color)
    pawns_near_king = pawns & chess.SquareSet(_sliding_attacks(board, king_sq))
    pawn_structure_score += len(pawns_near_king) * 0.2  # Increase score for pawns near the king

    return pawn_structure_score

def proximity_to_king_score(attack_square, king_square):
    """
    Evaluate the proximity of the attack square to the opponent's king.

    Returns:
    - High score for attacks near the opponent's king
    - Medium score for attacks one square away
    - Low score for attacks two squares away
    """
    file_distance = abs(chess.square_file(attack_square) - chess.square_file(king_square))
    rank_distance = abs(chess.square_rank(attack_square) - chess.square_rank(king_square))
    
    if file_distance <= 1 and rank_distance <= 1:
        return 2
    elif file_distance <= 2 and rank_distance <= 2:
        return 1
    else:
        return 0
