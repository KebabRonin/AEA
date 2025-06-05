import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import json

# List of test folders
folders = ['20', '50', '100', '150', '200', '250', '300']

# Initialize empty DataFrames to store results
all_results = []

# Read results from each folder
for folder in folders:
    if os.path.exists(f"{folder}/rezults_bnbt1.json"):
        df = pd.read_json(f"{folder}/rezults_bnbt1.json")
        df['folder'] = folder
        all_results.append(df)

# Combine all results
combined_df = pd.concat(all_results, ignore_index=True)

# Create figure with three subplots for the first two plots
plt.figure(figsize=(15, 10))
plt.grid(True)
# gs = fig1.add_gridspec(2, 1, height_ratios=[1, 1])
# ax1 = fig1.add_subplot(gs[0])
# ax2 = fig1.add_subplot(gs[1])

# Boxplot and scatter for mean time
sns.boxplot(data=combined_df, x='folder', y='time_mean', color='lightblue', width=0.5)
sns.stripplot(data=combined_df, x='folder', y='time_mean', color='darkblue', size=4, alpha=0.5)
plt.title('Mean Time Distribution by Test Instance')
plt.xlabel('Test Instance')
plt.ylabel('Mean Time (seconds)')
# plt.yscale('log')
# Adjust layout and save first figure
plt.tight_layout()
plt.savefig('configuration_comparison_boxplots_time_nolog.png', dpi=300, bbox_inches='tight')
plt.close()
# Boxplot and scatter for nodes processed
plt.figure(figsize=(15, 10))
plt.grid(True)
sns.boxplot(data=combined_df, x='folder', y='nodes', color='lightgreen', width=0.5)
sns.stripplot(data=combined_df, x='folder', y='nodes', color='darkgreen', size=4, alpha=0.5)
plt.title('Nodes Processed Distribution by Test Instance')
plt.xlabel('Test Instance')
plt.ylabel('Number of Nodes Processed')
# plt.yscale('log')

# Adjust layout and save first figure
plt.tight_layout()
plt.savefig('configuration_comparison_boxplots_nodes.png', dpi=300, bbox_inches='tight')
plt.close()

# Create separate line plots for each folder
for folder in folders:
    folder_data = combined_df[combined_df['folder'] == folder]
    if not folder_data.empty:
        # Sort by time_mean and create a new index for x-axis
        sorted_df = folder_data.sort_values('time_mean')
        sorted_df['config_index'] = range(len(sorted_df))

        # Create new figure for this folder
        plt.figure(figsize=(12, 6))

        # Plot line with scatter points
        plt.plot(sorted_df['config_index'], sorted_df['time_mean'], 'b-', alpha=0.5, label='Time progression')
        plt.scatter(sorted_df['config_index'], sorted_df['time_mean'], c='blue', s=20, alpha=0.6)

        plt.title(f'Progression of Mean Times for Folder {folder}')
        plt.xlabel('Configuration Index (sorted by time)')
        plt.ylabel('Mean Time (seconds)')
        plt.grid(True, alpha=0.3)

        # Adjust layout
        plt.tight_layout()

        # Save figure
        plt.savefig(f'configuration_comparison_folder_{folder}.png', dpi=300, bbox_inches='tight')
        plt.close()

# Print some statistics
print("\nStatistics by folder:")
for folder in folders:
    folder_data = combined_df[combined_df['folder'] == folder]
    if not folder_data.empty:
        print(f"\nFolder {folder}:")
        print(f"Mean time: {folder_data['time_mean'].mean():.4f} seconds")
        print(f"Mean nodes: {folder_data['nodes'].mean():.2f}")
        print(f"Number of configurations: {len(folder_data)}")