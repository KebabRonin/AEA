import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.stats.multicomp import MultiComparison
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

# Function to perform statistical analysis for a specific folder
def analyze_folder(folder_data):
    # Create a unique identifier for each configuration
    folder_data = folder_data.copy()  # Create a copy to avoid SettingWithCopyWarning
    folder_data['config_id'] = folder_data['config'].apply(lambda x: str(sorted(x.items())))

    # Prepare data for ANOVA
    # We'll use the time_mean and time_std to simulate the 30 runs
    groups = []
    group_labels = []

    for config_id, group in folder_data.groupby('config_id'):
        # Generate 30 samples using the mean and std
        mean = group['time_mean'].iloc[0]
        std = group['time_std'].iloc[0]
        samples = np.random.normal(mean, std, 30)
        groups.append(samples)
        group_labels.append(config_id)

    # Check if we have enough groups for ANOVA
    if len(groups) < 2:
        print("Not enough different configurations for ANOVA")
        return

    # Perform ANOVA
    try:
        f_stat, p_value = stats.f_oneway(*groups)

        print(f"\nANOVA Results:")
        print(f"F-statistic: {f_stat:.4f}")
        print(f"p-value: {p_value:.4f}")

        if p_value < 0.05:
            print("There are significant differences between configurations (p < 0.05)")

            # Perform Tukey's HSD test
            # Prepare data for Tukey's test
            data = []
            labels = []
            for i, group in enumerate(groups):
                data.extend(group)
                labels.extend([group_labels[i]] * len(group))

            mc = MultiComparison(data, labels)
            tukey_result = mc.tukeyhsd()

            print("\nTukey's HSD Test Results:")
            print(tukey_result)

            # Find significantly different pairs
            significant_pairs = []
            for i in range(len(tukey_result.groupsunique)):
                for j in range(i+1, len(tukey_result.groupsunique)):
                    if tukey_result.reject[i,j]:
                        significant_pairs.append((tukey_result.groupsunique[i],
                                               tukey_result.groupsunique[j],
                                               tukey_result.meandiffs[i,j],
                                               tukey_result.pvalues[i,j]))

            if significant_pairs:
                print("\nSignificantly different configuration pairs:")
                for pair in significant_pairs:
                    print(f"\nConfigurations {pair[0]} and {pair[1]}:")
                    print(f"Mean difference: {pair[2]:.4f}")
                    print(f"p-value: {pair[3]:.4f}")

                    # Get the actual configurations
                    config1 = eval(pair[0])
                    config2 = eval(pair[1])
                    print("Configuration 1:", dict(config1))
                    print("Configuration 2:", dict(config2))
        else:
            print("No significant differences found between configurations (p >= 0.05)")

    except Exception as e:
        print(f"Error performing ANOVA: {str(e)}")
        print("Data summary:")
        for i, group in enumerate(groups):
            print(f"\nGroup {i} (Config {group_labels[i]}):")
            print(f"Mean: {np.mean(group):.4f}")
            print(f"Std: {np.std(group):.4f}")
            print(f"Size: {len(group)}")

# Analyze each folder separately
for folder in folders:
    folder_data = combined_df[combined_df['folder'] == folder]
    if not folder_data.empty:
        print(f"\n{'='*50}")
        print(f"Analysis for Folder {folder}")
        print(f"{'='*50}")
        analyze_folder(folder_data)

        # Print basic statistics
        print(f"\nBasic Statistics for Folder {folder}:")
        print(f"Number of configurations: {len(folder_data)}")
        print(f"Overall mean time: {folder_data['time_mean'].mean():.4f} seconds")
        print(f"Overall std time: {folder_data['time_mean'].std():.4f} seconds")
        print(f"Min time: {folder_data['time_mean'].min():.4f} seconds")
        print(f"Max time: {folder_data['time_mean'].max():.4f} seconds")