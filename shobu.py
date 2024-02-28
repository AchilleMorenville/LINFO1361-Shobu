from typing import NamedTuple, List, Set

class ShobuAction(NamedTuple):
    """Represents an action in the Shobu game, encompassing both passive and active moves.

    Attributes:
        passive_board_id (int): Index of the board for the passive move (0-3).
        passive_stone_id (int): Index of the stone moved in the passive move (0-15).
        active_board_id (int): Index of the board for the active move (0-3).
        active_stone_id (int): Index of the stone moved in the active move (0-15).
        direction (int): The direction of the move, represented as an offset to the stone's index.
        length (int): The magnitude of the move, indicating how far the stone moves.

    The direction of the move is based on an integer value that represents an offset to the
    current position of the stone. Direction offsets are as follows:
    
     +3  | +4  | +5   (Upwards movements)
    ----------------
     -1  |     | +1   (Horizontal movements)
    ----------------
     -5  | -4  | -3   (Downwards movements)

    The `length` indicates how many times the direction offset is applied to move the stone.
    """
    passive_board_id: int
    passive_stone_id: int
    active_board_id: int
    active_stone_id: int
    direction: int
    length: int

class ShobuState(NamedTuple):
    """Represents the current state of a Shobu game.

    Attributes:
        to_move (int): The ID of the player who is next to move (0 or 1).
        utility (int): The utility score of the game, from the perspective of player 0. A score of 1
            indicates a win for player 0, -1 indicates a loss, and 0 typically indicates an ongoing
            game or a draw.
        board (List[List[Set[int], Set[int]]]): A representation of the 4 boards in the game.
            Each board is represented as a list containing two sets: the first set contains positions
            of player 0's stones, and the second set contains positions of player 1's stones. The
            positions on each board are numbered from 0 to 15, starting from the bottom left corner.
        actions (List[ShobuAction]): A list of legal actions (`ShobuAction` objects) available to the player who is
            next to move, based on the current state.
        count_boring_actions (int): A counter that tracks the number of consecutive actions taken
            that do not result in pushing a stone during the active move. This can be used for determining stalemate or
            draw conditions.

    The game layout is as follows, with the boards arranged in a 2x2 grid:

        Board Layout:
        [2][3] - Black's home boards
        [0][1] - White's home boards

        Position Indexing on each board:
         12 | 13 | 14 | 15
        -------------------
          8 |  9 | 10 | 11
        -------------------
          4 |  5 |  6 |  7
        -------------------
          0 |  1 |  2 |  3

    Note:
        To ease the comprihension of the board representation, the initial board configuration is represented as:
            
            board = [
                [{0, 1, 2, 3}, {12, 13, 14, 15}],
                [{0, 1, 2, 3}, {12, 13, 14, 15}],
                [{0, 1, 2, 3}, {12, 13, 14, 15}],
                [{0, 1, 2, 3}, {12, 13, 14, 15}]
            ]
    """
    to_move: int
    utility: int
    board: List[List[Set[int]]]
    actions: List[ShobuAction]
    count_boring_actions: int

class ShobuGame:
    """Represents the game logic and state management for a game of Shobu.

    This class encapsulates the game mechanics, including the initialization of the game state,
    determining legal actions, executing moves, and calculating game outcomes.

    Attributes:
        autorised_moves (list of sets): A precomputed list of legal moves for stones based on their position on the board.
        max_count_boring_actions (int): The maximum number of moves without any pushed stone before the game is considered a draw.
        initial (ShobuState): The initial state of the game with the board setup and starting player.

    Methods:
        to_move(state): Returns the player whose turn it is to move.
        actions(state): Returns a list of legal actions for the current state.
        result(state, action): Returns the state that results from executing the given action on the current state.
        is_terminal(state): Checks if the game has reached a terminal state.
        utility(state, player): Return the utility of a terminal state for a given player.
        compute_actions(board, player): Computes and returns all legal actions for the given player on the current board.
        compute_utility(board, player, actions): Computes the utility of the current board state for the given player.
    """

    autorised_moves = [
        # Row 0
        {(4, 2), (5, 2), (1, 2)},
        {(4, 2), (5, 2), (1, 2), (-1, 1), (3, 1)},
        {(4, 2), (5, 1), (1, 1), (-1, 2), (3, 2)},
        {(4, 2), (-1, 2), (3, 2)},

        # Row 1
        {(4, 2), (5, 2), (1, 2), (-3, 1), (-4, 1)},
        {(4, 2), (5, 2), (1, 2), (-3, 1), (-4, 1), (-5, 1), (-1, 1), (3, 1)},
        {(4, 2), (5, 1), (1, 1), (-3, 1), (-4, 1), (-5, 1), (-1, 2), (3, 2)},
        {(4, 2), (-4, 1), (-5, 1), (-1, 2), (3, 2)},

        # Row 2
        {(4, 1), (5, 1), (1, 2), (-3, 2), (-4, 2)},
        {(4, 1), (5, 1), (1, 2), (-3, 2), (-4, 2), (-5, 1), (-1, 1), (3, 1)},
        {(4, 1), (5, 1), (1, 1), (-3, 1), (-4, 2), (-5, 2), (-1, 2), (3, 1)},
        {(4, 1), (-4, 2), (-5, 2), (-1, 2), (3, 1)},

        # Row 3
        {(1, 2), (-3, 2), (-4, 2)},
        {(1, 2), (-3, 2), (-4, 2), (-5, 1), (-1, 1)},
        {(1, 1), (-3, 1), (-4, 2), (-5, 2), (-1, 2)},
        {(-4, 2), (-5, 2), (-1, 2)}
    ]

    def __init__(self, max_count_boring_actions=50):
        """Initializes a new game of Shobu.

        Args:
            max_count_boring_actions (int, optional): The maximum number of consecutive non-pushing actions allowed before declaring the game a draw. Defaults to 50.
        """
        self.max_count_boring_actions = max_count_boring_actions
        board = [
            [{0, 1, 2, 3}, {12, 13, 14, 15}],
            [{0, 1, 2, 3}, {12, 13, 14, 15}],
            [{0, 1, 2, 3}, {12, 13, 14, 15}],
            [{0, 1, 2, 3}, {12, 13, 14, 15}]
        ]
        actions = self.compute_actions(board, 0)
        self.initial = ShobuState(to_move=0, utility=0, board=board, actions=actions, count_boring_actions=0)

    def to_move(self, state):
        """Determines the player whose turn it is to move.

        Args:
            state (ShobuState): The current state of the game.

        Returns:
            int: The player number (0 or 1) whose turn it is to move.
        """
        return state.to_move

    def actions(self, state):
        """
        Returns a list of legal actions available for the current player in the given state.

        Args:
            state (ShobuState): The current state of the game.

        Returns:
            list of ShobuAction: A list of legal actions for the current player.
        """
        return state.actions

    def result(self, state, action):
        """
        Computes the state resulting from taking a specific action in the given state.

        Args:
            state (ShobuState): The current state of the game.
            action (ShobuAction): The action to be executed.

        Returns:
            ShobuState: The state resulting from the execution of the action.
        """
        if action not in state.actions:
            return state

        board = state.board
        next_board = [
            [set(board[0][0]), set(board[0][1])],
            [set(board[1][0]), set(board[1][1])],
            [set(board[2][0]), set(board[2][1])],
            [set(board[3][0]), set(board[3][1])],
        ]
        
        passive_board_id, passive_stone_id, active_board_id, active_stone_id, direction, length = action
        player = state.to_move
        opponent = (player + 1) % 2

        # Act passive move
        passive_board = next_board[passive_board_id]
        player_passive_stones = passive_board[player]
        
        player_passive_stones.remove(passive_stone_id)
        player_passive_stones.add(passive_stone_id + length * direction)

        # Act active move
        active_board = next_board[active_board_id]
        player_active_stones = active_board[player]
        opponent_active_stones = active_board[opponent]

        pushing = False
        opponent_active_stone = -1
        for l in range(1, length+1):
            if active_stone_id + l*direction in opponent_active_stones:
                pushing = True
                opponent_active_stone = active_stone_id + l*direction
                break
        
        player_active_stones.remove(active_stone_id)
        player_active_stones.add(active_stone_id + length * direction)

        if pushing:
            opponent_active_stones.remove(opponent_active_stone)
            new_opponent_active_stone = active_stone_id + (length+1) * direction
            if new_opponent_active_stone >= 0 and new_opponent_active_stone <= 15 and abs((active_stone_id + length * direction)%4 - (new_opponent_active_stone)%4) <= 1:
                opponent_active_stones.add(active_stone_id + (length+1) * direction)
            
        next_to_move = opponent
        next_actions = self.compute_actions(next_board, next_to_move)
        next_utility = self.compute_utility(next_board, next_to_move, next_actions)

        return ShobuState(to_move=next_to_move, utility=next_utility, board=next_board, actions=next_actions, count_boring_actions=0 if pushing else state.count_boring_actions+1)

    def is_terminal(self, state):
        """Checks if the game has reached a terminal state.

        A terminal state is reached when the game is over, either by one player winning, by reaching
        the maximum number of moves without a capture (resulting in a draw), or when one player has
        no legal moves left.

        Args:
            state (ShobuState): The current state of the game.

        Returns:
            bool: True if the game has reached a terminal state, False otherwise.
        """
        return state.utility != 0 or state.count_boring_actions >= self.max_count_boring_actions

    def utility(self, state, player):
        """Computes the utility of a terminal state for a given player.

        The utility is a numerical value representing the outcome of the game from the perspective
        of the specified player. It is used to evaluate the desirability of game outcomes. Typically,
        a positive value represents a win, a negative value represents a loss, and zero represents
        a draw.

        This function should only be called on terminal states.

        Args:
            state (ShobuState): The state of the game, which must be a terminal state.
            player (int): The player for whom to calculate the utility. This should be 0 or 1,
                        corresponding to the two players in the game.

        Returns:
            int: The utility of the state for the specified player. Common conventions include
                1 for a win, -1 for a loss, and 0 for a draw.
        """
        return state.utility if player == 0 else -state.utility
    
    def display(self, state):
        def get_row_str(board, i):
            s = ""
            for j in range(0, 4):
                white_stones = board[0]
                black_stones = board[1]
                if i*4 + j in white_stones:
                    s += "W"
                elif i*4 + j in black_stones:
                    s += "B"
                else:
                    s += "."
            return s

        s = ""
        for i in range(3, -1, -1):
            s += f"{get_row_str(state.board[2], i)}   {get_row_str(state.board[3], i)}\n"
        s += f"\n{'-'*11}\n\n"
        for i in range(3, -1, -1):
            s += f"{get_row_str(state.board[0], i)}   {get_row_str(state.board[1], i)}\n"
        
        print(s)

    def compute_actions(self, board, player):
        """Computes all legal actions for the given player on the current board.

        Args:
            board (list): The game board represented as a list of sets.
            player (int): The player number (0 or 1).

        Returns:
            list of ShobuAction: A list of all legal actions for the player.
        """
        opponent = (player + 1) % 2
        autorised_moves = ShobuGame.autorised_moves

        actions = []
        actions_append = actions.append

        for passive_board_j in range(2):
            passive_board_id = 2*player + passive_board_j
            player_passive_stones = board[passive_board_id][player]
            opponent_passive_stones = board[passive_board_id][opponent]
            all_passive_stones = player_passive_stones.union(opponent_passive_stones)
            passive_moves_dict = dict()
            for player_passive_stone in player_passive_stones:
                for direction, max_length in autorised_moves[player_passive_stone]:
                    for length in range(1, max_length+1):
                        if player_passive_stone + length * direction in all_passive_stones:
                            break
                        else:
                            if (direction, length) in passive_moves_dict:
                                passive_moves_dict[(direction, length)].append(player_passive_stone)
                            else:
                                passive_moves_dict[(direction, length)] = [player_passive_stone]

            for active_board_i in range(2):
                active_board_id = 2*active_board_i + (passive_board_j+1)%2
                player_active_stones = board[active_board_id][player]
                opponent_active_stones = board[active_board_id][opponent]
                all_active_stones = player_active_stones.union(opponent_active_stones)
                for player_active_stone in player_active_stones:
                    for direction, max_length in autorised_moves[player_active_stone]:
                        pushing = False
                        moved_player_active_stone = player_active_stone
                        for length in range(1, max_length+1):
                            if (direction, length) not in passive_moves_dict:
                                break
                            moved_player_active_stone += direction
                            if moved_player_active_stone in player_active_stones:
                                break
                            if not pushing and moved_player_active_stone in opponent_active_stones:
                                pushing = True
                            if pushing:
                                moved_opponent_active_stone = moved_player_active_stone + direction
                                if abs((moved_opponent_active_stone % 4) - (moved_player_active_stone % 4)) > 1 or moved_opponent_active_stone not in all_active_stones:
                                    for passive_stone in passive_moves_dict[(direction, length)]:
                                        actions_append(ShobuAction(passive_board_id, passive_stone, active_board_id, player_active_stone, direction, length))
                                else:
                                    break
                            else:
                                for passive_stone in passive_moves_dict[(direction, length)]:
                                    actions_append(ShobuAction(passive_board_id, passive_stone, active_board_id, player_active_stone, direction, length))

        return actions

    def compute_utility(self, board, player, actions):
        """
        Computes the utility of the current board state for the given player.

        This method is used to evaluate the state for end-game conditions.

        Args:
            board (list): The game board represented as a list of sets.
            player (int): The player number (0 or 1).
            actions (list of ShobuAction): The possible actions for the player.

        Returns:
            int: The utility value of the board state for the player. -1 for a loss, 1 for a win, or 0 if the game continues or is a draw.
        """
        if len(actions) == 0:
            return -1 if player == 0 else 1

        for white_stones, black_stones in board:
            if len(white_stones) == 0:
                return -1
            if len(black_stones) == 0:
                return 1
        
        return 0