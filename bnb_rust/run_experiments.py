import json
import subprocess
import os
from typing import Dict, Any

def load_settings() -> Dict[str, Any]:
    """Load the current settings from settings.json"""
    with open('settings.json', 'r') as f:
        return json.load(f)

def save_settings(settings: Dict[str, Any]):
    """Save settings to settings.json"""
    with open('settings.json', 'w') as f:
        json.dump(settings, indent=4, f)

def run_experiment(settings: Dict[str, Any], input_file: str):
    """Run the experiment with given settings and input file"""
    # Save the settings
    save_settings(settings)

    # Run the Rust project
    try:
        result = subprocess.run(['cargo', 'run', '--release', input_file],
                              capture_output=True,
                              text=True,
                              check=True)
        print(f"Output for {input_file}:")
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error running experiment: {e}")
        print("Output:", e.output)
        print("Error:", e.stderr)

def main():
    # Example configurations to test
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
            "time_limit": 1800
        },
        {
            "enable_local_search": False,
            "enable_max_degree_bound": True,
            "enable_sum_degree_bound": True,
            "enable_efficiency_bound": True,
            "enable_packing_bound": True,
            "enable_sum_over_packing_bound": True,
            "packing_from_scratch_limit": 3,
            "greedy_mode": "AlwaysBeforeExpensiveReductions",
            "time_limit": 1800
        }
    ]

    # Input files to test with
    input_files = [
        "path/to/your/input1.txt",  # Replace with actual input files
        "path/to/your/input2.txt"
    ]

    # Run experiments for each configuration and input file
    for config in configurations:
        print("\nRunning with configuration:", config)
        for input_file in input_files:
            print(f"\nTesting with input file: {input_file}")
            run_experiment(config, input_file)

if __name__ == "__main__":
    main()