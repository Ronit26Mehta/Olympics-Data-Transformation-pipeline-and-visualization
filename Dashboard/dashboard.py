import dash
from dash import dcc, html
import plotly.express as px
import pickle

# Load analytics results
with open("analytics_results.pkl", "rb") as f:
    analytics_results = pickle.load(f)

# Dash App and Visualization
app = dash.Dash(__name__)

# Plot 1: Total Medals by Country
fig1 = px.bar(
    analytics_results["medal_count"],
    x="Country",
    y="Total_Medals",
    color="Year",
    title="Total Medals by Country",
    color_discrete_sequence=px.colors.qualitative.Set1,
    text="Total_Medals"
)
fig1.update_layout(showlegend=False, template="plotly_white", title_x=0.5)

# Plot 2: Average Age Distribution by Sport
fig2 = px.bar(
    analytics_results["avg_age_by_sport"],
    x="Sport",
    y="Average_Age",
    title="Average Age by Sport",
    color="Sport",
    color_discrete_sequence=px.colors.qualitative.Pastel
)
fig2.update_layout(showlegend=False, template="plotly_white", title_x=0.5)

# Plot 3: Medal Distribution by Type
fig3 = px.pie(
    analytics_results["medal_distribution"],
    names="Medal",
    values="Count",
    title="Medal Distribution by Type",
    color_discrete_sequence=px.colors.qualitative.Safe
)
fig3.update_traces(textinfo="percent+label")
fig3.update_layout(template="plotly_white", title_x=0.5)

# Plot 4: Top Countries with Most Medals (Filter top 10)
top_countries = analytics_results["medal_count"].groupby("Country").sum() \
    .sort_values("Total_Medals", ascending=False).head(10).reset_index()
fig4 = px.bar(
    top_countries,
    x="Country",
    y="Total_Medals",
    title="Top 10 Countries by Total Medals",
    color="Country",
    text="Total_Medals",
    color_discrete_sequence=px.colors.qualitative.Dark24
)
fig4.update_layout(showlegend=False, template="plotly_white", title_x=0.5)

# Plot 5: Medal Trends over Years
fig5 = px.line(
    analytics_results["medal_count"],
    x="Year",
    y="Total_Medals",
    color="Country",
    title="Medal Trends Over Years",
    markers=True,
    line_shape="spline"
)
fig5.update_layout(template="plotly_white", title_x=0.5)

# Plot 6: Average Medals per Country (New Plot)
avg_medals = analytics_results["medal_count"].groupby("Country").mean().reset_index()
fig6 = px.bar(
    avg_medals,
    x="Country",
    y="Total_Medals",
    title="Average Medals per Country",
    color="Country",
    text="Total_Medals",
    color_discrete_sequence=px.colors.qualitative.Vivid
)
fig6.update_layout(showlegend=False, template="plotly_white", title_x=0.5)

# Plot 7: Medal Distribution by Country (New Plot)
fig7 = px.sunburst(
    analytics_results["medal_count"],
    path=["Year", "Country"],
    values="Total_Medals",
    title="Medal Distribution by Country and Year",
    color="Total_Medals",
    color_continuous_scale="Viridis"
)
fig7.update_layout(template="plotly_white", title_x=0.5)

# Layout of the Dashboard
app.layout = html.Div(
    children=[
        html.H1(
            "Olympics Big Data Dashboard",
            style={"textAlign": "center", "marginBottom": "30px", "fontFamily": "Arial"}
        ),
        html.Div(
            children=[
                html.Div(
                    dcc.Graph(id="total-medals-by-country", figure=fig1),
                    style={"flex": "1", "padding": "10px"}
                ),
                html.Div(
                    dcc.Graph(id="average-age-by-sport", figure=fig2),
                    style={"flex": "1", "padding": "10px"}
                ),
            ],
            style={"display": "flex", "flex-wrap": "wrap"}
        ),
        html.Div(
            children=[
                html.Div(
                    dcc.Graph(id="medal-distribution", figure=fig3),
                    style={"flex": "1", "padding": "10px"}
                ),
                html.Div(
                    dcc.Graph(id="top-countries", figure=fig4),
                    style={"flex": "1", "padding": "10px"}
                ),
            ],
            style={"display": "flex", "flex-wrap": "wrap"}
        ),
        html.Div(
            children=[
                html.Div(
                    dcc.Graph(id="medal-trends", figure=fig5),
                    style={"flex": "1", "padding": "10px"}
                ),
                html.Div(
                    dcc.Graph(id="average-medals", figure=fig6),
                    style={"flex": "1", "padding": "10px"}
                ),
            ],
            style={"display": "flex", "flex-wrap": "wrap"}
        ),
        html.Div(
            dcc.Graph(id="medal-distribution-by-country", figure=fig7),
            style={"padding": "10px"}
        ),
    ],
    style={"fontFamily": "Arial"}
)

# Run the Dash app
if __name__ == "__main__":
    app.run_server(debug=True)
