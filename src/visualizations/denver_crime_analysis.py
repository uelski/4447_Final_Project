#!/usr/bin/env python3
"""
Denver Crime Data Visualization Script
Focused on creating clear, impactful visualizations using count data only
No regression or ML - pure visualization for presentation

Team: Moose, Stuti, and Sam
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Color schemes for consistency
COLORS = {
    'primary': '#3498db',
    'danger': '#e74c3c',
    'success': '#27ae60',
    'warning': '#f39c12',
    'info': '#9b59b6'
}

def load_count_data():
    """Load only the essential count CSV files."""
    print("Loading count data files...")
    
    data = {}
    
    # Load the three essential files
    try:
        data['crime'] = pd.read_csv('./data/processed/neighborhood_crime_counts.csv')
        print(f"✓ Loaded neighborhood_crime_counts.csv: {data['crime'].shape}")
    except Exception as e:
        print("✗ Could not load neighborhood_crime_counts.csv")
        print(e)
        return None
    
    try:
        data['programs'] = pd.read_csv('./data/processed/school_programs_counts.csv')
        print(f"✓ Loaded school_programs_counts.csv: {data['programs'].shape}")
    except:
        print("✗ Could not load school_programs_counts.csv")
    
    try:
        data['crime_detail'] = pd.read_csv('./data/processed/crime_counts.csv')
        print(f"✓ Loaded crime_counts.csv: {data['crime_detail'].shape}")
    except:
        print("✗ Could not load crime_counts.csv")
    
    return data

def prepare_visualization_data(data):
    """Prepare and merge data for visualization."""
    print("\nPreparing data for visualization...")
    
    # Start with the main crime data
    df = data['crime'].copy()
    
    # Add program counts if available
    if 'programs' in data:
        programs = data['programs']
        df = df.merge(programs, on='neighborhood', how='left')
        df['program_count'] = df['program_count'].fillna(0)
        print("✓ Merged program counts")
    
    # Identify and mark outliers
    outliers = ['DIA', 'CBD', 'Civic Center', 'Union Station', 'Auraria']
    df['is_residential'] = ~df['neighborhood'].isin(outliers)
    
    print(f"Total neighborhoods: {len(df)}")
    print(f"Residential neighborhoods: {df['is_residential'].sum()}")
    
    return df

def create_main_story_visualization(df):
    """Create the main visualization that tells your story."""
    
    # Filter to residential neighborhoods
    df_res = df[df['is_residential']].copy()
    
    # Calculate correlation
    correlation = df_res['crime_per1000'].corr(df_res['program_count_per1000'])
    
    # Create figure
    fig = go.Figure()
    
    # Add main scatter plot
    fig.add_trace(go.Scatter(
        x=df_res['program_count_per1000'],
        y=df_res['crime_per1000'],
        mode='markers',
        marker=dict(
            size=15,
            color=df_res['avgOverallEquityScore'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(
                title="Equity<br>Score",
                tickmode="linear",
                tick0=1,
                dtick=1
            ),
            line=dict(color='white', width=1)
        ),
        text=df_res['neighborhood'],
        hovertemplate='<b>%{text}</b><br>' +
                      'Programs per 1000: %{x:.1f}<br>' +
                      'Crime per 1000: %{y:.1f}<br>' +
                      '<extra></extra>'
    ))
    
    # Add trend line
    z = np.polyfit(df_res['program_count_per1000'], df_res['crime_per1000'], 1)
    p = np.poly1d(z)
    x_trend = np.linspace(0, df_res['program_count_per1000'].max(), 100)
    
    fig.add_trace(go.Scatter(
        x=x_trend,
        y=p(x_trend),
        mode='lines',
        line=dict(color='red', dash='dash', width=2),
        name='Trend Line',
        showlegend=False
    ))
    
    # Add key insight annotation
    fig.add_annotation(
        text=f'<b>Key Finding</b><br>Correlation: r = {correlation:.3f}<br>' +
             'Weak positive correlation suggests<br>programs deployed in response to crime',
        xref="paper", yref="paper",
        x=0.95, y=0.95,
        showarrow=False,
        bgcolor="rgba(255, 255, 255, 0.8)",
        bordercolor="red",
        borderwidth=2,
        font=dict(size=12)
    )
    
    # Update layout
    fig.update_layout(
        title="The Surprising Truth: More Programs Don't Mean Less Crime<br>" +
              "<sub>After-school programs appear to be deployed reactively in high-crime areas</sub>",
        xaxis_title="After-School Programs per 1000 Residents",
        yaxis_title="Crime Rate per 1000 Residents",
        height=600,
        template="plotly_white"
    )
    
    return fig

def create_neighborhood_comparison(df):
    """Create a clear comparison of different neighborhood types."""
    
    df_res = df[df['is_residential']].copy()
    
    # Categorize neighborhoods
    df_res['category'] = 'Other'
    
    # High crime, low programs
    df_res.loc[
        (df_res['crime_per1000'] > df_res['crime_per1000'].quantile(0.75)) & 
        (df_res['program_count_per1000'] < df_res['program_count_per1000'].quantile(0.25)),
        'category'
    ] = 'High Risk\n(High Crime, Low Programs)'
    
    # Low crime, high programs
    df_res.loc[
        (df_res['crime_per1000'] < df_res['crime_per1000'].quantile(0.25)) & 
        (df_res['program_count_per1000'] > df_res['program_count_per1000'].quantile(0.75)),
        'category'
    ] = 'Model\n(Low Crime, High Programs)'
    
    # Create scatter plot with categories
    fig = px.scatter(
        df_res,
        x='program_count_per1000',
        y='crime_per1000',
        color='category',
        size='Percent Living in Poverty',
        hover_data=['neighborhood', 'avgOverallEquityScore'],
        color_discrete_map={
            'High Risk\n(High Crime, Low Programs)': COLORS['danger'],
            'Model\n(Low Crime, High Programs)': COLORS['success'],
            'Other': 'lightgray'
        },
        title="Identifying Priority Neighborhoods for Intervention<br>" +
              "<sub>Bubble size represents poverty level</sub>"
    )
    
    # Add quadrant lines
    fig.add_hline(y=df_res['crime_per1000'].median(), 
                  line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=df_res['program_count_per1000'].median(), 
                  line_dash="dash", line_color="gray", opacity=0.5)
    
    # Update layout
    fig.update_layout(
        xaxis_title="After-School Programs per 1000 Residents",
        yaxis_title="Crime Rate per 1000 Residents",
        height=600,
        template="plotly_white"
    )
    
    return fig

def create_intervention_priority_chart(df):
    """Create a clear chart showing which neighborhoods need help most."""
    
    df_res = df[df['is_residential']].copy()
    
    # Calculate intervention priority score
    # High crime + Low programs + High poverty = High priority
    df_res['intervention_score'] = (
        (df_res['crime_per1000'] / df_res['crime_per1000'].max()) * 0.4 +
        (1 - df_res['program_count_per1000'] / df_res['program_count_per1000'].max()) * 0.3 +
        (df_res['Percent Living in Poverty'] / 100) * 0.3
    )
    
    # Get top 15 priority neighborhoods
    priority = df_res.nlargest(15, 'intervention_score')
    
    # Create horizontal bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=priority['neighborhood'],
        x=priority['intervention_score'],
        orientation='h',
        marker=dict(
            color=priority['intervention_score'],
            colorscale='Reds',
            line=dict(color='darkred', width=1)
        ),
        text=[f"Crime: {c:.0f} | Programs: {p:.1f} | Poverty: {pov:.1f}%" 
              for c, p, pov in zip(priority['crime_per1000'], 
                                  priority['program_count_per1000'],
                                  priority['Percent Living in Poverty'])],
        textposition='inside',
        textfont=dict(color='white', size=10),
        hovertemplate='<b>%{y}</b><br>' +
                      'Priority Score: %{x:.2f}<br>' +
                      '%{text}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Neighborhoods Requiring Immediate Intervention<br>" +
              "<sub>Based on crime rate, program availability, and poverty level</sub>",
        xaxis_title="Intervention Priority Score",
        yaxis_title="",
        height=700,
        template="plotly_white",
        margin=dict(l=150)
    )
    
    return fig

def create_success_stories_chart(df):
    """Highlight successful neighborhoods to learn from."""
    
    df_res = df[df['is_residential']].copy()
    
    # Find successful neighborhoods
    success = df_res[
        (df_res['crime_per1000'] < df_res['crime_per1000'].quantile(0.25)) & 
        (df_res['avgOverallEquityScore'] > 4)
    ].nsmallest(10, 'crime_per1000')
    
    # Create radar chart comparing key metrics
    categories = ['Low Crime*', 'Programs', 'Equity', 'Income', 'Education']
    
    fig = go.Figure()
    
    # Add top 5 success stories
    for idx, (_, row) in enumerate(success.head(5).iterrows()):
        values = [
            100 - (row['crime_per1000'] / df_res['crime_per1000'].max() * 100),  # Invert crime
            row['program_count_per1000'] / df_res['program_count_per1000'].max() * 100,
            row['avgOverallEquityScore'] / 5 * 100,
            row['Median Household Income'] / df_res['Median Household Income'].max() * 100,
            row['percent_bachelors']
        ]
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=row['neighborhood'],
            line=dict(width=2),
            opacity=0.7
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                ticksuffix="%"
            )
        ),
        title="What Makes a Safe Neighborhood? Learning from Success Stories<br>" +
              "<sub>*Crime rate inverted - higher is better</sub>",
        height=600,
        template="plotly_white"
    )
    
    return fig

def create_demographic_insights(df):
    """Show how demographics relate to crime."""
    
    df_res = df[df['is_residential']].copy()
    
    # Create subplot figure
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Poverty and Crime',
            'Education and Crime',
            'Equity Score Distribution',
            'Program Distribution by Crime Level'
        ),
        specs=[[{"type": "scatter"}, {"type": "scatter"}],
               [{"type": "box"}, {"type": "box"}]]
    )
    
    # 1. Poverty vs Crime
    fig.add_trace(
        go.Scatter(
            x=df_res['Percent Living in Poverty'],
            y=df_res['crime_per1000'],
            mode='markers',
            marker=dict(
                size=10,
                color=COLORS['danger'],
                opacity=0.6
            ),
            text=df_res['neighborhood'],
            hovertemplate='%{text}<br>Poverty: %{x:.1f}%<br>Crime: %{y:.0f}<extra></extra>',
            showlegend=False
        ),
        row=1, col=1
    )
    
    # 2. Education vs Crime
    fig.add_trace(
        go.Scatter(
            x=df_res['percent_bachelors'],
            y=df_res['crime_per1000'],
            mode='markers',
            marker=dict(
                size=10,
                color=COLORS['info'],
                opacity=0.6
            ),
            text=df_res['neighborhood'],
            hovertemplate='%{text}<br>Bachelor\'s: %{x:.1f}%<br>Crime: %{y:.0f}<extra></extra>',
            showlegend=False
        ),
        row=1, col=2
    )
    
    # 3. Equity scores by crime level
    df_res['crime_level'] = pd.qcut(df_res['crime_per1000'], 
                                    q=3, 
                                    labels=['Low Crime', 'Medium Crime', 'High Crime'])
    
    for level in ['Low Crime', 'Medium Crime', 'High Crime']:
        data = df_res[df_res['crime_level'] == level]['avgOverallEquityScore']
        fig.add_trace(
            go.Box(
                y=data,
                name=level,
                showlegend=False
            ),
            row=2, col=1
        )
    
    # 4. Programs by crime level
    for level in ['Low Crime', 'Medium Crime', 'High Crime']:
        data = df_res[df_res['crime_level'] == level]['program_count_per1000']
        fig.add_trace(
            go.Box(
                y=data,
                name=level,
                showlegend=False
            ),
            row=2, col=2
        )
    
    # Update axes
    fig.update_xaxes(title_text="Percent Living in Poverty", row=1, col=1)
    fig.update_yaxes(title_text="Crime per 1000", row=1, col=1)
    
    fig.update_xaxes(title_text="Percent with Bachelor's Degree", row=1, col=2)
    fig.update_yaxes(title_text="Crime per 1000", row=1, col=2)
    
    fig.update_yaxes(title_text="Equity Score", row=2, col=1)
    fig.update_yaxes(title_text="Programs per 1000", row=2, col=2)
    
    fig.update_layout(
        height=800,
        title_text="Demographic Factors and Their Relationship to Crime",
        template="plotly_white"
    )
    
    return fig

def create_presentation_summary(df):
    """Create a single, powerful visualization for presentation."""
    
    df_res = df[df['is_residential']].copy()
    
    # Create figure with key insights
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'The Surprising Finding',
            'The Real Driver',
            'Where to Act Now',
            'What Success Looks Like'
        ),
        specs=[[{"type": "scatter"}, {"type": "scatter"}],
               [{"type": "bar"}, {"type": "bar"}]],
        vertical_spacing=0.15,
        horizontal_spacing=0.12
    )
    
    # 1. Main finding - weak correlation
    corr = df_res['crime_per1000'].corr(df_res['program_count_per1000'])
    
    fig.add_trace(
        go.Scatter(
            x=df_res['program_count_per1000'],
            y=df_res['crime_per1000'],
            mode='markers',
            marker=dict(size=12, color=COLORS['primary'], opacity=0.6),
            showlegend=False
        ),
        row=1, col=1
    )
    
    # Add correlation text
    fig.add_annotation(
        text=f'<b>r = {corr:.3f}</b>',
        xref="x", yref="y",
        x=df_res['program_count_per1000'].max() * 0.8,
        y=df_res['crime_per1000'].max() * 0.9,
        showarrow=False,
        bgcolor="yellow",
        font=dict(size=20),
        row=1, col=1
    )
    
    # 2. Poverty correlation
    poverty_corr = df_res['crime_per1000'].corr(df_res['Percent Living in Poverty'])
    
    fig.add_trace(
        go.Scatter(
            x=df_res['Percent Living in Poverty'],
            y=df_res['crime_per1000'],
            mode='markers',
            marker=dict(size=12, color=COLORS['danger'], opacity=0.6),
            showlegend=False
        ),
        row=1, col=2
    )
    
    fig.add_annotation(
        text=f'<b>r = {poverty_corr:.3f}</b>',
        xref="x2", yref="y2",
        x=df_res['Percent Living in Poverty'].max() * 0.8,
        y=df_res['crime_per1000'].max() * 0.9,
        showarrow=False,
        bgcolor="lightcoral",
        font=dict(size=20, color='white'),
        row=1, col=2
    )
    
    # 3. Top intervention priorities
    df_res['priority'] = (df_res['crime_per1000'] > df_res['crime_per1000'].quantile(0.7)) & \
                        (df_res['program_count_per1000'] < df_res['program_count_per1000'].quantile(0.3))
    
    priorities = df_res[df_res['priority']].nlargest(5, 'crime_per1000')
    
    fig.add_trace(
        go.Bar(
            y=priorities['neighborhood'],
            x=priorities['crime_per1000'],
            orientation='h',
            marker=dict(color=COLORS['warning']),
            showlegend=False
        ),
        row=2, col=1
    )
    
    # 4. Success metrics
    success = df_res.nsmallest(5, 'crime_per1000')
    
    fig.add_trace(
        go.Bar(
            y=success['neighborhood'],
            x=success['crime_per1000'],
            orientation='h',
            marker=dict(color=COLORS['success']),
            showlegend=False
        ),
        row=2, col=2
    )
    
    # Update axes
    fig.update_xaxes(title_text="Programs per 1000", row=1, col=1)
    fig.update_yaxes(title_text="Crime per 1000", row=1, col=1)
    
    fig.update_xaxes(title_text="Poverty %", row=1, col=2)
    fig.update_yaxes(title_text="Crime per 1000", row=1, col=2)
    
    fig.update_xaxes(title_text="Crime per 1000", row=2, col=1)
    fig.update_xaxes(title_text="Crime per 1000", row=2, col=2)
    
    fig.update_layout(
        height=800,
        title_text="Denver Crime Analysis: Key Insights at a Glance",
        template="plotly_white"
    )
    
    return fig

def save_key_statistics(df):
    """Save key statistics for the presentation."""
    
    df_res = df[df['is_residential']].copy()
    
    stats = {
        'Statistic': [
            'Crime-Program Correlation',
            'Crime-Poverty Correlation',
            'Crime-Education Correlation',
            'Average Crime Rate (per 1000)',
            'Average Programs (per 1000)',
            'High Risk Neighborhoods',
            'Model Neighborhoods'
        ],
        'Value': [
            f"{df_res['crime_per1000'].corr(df_res['program_count_per1000']):.3f}",
            f"{df_res['crime_per1000'].corr(df_res['Percent Living in Poverty']):.3f}",
            f"{df_res['crime_per1000'].corr(df_res['percent_bachelors']):.3f}",
            f"{df_res['crime_per1000'].mean():.1f}",
            f"{df_res['program_count_per1000'].mean():.1f}",
            f"{len(df_res[(df_res['crime_per1000'] > df_res['crime_per1000'].quantile(0.75)) & (df_res['program_count_per1000'] < df_res['program_count_per1000'].quantile(0.25))])}",
            f"{len(df_res[(df_res['crime_per1000'] < df_res['crime_per1000'].quantile(0.25)) & (df_res['avgOverallEquityScore'] > 4)])}"
        ],
        'Interpretation': [
            'Weak positive - programs deployed reactively',
            'Stronger relationship than programs',
            'Weak negative - education helps slightly',
            'Baseline for comparison',
            'Current distribution',
            'Need immediate intervention',
            'Learn from these successes'
        ]
    }
    
    stats_df = pd.DataFrame(stats)
    stats_df.to_csv('denver_visualization_key_stats.csv', index=False)
    print("✓ Saved key statistics to denver_visualization_key_stats.csv")

def main():
    """Main function to create all visualizations."""
    print("=" * 60)
    print("Denver Crime Data Visualization")
    print("Creating clear, impactful visualizations")
    print("=" * 60)
    
    # Load data
    data = load_count_data()
    if not data or 'crime' not in data:
        print("Error: Could not load required data files.")
        return
    
    # Prepare data
    df = prepare_visualization_data(data)
    
    # Create visualizations
    print("\nCreating visualizations...")
    
    # 1. Main story
    fig1 = create_main_story_visualization(df)
    fig1.write_html('denver_viz_main_story.html')
    print("✓ Created main story visualization")
    
    # 2. Neighborhood comparison
    fig2 = create_neighborhood_comparison(df)
    fig2.write_html('denver_viz_neighborhood_comparison.html')
    print("✓ Created neighborhood comparison")
    
    # 3. Intervention priorities
    fig3 = create_intervention_priority_chart(df)
    fig3.write_html('denver_viz_intervention_priorities.html')
    print("✓ Created intervention priority chart")
    
    # 4. Success stories
    fig4 = create_success_stories_chart(df)
    fig4.write_html('denver_viz_success_stories.html')
    print("✓ Created success stories chart")
    
    # 5. Demographic insights
    fig5 = create_demographic_insights(df)
    fig5.write_html('denver_viz_demographic_insights.html')
    print("✓ Created demographic insights")
    
    # 6. Presentation summary
    fig6 = create_presentation_summary(df)
    fig6.write_html('denver_viz_presentation_summary.html')
    print("✓ Created presentation summary")
    
    # Save key statistics
    save_key_statistics(df)
    
    print("\n" + "=" * 60)
    print("VISUALIZATION COMPLETE!")
    print("=" * 60)
    print("\nGenerated files:")
    print("1. denver_viz_main_story.html - Your key finding")
    print("2. denver_viz_neighborhood_comparison.html - Identifying different types")
    print("3. denver_viz_intervention_priorities.html - Where to act")
    print("4. denver_viz_success_stories.html - What works")
    print("5. denver_viz_demographic_insights.html - Contributing factors")
    print("6. denver_viz_presentation_summary.html - All key points in one view")
    print("7. denver_visualization_key_stats.csv - Statistics for your presentation")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()




