import pandas
import plotly.graph_objs



def get_bar_chart_figures(
	deposit_stats: pandas.DataFrame,
	debt_stats: pandas.DataFrame,
) -> tuple[plotly.graph_objs.Figure, plotly.graph_objs.Figure]:
    deposit_figure = plotly.graph_objs.Figure(
        data = [
            plotly.graph_objs.Bar(
                name = 'Kamino',
                x = deposit_stats.index,
                y = deposit_stats['Kamino'],
                marker = plotly.graph_objs.bar.Marker(color = '#19D3F3'),
            ),
            plotly.graph_objs.Bar(
                name = 'Solend',
                x = deposit_stats.index,
                y = deposit_stats['Solend'],
                marker = plotly.graph_objs.bar.Marker(color = 'red'),
            ),
            plotly.graph_objs.Bar(
                name = 'Mango', 
                x = deposit_stats.index, 
                y = deposit_stats['Mango'],
                marker = plotly.graph_objs.bar.Marker(color = 'orange'),
            ),
            plotly.graph_objs.Bar(
                name = 'MarginFi', 
                x = deposit_stats.index, 
                y = deposit_stats['MarginFi'],
                marker = plotly.graph_objs.bar.Marker(color = '#BCBD22'),
            ),
        ],
    )
    deposit_figure.update_layout(title_text = 'Deposits (USD) per token')
    debt_figure = plotly.graph_objs.Figure(
        data = [
            plotly.graph_objs.Bar(
                name = 'Kamino', 
                x = debt_stats.index, 
                y = debt_stats['Kamino'],
                marker = plotly.graph_objs.bar.Marker(color = '#19D3F3'),
            ),
            plotly.graph_objs.Bar(
                name = 'Solend', 
                x = debt_stats.index, 
                y = debt_stats['Solend'],
                marker = plotly.graph_objs.bar.Marker(color = 'red'),
            ),
            plotly.graph_objs.Bar(
                name = 'Mango', 
                x = debt_stats.index, 
                y = debt_stats['Mango'],
                marker = plotly.graph_objs.bar.Marker(color = 'orange'),
            ),
            plotly.graph_objs.Bar(
                name = 'MarginFi', 
                x = debt_stats.index, 
                y = debt_stats['MarginFi'],
                marker = plotly.graph_objs.bar.Marker(color = '#BCBD22'),
            ),
        ],
    )
    debt_figure.update_layout(title_text = 'Debt (USD) per token')
    return deposit_figure, debt_figure