import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set up styling - using approaches that work with newer matplotlib versions
sns.set_style("whitegrid")  # More reliable than plt.style.use()
sns.set_palette("deep")

# Sample data
neighborhood_data = pd.DataFrame({
    'name': ['Five Points', 'Capitol Hill', 'Highland', 'Cherry Creek', 'Washington Park', 
             'Montbello', 'Gateway-Green Valley Ranch', 'Auraria'],
    'crimeRate': [85, 78, 45, 32, 25, 68, 52, 55],
    'afterSchoolPrograms': [5, 8, 15, 22, 18, 7, 9, 5],
    'equityScore': [2.1, 3.2, 3.8, 4.5, 4.8, 2.3, 2.9, 3.1]
})

# 1. CRIME RATE BAR CHART
plt.figure(figsize=(12, 6))
sorted_data = neighborhood_data.sort_values('crimeRate', ascending=False)

# Create bar chart with color gradient based on crime rate
bars = plt.bar(sorted_data['name'], sorted_data['crimeRate'])

# Color the bars based on crime rate (red for high, green for low)
for i, bar in enumerate(bars):
    if sorted_data['crimeRate'].iloc[i] >= 70:
        bar.set_color('#d73027')  # Red for highest crime
    elif sorted_data['crimeRate'].iloc[i] >= 50:
        bar.set_color('#fc8d59')  # Orange for high crime
    elif sorted_data['crimeRate'].iloc[i] >= 30:
        bar.set_color('#fee090')  # Yellow for medium crime
    else:
        bar.set_color('#91cf60')  # Green for low crime

plt.title('Crime Rate by Neighborhood', fontsize=16)
plt.xlabel('Neighborhood')
plt.ylabel('Crime Rate per 1,000 Residents')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('neighborhood_crime_bars.png', dpi=300)
plt.show()

# 2. CORRELATION SCATTER PLOT
plt.figure(figsize=(10, 8))

# Create the scatter plot with regression line
sns.regplot(x='afterSchoolPrograms', y='crimeRate', data=neighborhood_data,
           scatter_kws={'s': 100, 'alpha': 0.7}, 
           line_kws={'color': 'red', 'linestyle': '--'})

# Add neighborhood labels
for i, txt in enumerate(neighborhood_data['name']):
    plt.annotate(txt, (neighborhood_data['afterSchoolPrograms'].iloc[i], 
                     neighborhood_data['crimeRate'].iloc[i]),
               fontsize=10, xytext=(5, 5), textcoords='offset points')

# Calculate and display correlation coefficient
correlation = neighborhood_data['afterSchoolPrograms'].corr(neighborhood_data['crimeRate'])
plt.annotate(f'Correlation: {correlation:.2f}', xy=(0.05, 0.95), 
            xycoords='axes fraction', fontsize=12,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))

plt.title('Relationship Between After-School Programs and Crime Rates', fontsize=16)
plt.xlabel('Number of After-School Programs', fontsize=12)
plt.ylabel('Crime Rate per 1,000 Residents', fontsize=12)
plt.tight_layout()
plt.savefig('program_crime_correlation.png', dpi=300)
plt.show()

# 3. NEIGHBORHOOD EQUITY COMPARISON
selected_neighborhoods = ['Five Points', 'Capitol Hill', 'Highland', 'Cherry Creek', 'Washington Park', 'Montbello']
subset_data = neighborhood_data[neighborhood_data['name'].isin(selected_neighborhoods)]

# Create figure with two y-axes
fig, ax1 = plt.subplots(figsize=(12, 6))
ax2 = ax1.twinx()

# Plot equity scores as bars
bars = ax1.bar(subset_data['name'], subset_data['equityScore'], color='steelblue', alpha=0.7, label='Equity Score')
ax1.set_xlabel('Neighborhood')
ax1.set_ylabel('Equity Score (1-5)', color='steelblue')
ax1.tick_params(axis='y', labelcolor='steelblue')
ax1.set_ylim(0, 5.5)

# Plot crime rates as a line
line = ax2.plot(subset_data['name'], subset_data['crimeRate'], 'ro-', label='Crime Rate')
ax2.set_ylabel('Crime Rate per 1,000', color='red')
ax2.tick_params(axis='y', labelcolor='red')

# Add title and labels
plt.title('Comparison of Equity Scores and Crime Rates by Neighborhood', fontsize=16)
plt.xticks(rotation=45, ha='right')

# Add legend
lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines + lines2, labels + labels2, loc='upper right')

plt.tight_layout()
plt.savefig('equity_crime_comparison.png', dpi=300)
plt.show()