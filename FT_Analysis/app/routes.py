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
    ageFrom = 'all'
    ageTo = 'all'
    valueFrom = 'all'
    valueTo = 'all'
    dateFrom = 'all'
    dateTo = 'all'

    bar = create_plot(season, leagueid, country, position, nationality, ageFrom, ageTo, valueFrom, valueTo,
                      dateFrom, dateTo)
    table1 = create_table1()

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

    return render_template('explore.html', plot=bar, seasons=season_list, leagues=league_lists, countries=country_list,
                           positions=position_list, nationalities=nationality_list, table1=table1)


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
        spent = '£' + str(float("{0:.2f}".format(df['spent'][clubName]))) + 'm'
        received = '£' + str(float("{0:.2f}".format(df['received'][clubName]))) + 'm'
        net = '£' + str(float("{0:.2f}".format(df['net'][clubName]))) + 'm'

        items.append(dict(name=df['name'][clubName], transfer_in=df['transfer_in'][clubName],
                          transfer_out=df['transfer_out'][clubName], total_transfer=df['total_transfer'][clubName],
                          spent=spent, received=received, net=net))

    table = ItemTable(items)
    return table


@cache.memoize(50)
def create_plot(season, leagueid, country, position, nationality, ageFrom, ageTo, valueFrom, valueTo, dateFrom, dateTo):
    transfers = Transfer.query.all()
    pair_clubs = []

    for transfer in transfers:
        clubFrom = Club.query.filter_by(id=transfer.fromId).first()
        clubTo = Club.query.filter_by(id=transfer.toId).first()
        value = transfer.value
        country_from = clubFrom.country
        country_to = clubTo.country
        player_position = Player.query.filter_by(id=transfer.playerId).first().position
        player_nationality = Player.query.filter_by(id=transfer.playerId).first().nationality

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

        if value[-1] == 'k':
            value = float(value[1:-1]) / 1000
        else:
            value = float(value[1:-1])

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

    df["Occ"] = df.groupby(['From', 'To']).cumcount() + 1
    df['Total_Value'] = df.groupby(['From', 'To'])['Value'].cumsum()
    df = df.sort_values(by=['Total_Value'])
    graphJSON = plot(df)
    return graphJSON


@cache.memoize(50)
def create_plot_one(clicked):
    transfers = Transfer.query.all()
    pair_clubs = []

    for transfer in transfers:
        if clicked != transfer.fromId and clicked != transfer.toId:
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

    df["Occ"] = df.groupby(['From', 'To']).cumcount() + 1
    df['Total_Value'] = df.groupby(['From', 'To'])['Value'].cumsum()
    df = df.sort_values(by=['Total_Value'])
    graphJSON = plot(df)
    return graphJSON


@cache.memoize(50)
def plot(df):
    G = nx.Graph()
    for i in range(len(df)):
        f = df["From"][i]
        t = df["To"][i]
        # p = df["Total_Value"][i]
        G.add_node(f, id=df['From Id'][i])
        G.add_node(t, id=df['To Id'][i])
        G.add_edge(f, t)
        # G.add_weighted_edges_from([(f, t, p)])

    # adjust node size according to degree, etc
    d = nx.degree(G)
    node_sizes = []
    for i in d:
        _, value = i
        node_sizes.append(5 * value + 5)

    # get a x,y position for each node
    pos = nx.circular_layout(G)

    # add a pos attribute to each node
    for node in G.nodes:
        G.nodes[node]['pos'] = list(pos[node])

    pos = nx.get_node_attributes(G, 'pos')

    dmin = 1
    ncenter = 0
    for n in pos:
        x, y = pos[n]
        d = (x - 0.5) ** 2 + (y - 0.5) ** 2
        if d < dmin:
            ncenter = n
            dmin = d

    p = nx.single_source_shortest_path_length(G, ncenter)

    # Create Edges
    edge_trace = go.Scatter(
        x=[],
        y=[],
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    for edge in G.edges():
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])

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

    for node in G.nodes():
        x, y = G.nodes[node]['pos']
        clubId = G.nodes[node]['id']
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['text'] += tuple([clubId])

    # add color to node points
    for node, adjacencies in enumerate(G.adjacency()):
        node_trace['marker']['color'] += tuple([len(adjacencies[1])])
        node_info = 'Name: ' + str(adjacencies[0]) + '<br># of connections: ' + str(len(adjacencies[1]))
        # node_trace['text'] += tuple([node_info])
        node_trace['hovertext'] += tuple([node_info])

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title='<br>Football Transfer Network',
                        titlefont=dict(size=16),
                        showlegend=False,
                        hovermode='closest',
                        width=1140,
                        height=700,
                        margin=dict(b=20, l=5, r=5, t=40),
                        annotations=[dict(
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002)],
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


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
def change_features_one():
    clicked = request.args['clicked']

    graphJSON = create_plot_one(clicked)
    return graphJSON
