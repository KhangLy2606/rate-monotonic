import math
import sys

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def lcm(a, b):
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // gcd(a, b)

def calculate_hyperperiod(tasks):
    if not tasks:
        return 0
    periods = [task['period'] for task in tasks]
    multiplier = 1
    for p in periods:
        if isinstance(p, float):
            s = str(p)
            if '.' in s:
                decimal_places = len(s.split('.')[1])
                multiplier = max(multiplier, 10**decimal_places)
    
    scaled_periods = [int(round(p * multiplier)) for p in periods]
    
    if len(scaled_periods) == 1:
        hyperperiod_scaled = scaled_periods[0]
    else:
        hyperperiod_scaled = scaled_periods[0]
        for i in range(1, len(scaled_periods)):
            hyperperiod_scaled = lcm(hyperperiod_scaled, scaled_periods[i])
            
    return hyperperiod_scaled / multiplier

class Task:
    def __init__(self, id, execution_time, period, deadline):
        self.id = id
        self.execution_time = float(execution_time)
        self.period = float(period)
        self.deadline = float(deadline)
        self.preemptions = 0
        
    def __repr__(self):
        return f"Task(id={self.id}, e={self.execution_time}, p={self.period}, d={self.deadline})"

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
                        if e <= 0 or p <= 0 or d <= 0:
                            print(f"Error: All values must be positive on line {i+1}", file=sys.stderr)
                            return None
                        tasks.append(Task(len(tasks), e, p, d)) 
                    except ValueError:
                        print(f"Error: Invalid number format on line {i+1}", file=sys.stderr)
                        return None
                else:
                    print(f"Error: Invalid format on line {i+1}", file=sys.stderr)
                    return None
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.", file=sys.stderr)
        return None
    return tasks

def simulate_dm(tasks):
    if not tasks:
        return True, []
    
    task_dict = [{'period': task.period} for task in tasks]
    hyperperiod = calculate_hyperperiod(task_dict)
    
    if hyperperiod == 0:
        return True, [0] * len(tasks)
    
    for task in tasks:
        task.preemptions = 0
    
    time_step = 0.001
    current_time = 0.0
    
    job_queue = []
    running_job = None
    
    job_arrivals = []
    for task in tasks:
        arrival_time = 0.0
        while arrival_time < hyperperiod:
            job_arrivals.append({
                'task': task,
                'arrival_time': arrival_time,
                'absolute_deadline': arrival_time + task.deadline,
                'remaining_execution': task.execution_time
            })
            arrival_time += task.period
    
    job_arrivals.sort(key=lambda x: x['arrival_time'])
    arrival_index = 0
    
    while current_time < hyperperiod:

        while (arrival_index < len(job_arrivals) and 
               job_arrivals[arrival_index]['arrival_time'] <= current_time + time_step/2):
            job_queue.append(job_arrivals[arrival_index])
            arrival_index += 1
        
        for job in job_queue:
            if job['absolute_deadline'] < current_time and job['remaining_execution'] > 0:
                return False, []
        
        job_queue = [job for job in job_queue if job['remaining_execution'] > 0]
        
        job_queue.sort(key=lambda x: x['task'].deadline)
        
        new_running_job = job_queue[0] if job_queue else None
        
        if running_job and new_running_job:
            if running_job['task'].id != new_running_job['task'].id:
                # Preemption 
                running_job['task'].preemptions += 1
        
        running_job = new_running_job
        
        if running_job:
            execution_amount = min(time_step, running_job['remaining_execution'])
            running_job['remaining_execution'] -= execution_amount
            
            if running_job['remaining_execution'] <= 0:
                running_job = None
        
        current_time += time_step
        current_time = round(current_time, 3)
    

    for job in job_queue:
        if job['remaining_execution'] > time_step/2: 
            return False, []
    
    preemption_counts = [task.preemptions for task in tasks]
    return True, preemption_counts

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
        print()
        return
    
    is_schedulable, preemptions = simulate_dm(tasks)
    
    if is_schedulable:
        print(1)
        print(','.join(map(str, preemptions)))
    else:
        print(0)
        print()

if __name__ == "__main__":
    main()