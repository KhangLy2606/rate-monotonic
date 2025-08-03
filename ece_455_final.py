import sys
import math
import heapq



def calculate_hyperperiod(tasks):
    if not tasks:
        return 0
    periods = []
    for task in tasks:
        if task.period > 0:
            period_ms = int(round(task.period * 1000))
            periods.append(period_ms)
    if not periods:
        return 0
    
    h = 1
    for p in periods:
        if p > 0:
            h = math.lcm(h, p)
    return h


class Task:
    def __init__(self, task_id, exec_time, period, deadline):
        self.id = task_id
        # Use round() for more accurate conversion
        self.exec_time = int(round(exec_time * 1000))
        self.period = int(round(period * 1000))
        self.deadline = int(round(deadline * 1000))
        self.priority = -1
        self.remaining_exec_time = 0
        self.absolute_deadline = 0
        self.next_release_time = 0
        self.preemption_count = 0

    def __lt__(self, other):
        return self.id < other.id

    def __repr__(self):
        return f"Task(id={self.id}, e={self.exec_time}, p={self.period}, d={self.deadline})"


def read_tasks(filename):
    tasks = []
    try:
        with open(filename, 'r') as f:
            for i, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                parts = line.split(',')
                if len(parts) == 3:
                    try:
                        e, p, d = map(float, parts)
                        if e <= 0 or p < 0 or d <= 0:
                            print(
                                f"Error: Execution and deadline must be positive on line {i+1}", file=sys.stderr)
                            return None
                        tasks.append(
                            Task(task_id=i, exec_time=e, period=p, deadline=d))
                    except ValueError:
                        print(
                            f"Error: Invalid number format on line {i+1}", file=sys.stderr)
                        return None
                else:
                    print(
                        f"Error: Invalid format on line {i+1}", file=sys.stderr)
                    return None
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.", file=sys.stderr)
        return None
    return tasks


def simulate_dm(tasks):

    # Assigns priorities based on deadlines
    tasks_sorted_by_deadline = sorted(tasks, key=lambda t: t.deadline)
    for i, task in enumerate(tasks_sorted_by_deadline):
        task.priority = i

    # Runs the simulation for one hyperperiod
    sim_duration = calculate_hyperperiod(tasks)
    if sim_duration == 0 and tasks:
        sim_duration = max(t.exec_time for t in tasks) if tasks else 0

    ready_queue = []
    running_task = None
    deadline_missed = False

    # Manages task releases, preemptions, and deadline checks
    for current_time in range(sim_duration):
        for task in tasks:
            if (task.period > 0 and current_time == task.next_release_time) or \
               (task.period == 0 and current_time == 0):
                if task.remaining_exec_time > 0:
                    deadline_missed = True
                    break
                task.remaining_exec_time = task.exec_time
                task.absolute_deadline = current_time + task.deadline
                if task.period > 0:
                    task.next_release_time += task.period
                heapq.heappush(ready_queue, (task.priority, task.id, task))

        if deadline_missed:
            break

        highest_priority_ready_tuple = ready_queue[0] if ready_queue else None

        # Tracks deadline misses and preemption counts
        if running_task:
            if highest_priority_ready_tuple and highest_priority_ready_tuple[0] < running_task.priority:
                running_task.preemption_count += 1
                heapq.heappush(
                    ready_queue, (running_task.priority, running_task.id, running_task))
                _, _, running_task = heapq.heappop(ready_queue)
        elif highest_priority_ready_tuple:
            _, _, running_task = heapq.heappop(ready_queue)

        if running_task:
            running_task.remaining_exec_time -= 1
            if running_task.remaining_exec_time == 0:
                if current_time + 1 > running_task.absolute_deadline:
                    deadline_missed = True
                    break
                running_task = None

    if not deadline_missed:
        for task in tasks:
            if task.remaining_exec_time > 0:
                deadline_missed = True
                break

    tasks_in_original_order = sorted(tasks, key=lambda t: t.id)
    preemption_counts = [t.preemption_count for t in tasks_in_original_order]

    return not deadline_missed, preemption_counts


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 ece_455_final.py <task_file.txt>", file=sys.stderr)
        sys.exit(1)

    task_file = sys.argv[1]
    tasks = read_tasks(task_file)

    if tasks is None:
        sys.exit(1)

    if not tasks:
        print(1)
        print("")
        return

    is_schedulable, preemptions = simulate_dm(tasks)

    if is_schedulable:
        print(1)
        print(','.join(map(str, preemptions)))
    else:
        print(0)
        print("")


if __name__ == "__main__":
    main()
