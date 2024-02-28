from agent import Agent
import random
import math

class Node:
    """Node Class

    A node in the MCTS tree.

    Attributes:
        parent (Node): The parent node of this node.
        state (ShobuState): The game state represented by this node.
        U (int): The total reward of the node. 
        N (int): The number of times the node has been visited.
        children (dict[Node, ShobuAction]): A dictionary mapping child nodes to their corresponding actions that lead to the state they represent.
    """
    def __init__(self, parent, state):
        """Initializes a new Node object.

        Args:
            parent (Node): The parent node of this node.
            state (ShobuState): The game state represented by this node.
        """
        self.parent = parent
        self.state = state
        self.U = 0
        self.N = 0
        self.children = {}

class UCTAgent(Agent):
    """An agent that uses the UCT algorithm to determine the best move.

    This agent extends the base Agent class, providing an implementation of the play
    method that utilizes UCT version of the MCTS algorithm.

    Attributes:
        player (int): The player id this agent represents.
        game (ShobuGame): The game the agent is playing.
        iteration (int): The number of simulations to perform in the UCT algorithm.
    """

    def __init__(self, player, game, iteration):
        """Initializes a UCTAgent with a specified player, game, and number of iterations.

        Args:
            player (int): The player id this agent represents.
            game (ShobuGame): The game the agent is playing.
            iteration (int): The number of simulations to perform in the UCT algorithm.
        """
        super().__init__(player, game)
        self.iteration = iteration

    def play(self, state, remaining_time):
        """Determines the next action to take in the given state.

        Args:
            state (ShobuState): The current state of the game.
            remaining_time (float): The remaining time in seconds that the agent has to make a decision.

        Returns:
            ShobuAction: The chosen action.
        """
        return self.uct(state)

    def uct(self, state):
        """Executes the UCT algorithm to find the best action from the current state.

        Args:
            state (ShobuState): The current state of the game.

        Returns:
            ShobuAction: The action leading to the best-perceived outcome based on UCT algorithm.
        """
        root = Node(None, state)
        for _ in range(self.iteration):
            leaf = self.select(root)
            child = self.expand(leaf)
            result = self.simulate(child.state)
            self.back_propagate(result, child)
        max_state = max(root.children, key=lambda n: n.N)
        return root.children.get(max_state)

    def select(self, node):
        """Selects a leaf node using the UCB1 formula to maximize exploration and exploitation.

        A node is considered a leaf if it has a potential child from which no simulation has yet been initiated or when the game is finished.

        Args:
            node (Node): The node to select from.

        Returns:
            Node: The selected leaf node.
        """
        ...
    
    def expand(self, node):
        """Expands a node by adding a child node to the tree for an unexplored action.

        This function generates all possible actions from the current state represented by the node if they haven't been explored yet. 
        For each unexplored action, a new child node is created, representing the state resulting from that action. The function then 
        selects one of these new child nodes and returns it. If the node represents a terminal state it effectively returns the node itself, 
        indicating that the node cannot be expanded further.

        Args:
            node (Node): The node to expand. This node represents the current state from which we want to explore possible actions.

        Returns:
            Node: The newly created child node representing the state after an unexplored action. If the node is at a terminal state, the node itself is returned.
        """
        ...

    def simulate(self, state):
        """Simulates a random play-through from the given state to a terminal state.

        Args:
            state (ShobuState): The state to simulate from.

        Returns:
            float: The utility value of the terminal state for the player to move.
        """
        ...

    def back_propagate(self, result, node):
        """Propagates the result of a simulation back up the tree, updating node statistics.

        Args:
            result (float): The result of the simulation.
            node (Node): The node to start backpropagation from.
        """
        ...

    def UCB1(self, node):
        """Calculates the UCB1 value for a given node.

        Args:
            node (Node): The node to calculate the UCB1 value for.

        Returns:
            float: The UCB1 value.
        """
        ...