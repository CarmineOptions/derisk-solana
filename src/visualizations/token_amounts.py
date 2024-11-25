import pandas
import plotly.graph_objs


def get_bar_chart_figures(
        deposit_stats: pandas.DataFrame, debt_stats: pandas.DataFrame
) -> tuple[plotly.graph_objs.Figure, plotly.graph_objs.Figure]:
    deposit_figure = plotly.graph_objs.Figure(
        data = [
            plotly.graph_objs.Bar(
                name = protocol_name,
                x = deposit_stats.index, 
                y = deposit_stats[protocol_name],
                marker = plotly.graph_objs.bar.Marker(color=color),
            ) for protocol_name, color in [
                ('Kamino', '#19D3F3'), ('Solend', 'red'), ('Mango', 'orange'), ('MarginFi', '#BCBD22')
            ] if protocol_name in deposit_stats
        ],
    )
    deposit_figure.update_layout(title_text = 'Deposits (USD) per token')
    debt_figure = plotly.graph_objs.Figure(
        data = [
            plotly.graph_objs.Bar(
                name=protocol_name,
                x=debt_stats.index,
                y=debt_stats[protocol_name],
                marker=plotly.graph_objs.bar.Marker(color=color),
            ) for protocol_name, color in [
                ('Kamino', '#19D3F3'), ('Solend', 'red'), ('Mango', 'orange'), ('MarginFi', '#BCBD22')
            ] if protocol_name in debt_stats
        ],
    )
    debt_figure.update_layout(title_text = 'Debt (USD) per token')
    return deposit_figure, debt_figure
