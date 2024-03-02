from random_agent import RandomAgent
from template_alphabeta import AlphaBetaAgent
from template_uct import UCTAgent
from template_contest import AI
from shobu import ShobuAction, ShobuState, ShobuGame

from logs import *
from interface import *

import argparse
import time

def get_agents(args, display):

    def get_agent(player, agent_name):
        if agent_name == "human":
            return HumanAgent(player)
        elif agent_name == "random":
            return RandomAgent(player, ShobuGame())
        elif agent_name == "alphabeta":
            return AlphaBetaAgent(player, ShobuGame(), 2)
        elif agent_name == "mcts":
            return UCTAgent(player, ShobuGame(), 1000)
        elif agent_name == "agent":
            return AI(player, ShobuGame())
        else:
            raise Exception(f"Invalid player: {agent_name}")
    
    if not display and (args.white == "human" or args.black == "human"):
        raise Exception("Cannot have human player without display")
    
    return get_agent(0, args.white), get_agent(1, args.black)

def main(agent_white, agent_black, display=False, log_file=None, play_time=600):

    game = ShobuGame()
    state = game.initial

    run = 1
    logs = []
    n_moves = 0

    if display:
        init_pygame()

    remaining_time_0 = play_time
    remaining_time_1 = play_time

    try:
        while not game.is_terminal(state) and run != -1 and remaining_time_0 > 0 and remaining_time_1 > 0:
            if n_moves > 10000:
                return -1, n_moves
            
            if run == 1:
                
                if game.to_move(state) == 0:
                    t0 = time.perf_counter()
                    action = agent_white.play(state, remaining_time_0)
                    while action == -2:
                        action = agent_white.play(state, remaining_time_0)
                    if play_time is not None:
                        remaining_time_0 -= time.perf_counter() - t0
                elif game.to_move(state) == 1:
                    t0 = time.perf_counter()
                    action = agent_black.play(state, remaining_time_1)
                    while action == -2:
                        action = agent_black.play(state)
                    if play_time is not None:
                        remaining_time_1 -= time.perf_counter() - t0
                else:
                    raise Exception(f"Invalid player: {state.to_move}")
                
                if log_file is not None:
                    logs.append(create_log(action, n_moves))

                if action not in game.actions(state):
                    raise Exception(f"Invalid action: {action}")
                
                state = game.result(state, action)

                n_moves += 1

            if display:
                run = update_ui(state)
        
    except Exception as e:
        if log_file is not None:
            write_logs(logs, log_file)
        raise e
    
    if remaining_time_0 <= 0:
        state = state._replace(utility=-1)
    if remaining_time_1 <= 0:
        state = state._replace(utility=1)

    while run != -1 and display:
        run = update_ui(state)

    if log_file is not None:
        write_logs(logs, log_file)

    if game.utility(state, 0) == 0:
        return -1, n_moves
    elif game.utility(state, 0) == 1:
        return 0, n_moves
    else:
        return 1, n_moves

def replay_game(actions, delay_time=0.0, display=True, start_turn=0):
    game = ShobuGame()
    state = game.initial
    if display:
        init_pygame()
    
    for action, n_move in actions:
        if action is not None:
            if n_move >= start_turn:
                state = game.result(state, action)
                if display:
                    run = update_ui(state)
                    if run == -1:
                        return
                time.sleep(delay_time)
            else:
                state = game.result(state, action)
    run = 1
    while run != -1 and display:
        run = update_ui(state)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Shobu game')
    parser.add_argument('-w', '--white', type=str, default="random", help='White player ["random | human | alphabeta | mcts | agent"]')
    parser.add_argument('-b', '--black', type=str, default="random", help='Black player ["random | human | alphabeta | mcts | agent"]')
    parser.add_argument('-t', '--time', type=int, default=600, help='Time per game for each player (in seconds)')
    parser.add_argument('-d', '--display', action='store_true', help='Display game')
    parser.add_argument('-l', '--logs', type=str, default=None, help='path to log file to record the game')
    parser.add_argument('-dt', '--delay_time', type=float, default=0.0, help='Delay time between moves (in seconds)')
    parser.add_argument('-r', '--replay', type=str, default=None, help='Path to log file to replay the game')
    parser.add_argument('-st', '--start_turn', type=int, default=0, help='Start turn for replaying the game')
    parser.add_argument('-n', '--n', type=int, default=1, help='Run N games and report stats')
    args = parser.parse_args()

    if args.replay is not None:
        actions = read_logs(args.replay)
        replay_game(actions, args.delay_time, display=args.display, start_turn=args.start_turn)
    elif args.n > 1:
        winners = {
            0: 0,
            1: 0,
            -1: 0
        }
        total_moves = []
        agent_white, agent_black = get_agents(args, args.display)
        for i in range(0, args.n):
            if i % 25 == 0 and i > 0:
                print(f"{i} -> White : {winners[0] / (i+1)}, Black : {winners[1] / (i+1)}, Draw : {winners[-1] / (i+1)}, mean numer of moves : {sum(total_moves) / len(total_moves)}")
            log_file = args.logs
            winner, n_moves = main(agent_white, agent_black, display=args.display, log_file=log_file)
            winners[winner] += 1
            total_moves.append(n_moves)
        print(f" White : {winners[0] / args.n}, Black : {winners[1] / args.n}, Draw : {winners[-1] / args.n}, mean numer of moves : {sum(total_moves) / len(total_moves)}")
    else:
        log_file = args.logs
        agent_white, agent_black = get_agents(args, args.display)
        winner, n_moves = main(agent_white, agent_black, display=args.display, log_file=log_file, play_time=args.time)
        print(f"Winner: {winner}, n_moves: {n_moves}")