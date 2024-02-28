from shobu import ShobuAction

def create_log(action, n_move):
    if action is not None:
        return f"{n_move}:{action.passive_board_id}:{action.passive_stone_id}:{action.active_board_id}:{action.active_stone_id}:{action.direction}:{action.length}"
    else:
        return ""
    
def write_logs(logs, log_file):
    print(f"Writing logs to {log_file}")
    with open(log_file, "w") as f:
        for s in logs:
            f.write(f"{s}\n")

def convert_log_to_action(log):
    if log == "":
        return None
    else:
        parts = [int(part) for part in log.split(":")]
        n_move = parts[0]
        action = ShobuAction(parts[1], parts[2], parts[3], parts[4], parts[5], parts[6])
        return n_move, action

def read_logs(file):
    print("Loading logs...", end="")
    actions = []
    with open(file, "r") as f:
        for line in f:
            n_move, action = convert_log_to_action(line.strip())
            actions.append((action, n_move))
    print(" done")
    return actions