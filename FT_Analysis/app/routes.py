from datetime import datetime
from flask import Flask, render_template, request
import plotly
import plotly.graph_objs as go
import networkx as nx
from flask_table import Table, Col
from app.models import Player, League, Club, Transfer
import pandas as pd
import json
from app import app, cache
from flask_caching import Cache
from sqlalchemy import or_, and_


@app.route('/')
@app.route('/index')
@cache.cached(timeout=50)
def index():
    return render_template('index.html')

@app.route('/explore/')
@cache.cached(timeout=50)
def explore():
    season = 'all'
    leagueid = 'premier-leaguetransferswettbewerbGB1'
    country = 'all'
    position = 'all'
    nationality = 'all'
    ageFrom = ''
    ageTo = ''
    valueFrom = ''
    valueTo = ''
    dateFrom = ''
    dateTo = ''

    league_lists = []
    country_list = []
    season_list = []
    position_list = []
    nationality_list = []

    leagues = League.query.all()
    for league in leagues:
        temp = dict()
        temp.update({'id': league.id})
        temp.update({'name': league.name})
        country_list.append(league.country)
        league_lists.append(temp)

    transfers = Transfer.query.all()
    for transfer in transfers:
        season_list.append(transfer.season)

    players = Player.query.all()
    for player in players:
        position_list.append(player.position)
        nationality_list.append(player.nationality)

    country_list = list(dict.fromkeys(country_list))
    season_list = list(dict.fromkeys(season_list))
    position_list = list(dict.fromkeys(position_list))
    nationality_list = list(dict.fromkeys(nationality_list))

    bar = create_plot(season, leagueid, country, position, nationality, ageFrom, ageTo, valueFrom, valueTo,
                      dateFrom, dateTo)
    table1 = create_table1()

    return render_template('explore.html', plot=bar, seasons=season_list, leagues=league_lists, countries=country_list,
                           positions=position_list, nationalities=nationality_list, table1=table1)


@cache.memoize(50)
def create_plot(season, leagueid, country, position, nationality, ageFrom, ageTo, valueFrom, valueTo, dateFrom, dateTo):
    transfers = Transfer.query.all()
    pair_clubs = []
    s17_18 = []
    s18_19 = []
    s19_20 = []

    for transfer in transfers:
        clubFrom = Club.query.filter_by(id=transfer.fromId).first()
        clubTo = Club.query.filter_by(id=transfer.toId).first()
        value = transfer.value
        country_from = clubFrom.country
        country_to = clubTo.country
        player_position = Player.query.filter_by(id=transfer.playerId).first().position
        player_nationality = Player.query.filter_by(id=transfer.playerId).first().nationality
        player_age = Player.query.filter_by(id=transfer.playerId).first().age
        date = datetime.utcfromtimestamp(int(transfer.timestamp)).strftime('%Y-%m-%d')

        if leagueid != 'all':
            if clubFrom.leagueId != leagueid or clubTo.leagueId != leagueid:
                continue

        if country != 'all':
            if country_from != country or country_to != country:
                continue

        if position != 'all':
            if player_position != position:
                continue

        if nationality != 'all':
            if player_nationality != nationality:
                continue

        if ageFrom != '':
            if player_age < ageFrom:
                continue

        if ageTo != '':
            if player_age > ageTo:
                continue

        if value[-1] == 'k':
            value = float(value[1:-1]) / 1000
        else:
            value = float(value[1:-1])

        if valueFrom != '':
            if value < float(valueFrom):
                continue

        if valueTo != '':
            if value > float(valueTo):
                continue

        temp = [clubFrom.name, clubTo.name, value, transfer.fromId, transfer.toId]
        if transfer.season == '2017/2018':
            s17_18.append(temp)
        elif transfer.season == '2018/2019':
            s18_19.append(temp)
        elif transfer.season == '2019/2020':
            s19_20.append(temp)

        if dateFrom != '':
            if date < dateFrom:
                continue

        if dateTo != '':
            if date > dateTo:
                continue

        if season != 'all':
            if transfer.season != season:
                continue

        pair = [clubFrom.name, clubTo.name, value, transfer.fromId, transfer.toId]
        pair_clubs.append(pair)

    if pair_clubs:
        df = pd.DataFrame(pair_clubs, columns=['From', 'To', 'Value', 'From Id', 'To Id'])
    else:
        data = {'From': ['Invalid Filter'],
                'To': ['Invalid Filter'],
                'Value': [500],
                'From Id': '-',
                'To Id': '-'
                }
        df = pd.DataFrame(data, columns=['From', 'To', 'Value', 'From Id', 'To Id'])

    if s17_18:
        df17_18 = pd.DataFrame(s17_18, columns=['From', 'To', 'Value', 'From Id', 'To Id'])
    else:
        data = {'From': ['Invalid Filter'],
                'To': ['Invalid Filter'],
                'Value': [500],
                'From Id': '-',
                'To Id': '-'
                }
        df17_18 = pd.DataFrame(data, columns=['From', 'To', 'Value', 'From Id', 'To Id'])

    if s18_19:
        df18_19 = pd.DataFrame(s18_19, columns=['From', 'To', 'Value', 'From Id', 'To Id'])
    else:
        data = {'From': ['Invalid Filter'],
                'To': ['Invalid Filter'],
                'Value': [500],
                'From Id': '-',
                'To Id': '-'
                }
        df18_19 = pd.DataFrame(data, columns=['From', 'To', 'Value', 'From Id', 'To Id'])

    if s19_20:
        df19_20 = pd.DataFrame(s19_20, columns=['From', 'To', 'Value', 'From Id', 'To Id'])
    else:
        data = {'From': ['Invalid Filter'],
                'To': ['Invalid Filter'],
                'Value': [500],
                'From Id': '-',
                'To Id': '-'
                }
        df19_20 = pd.DataFrame(data, columns=['From', 'To', 'Value', 'From Id', 'To Id'])

    """df["Occ"] = df.groupby(['From', 'To']).cumcount() + 1
    df['Total_Value'] = df.groupby(['From', 'To'])['Value'].cumsum()
    df = df.sort_values(by=['Total_Value'])"""
    graphJSON = plot(df, df17_18, df18_19, df19_20)
    return graphJSON


@cache.memoize(50)
def create_plot_ego(clicked):
    transfers = Transfer.query.filter(or_(Transfer.fromId == clicked, Transfer.toId == clicked))
    pair_clubs = []
    alter_id = []
    s17_18 = []
    s18_19 = []
    s19_20 = []

    for transfer in transfers:
        if clicked == transfer.fromId:
            alter_id.append(transfer.toId)

        elif clicked == transfer.toId:
            alter_id.append(transfer.fromId)
        else:
            continue

        clubFrom = Club.query.filter_by(id=transfer.fromId).first()
        clubTo = Club.query.filter_by(id=transfer.toId).first()
        value = transfer.value
        country_from = clubFrom.country
        country_to = clubTo.country

        if value[-1] == 'k':
            value = float(value[1:-1]) / 1000
        else:
            value = float(value[1:-1])

        temp = [clubFrom.name, clubTo.name, value, transfer.fromId, transfer.toId]
        if transfer.season == '2017/2018':
            s17_18.append(temp)
        elif transfer.season == '2018/2019':
            s18_19.append(temp)
        elif transfer.season == '2019/2020':
            s19_20.append(temp)

        pair = [clubFrom.name, clubTo.name, value, transfer.fromId, transfer.toId]
        pair_clubs.append(pair)

    for i in range(len(alter_id)):
        alterAsFrom = Transfer.query.filter_by(fromId=alter_id[i])
        for a in alterAsFrom:
            if a.toId in alter_id:
                clubFrom = Club.query.filter_by(id=alter_id[i]).first()
                clubTo = Club.query.filter_by(id=a.toId).first()
                value = alterAsFrom.value
                temp = [clubFrom.name, clubTo.name, value, alter_id[i], a.toId]
                if transfer.season == '2017/2018':
                    s17_18.append(temp)
                elif transfer.season == '2018/2019':
                    s18_19.append(temp)
                elif transfer.season == '2019/2020':
                    s19_20.append(temp)
                pair = [clubFrom.name, clubTo.name, value, alter_id[i], a.toId]
                pair_clubs.append(pair)

        alterAsTo = Transfer.query.filter_by(toId=alter_id[i])
        for a in alterAsTo:
            if a.fromId in alter_id:
                clubFrom = Club.query.filter_by(id=a.fromId).first()
                clubTo = Club.query.filter_by(id=alter_id[i]).first()
                value = alterAsFrom.value
                temp = [clubFrom.name, clubTo.name, value, a.toId, alter_id[i]]
                if transfer.season == '2017/2018':
                    s17_18.append(temp)
                elif transfer.season == '2018/2019':
                    s18_19.append(temp)
                elif transfer.season == '2019/2020':
                    s19_20.append(temp)
                pair = [clubFrom.name, clubTo.name, value, a.toId, alter_id[i]]
                pair_clubs.append(pair)

    if pair_clubs:
        df = pd.DataFrame(pair_clubs, columns=['From', 'To', 'Value', 'From Id', 'To Id'])
    else:
        data = {'From': ['Invalid Filter'],
                'To': ['Invalid Filter'],
                'Value': [500],
                'From Id': '-',
                'To Id': '-'
                }
        df = pd.DataFrame(data, columns=['From', 'To', 'Value', 'From Id', 'To Id'])

    if s17_18:
        df17_18 = pd.DataFrame(s17_18, columns=['From', 'To', 'Value', 'From Id', 'To Id'])
    else:
        data = {'From': ['Invalid Filter'],
                'To': ['Invalid Filter'],
                'Value': [500],
                'From Id': '-',
                'To Id': '-'
                }
        df17_18 = pd.DataFrame(data, columns=['From', 'To', 'Value', 'From Id', 'To Id'])

    if s18_19:
        df18_19 = pd.DataFrame(s18_19, columns=['From', 'To', 'Value', 'From Id', 'To Id'])
    else:
        data = {'From': ['Invalid Filter'],
                'To': ['Invalid Filter'],
                'Value': [500],
                'From Id': '-',
                'To Id': '-'
                }
        df18_19 = pd.DataFrame(data, columns=['From', 'To', 'Value', 'From Id', 'To Id'])

    if s19_20:
        df19_20 = pd.DataFrame(s19_20, columns=['From', 'To', 'Value', 'From Id', 'To Id'])
    else:
        data = {'From': ['Invalid Filter'],
                'To': ['Invalid Filter'],
                'Value': [500],
                'From Id': '-',
                'To Id': '-'
                }
        df19_20 = pd.DataFrame(data, columns=['From', 'To', 'Value', 'From Id', 'To Id'])

        df = pd.DataFrame(data, columns=['From', 'To', 'Value', 'From Id', 'To Id'])

    """df["Occ"] = df.groupby(['From', 'To']).cumcount() + 1
    df['Total_Value'] = df.groupby(['From', 'To'])['Value'].cumsum()
    df = df.sort_values(by=['Total_Value'])"""
    graphJSON = plot(df, df17_18, df18_19, df19_20)
    return graphJSON


@cache.memoize(50)
def plot(df, df17_18, df18_19, df19_20):
    G = assign_nodes_edges(df)
    G17_18 = assign_nodes_edges(df17_18)
    G18_19 = assign_nodes_edges(df18_19)
    G19_20 = assign_nodes_edges(df19_20)

    # adjust node size according to degree, etc
    node_sizes = adjust_node_size(G)
    node_sizes_17_18 = adjust_node_size(G17_18)
    node_sizes_18_19 = adjust_node_size(G18_19)
    node_sizes_19_20 = adjust_node_size(G19_20)

    # get a x,y position for each node
    pos = nx.circular_layout(G)
    pos_17_18 = nx.circular_layout(G17_18)
    pos_18_19 = nx.circular_layout(G18_19)
    pos_19_20 = nx.circular_layout(G19_20)

    # add a pos attribute to each node
    for node in G.nodes:
        G.nodes[node]['pos'] = list(pos[node])

    for node in G17_18.nodes:
        G17_18.nodes[node]['pos'] = list(pos_17_18[node])

    for node in G18_19.nodes:
        G18_19.nodes[node]['pos'] = list(pos_18_19[node])

    for node in G19_20.nodes:
        G19_20.nodes[node]['pos'] = list(pos_19_20[node])

    pos = nx.get_node_attributes(G, 'pos')
    pos_17_18 = nx.get_node_attributes(G17_18, 'pos')
    pos_18_19 = nx.get_node_attributes(G18_19, 'pos')
    pos_19_20 = nx.get_node_attributes(G19_20, 'pos')

    """dmin = 1
    ncenter = 0
    for n in pos:
        x, y = pos[n]
        d = (x - 0.5) ** 2 + (y - 0.5) ** 2
        if d < dmin:
            ncenter = n
            dmin = d

    p = nx.single_source_shortest_path_length(G, ncenter)"""

    # Create Edges
    edge_trace = create_edge_scatter()
    edge_trace_17_18 = create_edge_scatter()
    edge_trace_18_19 = create_edge_scatter()
    edge_trace_19_20 = create_edge_scatter()

    for edge in G.edges():
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])

    for edge in G17_18.edges():
        x0, y0 = G17_18.nodes[edge[0]]['pos']
        x1, y1 = G17_18.nodes[edge[1]]['pos']
        edge_trace_17_18['x'] += tuple([x0, x1, None])
        edge_trace_17_18['y'] += tuple([y0, y1, None])

    for edge in G18_19.edges():
        x0, y0 = G18_19.nodes[edge[0]]['pos']
        x1, y1 = G18_19.nodes[edge[1]]['pos']
        edge_trace_18_19['x'] += tuple([x0, x1, None])
        edge_trace_18_19['y'] += tuple([y0, y1, None])

    for edge in G19_20.edges():
        x0, y0 = G19_20.nodes[edge[0]]['pos']
        x1, y1 = G19_20.nodes[edge[1]]['pos']
        edge_trace_19_20['x'] += tuple([x0, x1, None])
        edge_trace_19_20['y'] += tuple([y0, y1, None])

    node_trace = create_node_scatter(node_sizes)
    node_trace_17_18 = create_node_scatter(node_sizes_17_18)
    node_trace_18_19 = create_node_scatter(node_sizes_18_19)
    node_trace_19_20 = create_node_scatter(node_sizes_19_20)

    for node in G.nodes():
        x, y = G.nodes[node]['pos']
        clubId = G.nodes[node]['id']
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['text'] += tuple([clubId])

    for node in G17_18.nodes():
        x, y = G17_18.nodes[node]['pos']
        clubId = G17_18.nodes[node]['id']
        node_trace_17_18['x'] += tuple([x])
        node_trace_17_18['y'] += tuple([y])
        node_trace_17_18['text'] += tuple([clubId])

    for node in G18_19.nodes():
        x, y = G18_19.nodes[node]['pos']
        clubId = G18_19.nodes[node]['id']
        node_trace_18_19['x'] += tuple([x])
        node_trace_18_19['y'] += tuple([y])
        node_trace_18_19['text'] += tuple([clubId])

    for node in G19_20.nodes():
        x, y = G19_20.nodes[node]['pos']
        clubId = G19_20.nodes[node]['id']
        node_trace_19_20['x'] += tuple([x])
        node_trace_19_20['y'] += tuple([y])
        node_trace_19_20['text'] += tuple([clubId])

    # add color to node points
    for node, adjacencies in enumerate(G.adjacency()):
        node_trace['marker']['color'] += tuple([len(adjacencies[1])])
        node_info = 'Name: ' + str(adjacencies[0]) + '<br># of connections: ' + str(len(adjacencies[1]))
        # node_trace['text'] += tuple([node_info])
        node_trace['hovertext'] += tuple([node_info])

    for node, adjacencies in enumerate(G17_18.adjacency()):
        node_trace_17_18['marker']['color'] += tuple([len(adjacencies[1])])
        node_info = 'Name: ' + str(adjacencies[0]) + '<br># of connections: ' + str(len(adjacencies[1]))
        # node_trace['text'] += tuple([node_info])
        node_trace_17_18['hovertext'] += tuple([node_info])

    for node, adjacencies in enumerate(G18_19.adjacency()):
        node_trace_18_19['marker']['color'] += tuple([len(adjacencies[1])])
        node_info = 'Name: ' + str(adjacencies[0]) + '<br># of connections: ' + str(len(adjacencies[1]))
        # node_trace['text'] += tuple([node_info])
        node_trace_18_19['hovertext'] += tuple([node_info])

    for node, adjacencies in enumerate(G19_20.adjacency()):
        node_trace_19_20['marker']['color'] += tuple([len(adjacencies[1])])
        node_info = 'Name: ' + str(adjacencies[0]) + '<br># of connections: ' + str(len(adjacencies[1]))
        # node_trace['text'] += tuple([node_info])
        node_trace_19_20['hovertext'] += tuple([node_info])

    years = ["2017/2018", "2018/2019", "2019/2020"]
    for year in years:
        slider_step = {"args": [
            ["year"],
            {"frame": {"duration": 300, "redraw": False},
             "mode": "immediate",
             "transition": {"duration": 300}}
        ],
            "label": year,
            "method": "animate"}

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title='<br>Football Transfer Network',
                        titlefont=dict(size=16),
                        showlegend=False,
                        hovermode='closest',
                        width=1140,
                        height=700,
                        margin=dict(b=20, l=5, r=5, t=40),
                        updatemenus=[dict(
                            type="buttons",
                            buttons=[dict(label="Play",
                                          method="animate",
                                          args=[None, {"frame": {"duration": 3000, "redraw": False},
                                                       "fromcurrent": True,
                                                       "transition": {"duration": 1000, "easing": "quadratic-in-out"}}]),
                                     dict(label="Pause",
                                          method="animate",
                                          args=[[None], {"frame": {"duration": 0, "redraw": False},
                                                         "mode": "immediate",
                                                         "transition": {"duration": 0}}])
                                     ]
                            ,
                            direction="left",
                            pad={"r": 10, "t": 87},
                            showactive=False,
                            x=0.1,
                            xanchor="right",
                            y=0,
                            yanchor="top"
                        )],
                        annotations=[dict(showarrow=False,
                                          xref="paper", yref="paper",
                                          x=0.005, y=-0.002)
                                     ],
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)),
                    frames=[go.Frame(data=[edge_trace, node_trace], name="Start"),
                            go.Frame(data=[edge_trace_17_18, node_trace_17_18], name="2017/2018"),
                            go.Frame(data=[edge_trace_18_19, node_trace_18_19], name="2018/2019"),
                            go.Frame(data=[edge_trace_19_20, node_trace_19_20], name="2019/2020"),
                            go.Frame(data=[edge_trace, node_trace], name="End",
                                     layout=go.Layout(title_text="End Title"))]
                    )
    years = ["Start", "2017/2018", "2018/2019", "2019/2020", "End"]
    steps = []
    for year in years:
        step = dict(
            label=year,
            method="animate",
            args=[[year],
                  {"frame": {"duration": 300, "redraw": False},
                  "mode": "immediate", "transition": {"duration": 300}}
                  ],
        )
        steps.append(step)

    sliders = [dict(active=0,
                    yanchor="top",
                    xanchor="left",
                    currentvalue={
                        "font": {"size": 20},
                        "prefix": "Year:",
                        "visible": True,
                        "xanchor": "right"
                    },
                    transition={"duration": 300, "easing": "cubic-in-out"},
                    pad={"b": 10, "t": 50},
                    len=0.9,
                    x=0.1,
                    y=0,
                    steps=steps)
               ]
    fig.update_layout(
        sliders=sliders
    )
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def assign_nodes_edges(df):
    G = nx.Graph()
    for i in range(len(df)):
        f = df["From"][i]
        t = df["To"][i]
        # p = df["Total_Value"][i]
        G.add_node(f, id=df['From Id'][i])
        G.add_node(t, id=df['To Id'][i])
        G.add_edge(f, t)
        # G.add_weighted_edges_from([(f, t, p)])
    return G


def adjust_node_size(G):
    # adjust node size according to degree, etc
    d = nx.degree(G)
    node_sizes = []
    for i in d:
        _, value = i
        node_sizes.append(5 * value + 5)
    return node_sizes


def create_edge_scatter():
    edge_trace = go.Scatter(
        x=[],
        y=[],
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')
    return edge_trace


def create_node_scatter(node_sizes):
    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        hovertext=[],
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            # colorscale options
            # 'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            # 'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            # 'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale='Viridis',
            reversescale=True,
            color=[],
            size=node_sizes,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line=dict(width=2)))
    return node_trace



@app.route('/table')
@cache.memoize(50)
def create_table1():
    # Declare your table
    class ItemTable(Table):
        table_id = 'main_table'
        classes = ['table', 'table-bordered', 'table-striped']
        name = Col('Club Name')
        transfer_in = Col('Transfer In')
        transfer_out = Col('Transfer Out')
        total_transfer = Col('Total Transfer')
        spent = Col('Total transfer fee spent')
        received = Col('Total transfer fee received')
        net = Col('Net Spent')

    df = pd.DataFrame(columns=['name', 'transfer_in', 'transfer_out', 'total_transfer', 'spent', 'received', 'net'])
    df.set_index('name')
    transfers = Transfer.query.all()

    for transfer in transfers:
        clubFrom = Club.query.filter_by(id=transfer.fromId).first().name
        clubTo = Club.query.filter_by(id=transfer.toId).first().name
        value = transfer.value
        if value[-1] == 'k':
            value = float(value[1:-1]) / 1000
        else:
            value = float(value[1:-1])

        if clubFrom in df['name']:
            df['transfer_out'][clubFrom] += 1
            df['total_transfer'][clubFrom] += 1
            df['received'][clubFrom] += value
            df['net'][clubFrom] -= value
        else:
            df.loc[clubFrom] = [clubFrom, 0, 1, 1, 0, value, -value]

        if clubTo in df['name']:
            df['transfer_in'][clubTo] += 1
            df['total_transfer'][clubTo] += 1
            df['spent'][clubTo] += value
            df['net'][clubTo] += value
        else:
            df.loc[clubTo] = [clubTo, 1, 0, 1, value, 0, value]

    # Populate the table
    items = []

    for clubName in df['name']:
        spent = '&#163;' + str(float("{0:.2f}".format(df['spent'][clubName]))) + 'm'
        received = '&#163;' + str(float("{0:.2f}".format(df['received'][clubName]))) + 'm'
        net = '&#163;' + str(float("{0:.2f}".format(df['net'][clubName]))) + 'm'

        items.append(dict(name=df['name'][clubName], transfer_in=df['transfer_in'][clubName],
                          transfer_out=df['transfer_out'][clubName], total_transfer=df['total_transfer'][clubName],
                          spent=spent, received=received, net=net))

    table = ItemTable(items)
    return table


@app.route('/personalized_table',  methods=['GET', 'POST'])
def ego_table():
    clicked = request.args['clicked']
    df = pd.DataFrame(columns=['name', 'transfer_in', 'transfer_out', 'total_transfer', 'spent', 'received', 'net'])
    df.set_index('name')
    transfers = Transfer.query.filter(or_(Transfer.fromId == clicked, Transfer.toId == clicked))
    alter_id = []

    for transfer in transfers:
        if clicked == transfer.fromId:
            alter_id.append(transfer.toId)

        elif clicked == transfer.toId:
            alter_id.append(transfer.fromId)
        else:
            continue

        clubFrom = Club.query.filter_by(id=transfer.fromId).first().name
        clubTo = Club.query.filter_by(id=transfer.toId).first().name
        value = transfer.value
        if value[-1] == 'k':
            value = float(value[1:-1]) / 1000
        else:
            value = float(value[1:-1])

        if clubFrom in df['name']:
            df['transfer_out'][clubFrom] += 1
            df['total_transfer'][clubFrom] += 1
            df['received'][clubFrom] += value
            df['net'][clubFrom] -= value
        else:
            df.loc[clubFrom] = [clubFrom, 0, 1, 1, 0, value, -value]

        if clubTo in df['name']:
            df['transfer_in'][clubTo] += 1
            df['total_transfer'][clubTo] += 1
            df['spent'][clubTo] += value
            df['net'][clubTo] += value
        else:
            df.loc[clubTo] = [clubTo, 1, 0, 1, value, 0, value]

    # Populate the table
    items = []
    records = 0
    for clubName in df['name']:
        spent = '&#163;' + str(float("{0:.2f}".format(df['spent'][clubName]))) + 'm'
        received = '&#163;' + str(float("{0:.2f}".format(df['received'][clubName]))) + 'm'
        net = '&#163;' + str(float("{0:.2f}".format(df['net'][clubName]))) + 'm'

        items.append(dict(name=df['name'][clubName], transfer_in=df['transfer_in'][clubName],
                          transfer_out=df['transfer_out'][clubName], total_transfer=df['total_transfer'][clubName],
                          spent=spent, received=received, net=net))
        records += 1

    # proper_json = dict(draw=1, recordsTotal=records, recordsFiltered=records, data=items)
    proper_json = dict(data=items)
    return json.dumps(proper_json)


@app.route('/bar', methods=['GET', 'POST'])
def change_features():
    season = request.args['season']
    league = request.args['league']
    country = request.args['country']
    position = request.args['position']
    nationality = request.args['nationality']
    ageFrom = request.args['ageFrom']
    ageTo = request.args['ageTo']
    valueFrom = request.args['valueFrom']
    valueTo = request.args['valueTo']
    dateFrom = request.args['dateFrom']
    dateTo = request.args['dateTo']

    graphJSON = create_plot(season, league, country, position, nationality, ageFrom, ageTo, valueFrom, valueTo,
                            dateFrom, dateTo)
    return graphJSON


@app.route('/one', methods=['GET', 'POST'])
def change_features_ego():
    clicked = request.args['clicked']

    graphJSON = create_plot_ego(clicked)
    return graphJSON

