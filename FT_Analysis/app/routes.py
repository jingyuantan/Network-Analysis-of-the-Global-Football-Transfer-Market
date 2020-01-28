from flask import Flask, render_template, request
import plotly
import plotly.graph_objs as go
import networkx as nx
from webweb import Web
from flask_table import Table, Col
from app import db
from app.models import Player, League, Club, Transfer
import pandas as pd
import numpy as np
import json
from sqlalchemy import func
from app import app


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/explore/')
def explore():
    leagueid = 'premier-leaguetransferswettbewerbGB1'
    country = 'all'
    bar = create_plot(leagueid, country)
    table1 = create_table1()
    leagues = League.query.all()
    league_lists = []
    country_list = []

    for league in leagues:
        temp = dict()
        temp.update({'id': league.id})
        temp.update({'name': league.name})
        country_list.append(league.country)
        league_lists.append(temp)

    country_list = list(dict.fromkeys(country_list))
    return render_template('explore.html', plot=bar, leagues=league_lists, countries=country_list, table1=table1)


def create_table1():
    # Declare your table
    class ItemTable(Table):
        name = Col('Club Name')
        country = Col('Country of Origin')

    # Or, equivalently, some dicts
    """items = [dict(name='Name1', description='Description1'),
             dict(name='Name2', description='Description2'),
             dict(name='Name3', description='Description3')]"""
    # Or, more likely, load items from your database with something like
    test = Club.query.filter_by(leagueId='premier-leaguetransferswettbewerbGB1')
    transfers = Transfer.query.all()
    main_list = pd.DataFrame()
    test = db.session.query(Transfer.fromId, func.count(Transfer.fromId)).group_by(Transfer.fromId).all()
    print(test[1][1])

    for transfer in transfers:
        clubFrom = Club.query.filter_by(id=transfer.fromId).first()
        clubTo = Club.query.filter_by(id=transfer.toId).first()
        value = transfer.value

    # Populate the table
    table = ItemTable(items)
    return table


def create_plot(leagueid, country):
    G = nx.Graph()
    transfers = Transfer.query.all()
    pair_clubs = []

    for transfer in transfers:
        clubFrom = Club.query.filter_by(id=transfer.fromId).first()
        clubTo = Club.query.filter_by(id=transfer.toId).first()
        value = transfer.value
        country_from = clubFrom.country
        country_to = clubTo.country

        if leagueid != 'all':
            if clubFrom.leagueId != leagueid or clubTo.leagueId != leagueid:
                continue

        if country != 'all':
            if country_from != country or country_to != country:
                continue

        if value[-1] == 'k':
            value = float(value[1:-1]) / 1000
        else:
            value = float(value[1:-1])

        pair = [clubFrom.name, clubTo.name, value]
        pair_clubs.append(pair)

    if pair_clubs:
        df = pd.DataFrame(pair_clubs, columns=['From', 'To', 'Value'])

    else:
        data = {'From': ['Invalid Filter'],
                'To': ['Invalid Filter'],
                'Value': [500]
                }

        df = pd.DataFrame(data, columns=['From', 'To', 'Value'])

    df["Occ"] = df.groupby(['From', 'To']).cumcount() + 1
    df['Total_Value'] = df.groupby(['From', 'To'])['Value'].cumsum()
    df = df.sort_values(by=['Total_Value'])

    for i in range(len(df)):
        f = df["From"][i]
        t = df["To"][i]
        p = df["Total_Value"][i]

        G.add_weighted_edges_from([(f, t, p)])

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
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])

    # add color to node points
    for node, adjacencies in enumerate(G.adjacency()):
        node_trace['marker']['color'] += tuple([len(adjacencies[1])])
        node_info = 'Name: ' + str(adjacencies[0]) + '<br># of connections: ' + str(len(adjacencies[1]))
        node_trace['text'] += tuple([node_info])

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
    league = request.args['league']
    country = request.args['country']
    graphJSON = create_plot(league, country)

    return graphJSON
