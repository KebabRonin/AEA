import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
import numpy as np

# List of test folders
folders = ['20', '50', '100', '150', '200', '300']

# Create figure
plt.figure(figsize=(15, 8))

# Process each folder separately
for folder in folders:
    if os.path.exists(f"{folder}/rezults_bnbt1.json"):
        # Read data for this folder
        df = pd.read_json(f"{folder}/rezults_bnbt1.json")
        # Convert config dictionary to string for indexing
        df['config_str'] = df['config'].apply(lambda x: json.dumps(x, sort_keys=True))

        # Sort by config_str to ensure consistent ordering
        df = df.sort_values('config_str')

        # Save sorted dataframe to JSON
        df.to_json(f"{folder}/sorted_results.json", orient='records', indent=2)

        # Plot this folder's data as a line
        plt.plot(range(len(df)), df['time_mean'],
                label=f'Size {folder}',
                marker='o',  # Add markers for each point
                markersize=4,  # Small markers
                alpha=0.7)  # Slightly transparent

# Customize the plot
plt.title('Mean Times Across Test Instances')
plt.xlabel('Configuration Index')
plt.ylabel('Mean Time (seconds)')
plt.legend(title='Test Instance Size', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True, alpha=0.3)

# Add ticks for configuration index every 10 indices
if os.path.exists(f"{folders[-1]}/rezults_bnbt1.json"):
    df = pd.read_json(f"{folders[-1]}/rezults_bnbt1.json")
    num_configs = len(df)
    plt.xticks(range(0, num_configs, 10), range(0, num_configs, 10), rotation=45)

# Find plateau configurations and save to JSON
if os.path.exists(f"{folders[-1]}/rezults_bnbt1.json"):
    df = pd.read_json(f"{folders[-1]}/rezults_bnbt1.json")
    df['config_str'] = df['config'].apply(lambda x: json.dumps(x, sort_keys=True))
    df = df.sort_values('config_str')

    # Calculate time differences between consecutive configurations
    time_diffs = df['time_mean'].diff().abs()
    # Find significant changes (plateau starts)
    threshold = time_diffs.std() * 2  # Use 2 standard deviations as threshold
    plateau_starts = time_diffs[time_diffs > threshold].index

    # Create list of plateau configurations
    plateau_configs = []
    for idx in plateau_starts:
        config = df.loc[idx, 'config']
        time = df.loc[idx, 'time_mean']
        plateau_configs.append({
            'config_index': int(idx),
            'config': config,
            'time_mean': float(time)
        })

    # Save plateau configurations to JSON
    with open('plateau_configs.json', 'w') as f:
        json.dump(plateau_configs, f, indent=2)

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Save the figure
plt.savefig('stacked_times_comparison.png', dpi=300, bbox_inches='tight')
plt.close()

# Analyze configurations with high time means
print("\nAnalyzing configurations with high time means:")
for folder in folders:
    if os.path.exists(f"{folder}/rezults_bnbt1.json"):
        df = pd.read_json(f"{folder}/rezults_bnbt1.json")
        df['config_str'] = df['config'].apply(lambda x: json.dumps(x, sort_keys=True))
        df = df.sort_values('config_str')

        # Calculate the mean and std of time_mean
        mean_time = df['time_mean'].mean()
        std_time = df['time_mean'].std()

        # Find configurations with time_mean > mean + std
        high_time_configs = df[df['time_mean'] > mean_time + std_time]

        print(f"\nFolder {folder}: ({df['nodes'].unique()}) ({df['objective'].unique()})")
        print(f"Mean time: {mean_time:.4f}")
        print(f"Std time: {std_time:.4f}")
        print("\nConfigurations with high time means:")
        print(f"{df['time_mean'].min():.6f} & {df['time_mean'].max():.6f} & {df['time_mean'].mean():.6f} & {df['time_mean'].std():.6f}")
        # for idx, row in high_time_configs.iterrows():
        #     print(f"Config {idx}:")
        #     print(f"  Time mean: {row['time_mean']:.4f}")
        #     print(f"  Config: {row['config']}")
        #     print(f"  Nodes: {row['nodes']}")
        #     print()

# Create and save ordered dataframe with all results
all_data = []
for folder in folders:
    if os.path.exists(f"{folder}/rezults_bnbt1.json"):
        df = pd.read_json(f"{folder}/rezults_bnbt1.json")
        df['config_str'] = df['config'].apply(lambda x: json.dumps(x, sort_keys=True))
        df['folder'] = folder
        all_data.append(df)

if all_data:
    # Combine all data
    combined_df = pd.concat(all_data, ignore_index=True)

    # Sort by config_str and folder
    combined_df = combined_df.sort_values(['config_str', 'folder'])

    # Save to CSV
    combined_df.to_csv('ordered_results.csv', index=False)

    # Print the dataframe
    # print("\nOrdered Results:")
    # print(combined_df[['config_str', 'folder', 'time_mean', 'nodes']].to_string())