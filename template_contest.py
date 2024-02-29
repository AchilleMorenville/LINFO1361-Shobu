from agent import Agent
import random

class AI(Agent):
    """An agent that plays following your algorithm.

    This agent extends the base Agent class, providing an implementation your agent.

    Attributes:
        player (int): The player id this agent represents.
        game (ShobuGame): The game the agent is playing.
    """

    def play(self, state, remaining_time):
        """Determines the next action to take in the given state.

        Args:
            state (ShobuState): The current state of the game.
            remaining_time (float): The remaining time in seconds that the agent has to make a decision.

        Returns:
            ShobuAction: The chosen action.
        """
        ...
