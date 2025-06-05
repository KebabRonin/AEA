import json
import subprocess
import os
import time
from typing import Dict, Any, List
from pathlib import Path
import tqdm

def load_settings() -> Dict[str, Any]:
    """Load the current settings from settings.json"""
    with open('settings.json', 'r') as f:
        return json.load(f)

def save_settings(settings: Dict[str, Any]):
    """Save settings to settings.json"""
    with open('settings.json', 'w') as f:
        json.dump(settings, f, indent=4)

def run_experiment(settings: Dict[str, Any], input_file: str, run_number: int) -> Dict[str, Any]:
    """Run the experiment with given settings and input file"""
    # Save the settings
    save_settings(settings)

    # Prepare output files
    solution_file = f"../sol_{run_number}.json"
    report_file = f"../report_{run_number}.json"

    # Run the Rust project
    start_time = time.time()
    try:
        # Run without capturing output to see it in real-time
        result = subprocess.run([
            'cargo', 'run', 'solve',
            input_file, 'settings.json',
            '--hgr', '--solution', solution_file,
            '--report', report_file
        ], check=True)

        end_time = time.time()
        execution_time = end_time - start_time

        # Read the solution and report
        solution = {}
        report = {}
        try:
            with open(solution_file, 'r') as f:
                solution = json.load(f)
            with open(report_file, 'r') as f:
                report = json.load(f)
        except Exception as e:
            print(f"Error reading output files: {e}")

        # Clean up temporary files
        try:
            os.remove(solution_file)
            os.remove(report_file)
        except:
            pass

        return {
            "run_number": run_number,
            "execution_time": execution_time,
            "solution": solution,
            "report": report
        }

    except subprocess.CalledProcessError as e:
        print(f"\nError in run {run_number}: {e}")
        return {
            "run_number": run_number,
            "error": str(e)
        }

def main():
    # Example configurations to test
    starttime = int(time.time())
    os.makedirs(f"{starttime}", exist_ok=True)
    configurations = [
        {
            "enable_local_search": True,
            "enable_max_degree_bound": True,
            "enable_sum_degree_bound": True,
            "enable_efficiency_bound": True,
            "enable_packing_bound": True,
            "enable_sum_over_packing_bound": True,
            "packing_from_scratch_limit": 3,
            "greedy_mode": "AlwaysBeforeExpensiveReductions",
            "time_limit": 10 * 60
        },
        {
            "enable_local_search": False,
            "enable_max_degree_bound": True,
            "enable_sum_degree_bound": False,
            "enable_efficiency_bound": True,
            "enable_packing_bound": True,
            "enable_sum_over_packing_bound": True,
            "packing_from_scratch_limit": 3,
            "greedy_mode": "Once",
            "time_limit": 10 * 60
        }
    ]
    # Input file to test with
    for infile in [200, 250, 300]: # 20, 50, 100, 150,
        input_file = f"../Proj/testset/bremen_subgraph_{infile}.hgr"
        num_runs = 1

        # Store all results
        all_results = []

        # Run experiments for each configuration
        for config_idx, config in enumerate(configurations):
            print(f"\nRunning configuration {config_idx + 1}/{len(configurations)}")
            config_results = []

            for run in tqdm.trange(num_runs):
                result = run_experiment(config, input_file, run)
                config_results.append(result)

                # Print summary of this run
                if "error" not in result:
                    print(f"Time: {result['execution_time']:.2f}s")
                    if "solution" in result and result["solution"]:
                        print(f"Best solution found: {result['solution']}")
                else:
                    print(f"Error in run: {result['error']}")

            all_results.append({
                "configuration": config,
                "runs": config_results
            })

        # Save all results to a JSON file
        output_file = f"{starttime}/experiment_results_{infile}_cfg_{config_idx}.json"
        with open(output_file, 'w') as f:
            json.dump(all_results, f, indent=2)

        print(f"\nAll results have been saved to {output_file}")

if __name__ == "__main__":
    main()