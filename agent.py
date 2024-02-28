class Agent:
    """Represents an AI agent playing the Shobu game.

    This class provides a structure for implementing agents that can make decisions
    based on the game state. It should be subclassed to create agents with specific
    decision-making strategies.

    Attributes:
        player (int): The player ID this agent represents (0 or 1).
        game (ShobuGame): An instance of the Shobu game the agent is playing on.
    """
    def __init__(self, player, game):
        """Initializes an Agent instance.

        Args:
            player (int): The player ID this agent represents (0 or 1).
            game (ShobuGame): The Shobu game instance the agent will play on.
        """
        self.player = player
        self.game = game
    
    def play(self, state, remaining_time):
        """Determines the action the agent will take in the given game state.

        This method should be overridden by subclasses to implement specific
        decision-making algorithms.

        Args:
            state (ShobuState): The current state of the game.
            remaining_time (float): The remaining time in seconds that the agent has to make a decision.

        Returns:
            ShobuAction: The action chosen by the agent to be played on the state.

        Raises:
            NotImplementedError: If the method is not overridden in a subclass.
        """
        raise NotImplementedError