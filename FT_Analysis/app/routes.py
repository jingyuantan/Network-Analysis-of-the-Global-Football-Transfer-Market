from datetime import datetime
from flask import render_template, request
import plotly
import plotly.graph_objs as go
import networkx as nx
from app.models import Player, League, Club, Transfer
import pandas as pd
import json
from app import app, cache
from sqlalchemy import or_, and_
from collections import Counter


@app.route('/')
@app.route('/index')
@cache.cached(timeout=50)
def index():
    # this function is to for the home page
    transfers = Transfer.query.all()
    dates = []
    unique_list = []

    # get all the transfer dates from database
    for transfer in transfers:
        dates.append(int(transfer.timestamp))

    # calculate the number of occurrence for every dates
    dates.sort()
    num_occurrence = Counter(dates).values()

    # create a list of dates for x axis for the graph
    for x in dates:
        dt_object = datetime.fromtimestamp(x).date()
        if dt_object not in unique_list:
            unique_list.append(dt_object)

    # create the graph
    fig = json.dumps(go.Figure(data=go.Scatter(x=unique_list, y=list(num_occurrence))), cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('index.html', plot=fig)


@app.route('/explore/')
@cache.cached(timeout=50)
def explore():
    # this function is for the 'explore - network by club' page
    # default filter parameters
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

    # declare lists for filter values for the filtering section
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

    # populate values into lists
    transfers = Transfer.query.all()
    for transfer in transfers:
        season_list.append(transfer.season)

    players = Player.query.all()
    for player in players:
        position_list.append(player.position)
        nationality_list.append(player.nationality)

    # remove duplicates
    league_lists = sorted(league_lists, key=str)
    country_list = sorted(list(dict.fromkeys(country_list)), key=str)
    season_list = sorted(list(dict.fromkeys(season_list)), key=str)
    position_list = sorted(list(dict.fromkeys(position_list)), key=str)
    nationality_list = sorted(list(dict.fromkeys(nationality_list)), key=str)

    plots = create_plot('explore', season, leagueid, country, position, nationality, ageFrom, ageTo, valueFrom, valueTo,
                        dateFrom, dateTo)

    plot1 = plots[0]
    table1 = plots[1]

    return render_template('explore.html', plot=plot1, seasons=season_list, leagues=league_lists, countries=country_list,
                           positions=position_list, nationalities=nationality_list, table1=table1)


def create_plot(page, season, leagueid, country, position, nationality, ageFrom, ageTo, valueFrom, valueTo, dateFrom, dateTo):
    # this function is to retrieve relevant data from database based on the filter parameters,
    # and return graphs + tables for the page

    # declare a data frame with coulmn names initialized to store filtered data for table drawing
    df_table = pd.DataFrame(columns=['name', 'league', 'country', 'transfer_in', 'transfer_out', 'total_transfer',
                                     'spent', 'received', 'net', 'link'])

    # filtering process begins...
    transfers = Transfer.query
    if leagueid != 'all':
        transfers = transfers.filter(and_(Transfer.fromLeagueId == leagueid, Transfer.toLeagueId == leagueid))
    if country != 'all':
        transfers = transfers.filter(and_(Transfer.fromCountry == country, Transfer.toCountry == country))
    # position
    if position != 'all':
        transfers = transfers.join(Player).filter(Player.position == position)
    # nationality
    if nationality != 'all':
        if position != 'all':
            transfers = transfers.filter(Player.nationality == nationality)
        else:
            transfers = transfers.join(Player).filter(Player.nationality == nationality)

    # age
    if ageFrom != '':
        if position != 'all' or nationality != 'all':
            transfers = transfers.filter(Player.age >= ageFrom)
        else:
            transfers = transfers.join(Player).filter(Player.age >= ageFrom)

    if ageTo != '':
        if position != 'all' or nationality != 'all' or ageFrom != '':
            transfers = transfers.filter(Player.age <= ageTo)
        else:
            transfers = transfers.join(Player).filter(Player.age <= ageTo)

    pair_clubs = []
    s17_18 = []
    s18_19 = []
    s19_20 = []

    for transfer in transfers:
        clubFrom = Club.query.filter_by(id=transfer.fromId).first()
        clubTo = Club.query.filter_by(id=transfer.toId).first()
        value = transfer.value
        leagueFrom = League.query.filter_by(id=clubFrom.leagueId).first()
        leagueTo = League.query.filter_by(id=clubTo.leagueId).first()
        date = datetime.utcfromtimestamp(int(transfer.timestamp)).strftime('%Y-%m-%d')

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

        temp = [clubFrom.name, clubTo.name, transfer.fromId, transfer.toId]
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

        pair = [clubFrom.name, clubTo.name, transfer.fromId, transfer.toId]
        pair_clubs.append(pair)

        if clubFrom.name in df_table.values:
            df_table.loc[df_table.name == clubFrom.name, 'transfer_out'] += 1
            df_table.loc[df_table.name == clubFrom.name, 'total_transfer'] += 1
            df_table.loc[df_table.name == clubFrom.name, 'received'] += value
            df_table.loc[df_table.name == clubFrom.name, 'net'] -= value
        else:
            df_table.loc[clubFrom.name] = [clubFrom.name, leagueFrom.name, clubFrom.country, 0, 1, 1, 0, value, -value, clubFrom.id]

        if clubTo.name in df_table.values:
            df_table.loc[df_table.name == clubTo.name, 'transfer_in'] += 1
            df_table.loc[df_table.name == clubTo.name, 'total_transfer'] += 1
            df_table.loc[df_table.name == clubTo.name, 'spent'] += value
            df_table.loc[df_table.name == clubTo.name, 'net'] += value
        else:
            df_table.loc[clubTo.name] = [clubTo.name, leagueTo.name, clubTo.country, 1, 0, 1, value, 0, value, clubTo.id]
    # filtering process ends...

    # this part is to check if there's any empty data frame. A network cannot be plotted with empty data frame so if
    # there is any, we assign a dummy value to the data frame.
    if pair_clubs:
        df = pd.DataFrame(pair_clubs, columns=['From', 'To', 'From Id', 'To Id'])
    else:
        data = {'From': ['Invalid Filter'],
                'To': ['Invalid Filter'],
                'From Id': '-',
                'To Id': '-'
                }
        df = pd.DataFrame(data, columns=['From', 'To', 'From Id', 'To Id'])

    if s17_18:
        df17_18 = pd.DataFrame(s17_18, columns=['From', 'To', 'From Id', 'To Id'])
    else:
        data = {'From': ['Invalid Filter'],
                'To': ['Invalid Filter'],
                'From Id': '-',
                'To Id': '-'
                }
        df17_18 = pd.DataFrame(data, columns=['From', 'To', 'From Id', 'To Id'])

    if s18_19:
        df18_19 = pd.DataFrame(s18_19, columns=['From', 'To', 'From Id', 'To Id'])
    else:
        data = {'From': ['Invalid Filter'],
                'To': ['Invalid Filter'],
                'From Id': '-',
                'To Id': '-'
                }
        df18_19 = pd.DataFrame(data, columns=['From', 'To', 'From Id', 'To Id'])

    if s19_20:
        df19_20 = pd.DataFrame(s19_20, columns=['From', 'To', 'From Id', 'To Id'])
    else:
        data = {'From': ['Invalid Filter'],
                'To': ['Invalid Filter'],
                'From Id': '-',
                'To Id': '-'
                }
        df19_20 = pd.DataFrame(data, columns=['From', 'To', 'From Id', 'To Id'])

    # different request will be handled differently here
    # 'explore' is when we want to display the deault page
    # 'explore2' is when user uses the filtering function to plot a customized network
    if page == 'explore':
        graphJSON = plot(df, df17_18, df18_19, df19_20, 'init', False)
        myTable = create_table1(df_table, 'init', 1)
        return graphJSON, myTable
    elif page == 'explore2':
        graphJSON = plot(df, df17_18, df18_19, df19_20, 're', False)
        myTable = create_table1(df_table, 're', 1)
        return graphJSON, myTable
    elif page == 'statistics':
        cen = stats_table(df, 'init')
        return cen
    elif page == 'statistics2':
        cen = stats_table(df, 're')
        return cen


@cache.memoize(50)
def plot(df, df17_18, df18_19, df19_20, status, isBipartite):
    # this function is responsible for creating the network graph

    # create nodes of the network
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
    if isBipartite:
        pos = nx.bipartite_layout(G, df['From'].tolist())
        pos_17_18 = nx.bipartite_layout(G17_18, df17_18['From'].tolist())
        pos_18_19 = nx.bipartite_layout(G18_19, df18_19['From'].tolist())
        pos_19_20 = nx.bipartite_layout(G19_20, df19_20['From'].tolist())
    else:
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

    # assign information of the nodes to relevant nodes
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

    # add colors and texts to node points
    for node, adjacencies in enumerate(G.adjacency()):
        node_trace['marker']['color'] += tuple([len(adjacencies[1])])
        node_info = 'Name: ' + str(adjacencies[0]) + '<br># of connections: ' + str(len(adjacencies[1]))
        node_trace['hovertext'] += tuple([node_info])

    for node, adjacencies in enumerate(G17_18.adjacency()):
        node_trace_17_18['marker']['color'] += tuple([len(adjacencies[1])])
        node_info = 'Name: ' + str(adjacencies[0]) + '<br># of connections: ' + str(len(adjacencies[1]))
        node_trace_17_18['hovertext'] += tuple([node_info])

    for node, adjacencies in enumerate(G18_19.adjacency()):
        node_trace_18_19['marker']['color'] += tuple([len(adjacencies[1])])
        node_info = 'Name: ' + str(adjacencies[0]) + '<br># of connections: ' + str(len(adjacencies[1]))
        node_trace_18_19['hovertext'] += tuple([node_info])

    for node, adjacencies in enumerate(G19_20.adjacency()):
        node_trace_19_20['marker']['color'] += tuple([len(adjacencies[1])])
        node_info = 'Name: ' + str(adjacencies[0]) + '<br># of connections: ' + str(len(adjacencies[1]))
        node_trace_19_20['hovertext'] += tuple([node_info])

    # create the sliders to show dynamic networks
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

    # plot the network graph
    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        # title='<br>Football Transfer Network',
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
                        "prefix": "Season:",
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

    if status == 'init':
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    else:
        graphJSON = fig

    return graphJSON


def assign_nodes_edges(df):
    # this function is use to create nodes and edges for a network graph using the received data frame
    G = nx.Graph()
    for i in range(len(df)):
        f = df["From"][i]
        t = df["To"][i]
        G.add_node(f, id=df['From Id'][i])
        G.add_node(t, id=df['To Id'][i])
        G.add_edge(f, t)
    return G


def adjust_node_size(G):
    # this funciton is to adjust node size according to degree, etc
    d = nx.degree(G)
    node_sizes = []
    for i in d:
        _, value = i
        node_sizes.append(5 * value + 5)
    return node_sizes


def create_edge_scatter():
    # this function is to adjust the appearance of the edges
    edge_trace = go.Scatter(
        x=[],
        y=[],
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')
    return edge_trace


def create_node_scatter(node_sizes):
    # this function is to adjust the appearance of the nodes
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
def create_table1(df, status, extra_column):
    # this function is used to create the fact tables for the network pages

    # Populate the table
    items = []
    if extra_column == 1:
        # for network by clubs
        for clubName in df['name']:
            spent = u"\xA3" + str(float("{0:.2f}".format(df['spent'][clubName]))) + 'm'
            received = u"\xA3" + str(float("{0:.2f}".format(df['received'][clubName]))) + 'm'
            net = u"\xA3" + str(float("{0:.2f}".format(df['net'][clubName]))) + 'm'
            items.append(dict(name=df['name'][clubName], league=df['league'][clubName], country=df['country'][clubName],
                              transfer_in=df['transfer_in'][clubName], transfer_out=df['transfer_out'][clubName],
                              total_transfer=df['total_transfer'][clubName], spent=spent, received=received, net=net))
    elif extra_column == 2:
        # for network by leagues
        for leagueName in df['name']:
            spent = u"\xA3" + str(float("{0:.2f}".format(df['spent'][leagueName]))) + 'm'
            received = u"\xA3" + str(float("{0:.2f}".format(df['received'][leagueName]))) + 'm'
            net = u"\xA3" + str(float("{0:.2f}".format(df['net'][leagueName]))) + 'm'
            items.append(dict(name=df['name'][leagueName], country=df['country'][leagueName],
                              transfer_in=df['transfer_in'][leagueName], transfer_out=df['transfer_out'][leagueName],
                              total_transfer=df['total_transfer'][leagueName], spent=spent, received=received, net=net))
    else:
        # for network by countries
        for countryName in df['name']:
            spent = u"\xA3" + str(float("{0:.2f}".format(df['spent'][countryName]))) + 'm'
            received = u"\xA3" + str(float("{0:.2f}".format(df['received'][countryName]))) + 'm'
            net = u"\xA3" + str(float("{0:.2f}".format(df['net'][countryName]))) + 'm'
            items.append(dict(name=df['name'][countryName],
                              transfer_in=df['transfer_in'][countryName], transfer_out=df['transfer_out'][countryName],
                              total_transfer=df['total_transfer'][countryName], spent=spent, received=received,
                              net=net))

    if status == 'init':
        return items
    elif status == 're':
        table = dict(data=items)
        return table


@app.route('/explore_filter_1', methods=['GET', 'POST'])
def change_features():
    # this function is responsible to receive requests from client side (network by clubs) when user uses the filtering
    # function and return necessary response

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

    graphJSON = create_plot('explore2', season, league, country, position, nationality, ageFrom, ageTo, valueFrom, valueTo,
                            dateFrom, dateTo)
    return json.dumps(graphJSON, cls=plotly.utils.PlotlyJSONEncoder)


@app.route('/one', methods=['GET', 'POST'])
def change_features_ego():
    # this function is responsible to receive request from client side (network by clubs)
    # and return an ego network as response to the page

    clicked = request.args['clicked']
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

    graphJSON = create_plot_ego(clicked, season, league, country, position, nationality, ageFrom, ageTo, valueFrom, valueTo, dateFrom, dateTo)
    return json.dumps(graphJSON, cls=plotly.utils.PlotlyJSONEncoder)


@cache.memoize(50)
def create_plot_ego(clicked, season, league, country, position, nationality, ageFrom, ageTo, valueFrom, valueTo, dateFrom, dateTo):
    # this function is similar to create_plot, but it is responsible to filter values for the
    # ego network requested by users

    df_table = pd.DataFrame(columns=['name', 'league', 'country', 'transfer_in', 'transfer_out', 'total_transfer', 'spent', 'received', 'net'])
    df_table.set_index('name')

    # start of filtering process...
    transfers = Transfer.query.filter(or_(Transfer.fromId == clicked, Transfer.toId == clicked))
    if league != 'all':
        transfers = transfers.filter(and_(Transfer.fromLeagueId == league, Transfer.toLeagueId == league))

    if country != 'all':
        transfers = transfers.filter(and_(Transfer.fromCountry == country, Transfer.toCountry == country))

    if position != 'all':
        transfers = transfers.join(Player).filter(Player.position == position)

    if nationality != 'all':
        if position != 'all':
            transfers = transfers.filter(Player.nationality == nationality)
        else:
            transfers = transfers.join(Player).filter(Player.nationality == nationality)

    if ageFrom != '':
        if position != 'all' or nationality != 'all':
            transfers = transfers.filter(Player.age >= ageFrom)
        else:
            transfers = transfers.join(Player).filter(Player.age >= ageFrom)

    if ageTo != '':
        if position != 'all' or nationality != 'all' or ageFrom != '':
            transfers = transfers.filter(Player.age <= ageTo)
        else:
            transfers = transfers.join(Player).filter(Player.age <= ageTo)

    pair_clubs = []
    alter_id = []
    s17_18 = []
    s18_19 = []
    s19_20 = []

    for transfer in transfers:
        clubFrom = Club.query.filter_by(id=transfer.fromId).first()
        clubTo = Club.query.filter_by(id=transfer.toId).first()
        leagueFrom = League.query.filter_by(id=clubFrom.leagueId).first()
        leagueTo = League.query.filter_by(id=clubTo.leagueId).first()
        value = transfer.value
        date = datetime.utcfromtimestamp(int(transfer.timestamp)).strftime('%Y-%m-%d')

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

        if clicked == transfer.fromId:
            alter_id.append(transfer.toId)

        elif clicked == transfer.toId:
            alter_id.append(transfer.fromId)
        else:
            continue

        temp = [clubFrom.name, clubTo.name, transfer.fromId, transfer.toId]
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

        pair = [clubFrom.name, clubTo.name, transfer.fromId, transfer.toId]
        pair_clubs.append(pair)

        if clubFrom.name in df_table.values:
            df_table.loc[df_table.name == clubFrom.name, 'transfer_out'] += 1
            df_table.loc[df_table.name == clubFrom.name, 'total_transfer'] += 1
            df_table.loc[df_table.name == clubFrom.name, 'received'] += value
            df_table.loc[df_table.name == clubFrom.name, 'net'] -= value
        else:
            df_table.loc[clubFrom.name] = [clubFrom.name, leagueFrom.name, clubFrom.country, 0, 1, 1, 0, value, -value]

        if clubTo.name in df_table.values:
            df_table.loc[df_table.name == clubTo.name, 'transfer_in'] += 1
            df_table.loc[df_table.name == clubTo.name, 'total_transfer'] += 1
            df_table.loc[df_table.name == clubTo.name, 'spent'] += value
            df_table.loc[df_table.name == clubTo.name, 'net'] += value
        else:
            df_table.loc[clubTo.name] = [clubTo.name, leagueTo.name, clubTo.country, 1, 0, 1, value, 0, value]
    # end of filtering process...

    # grouping the focal nodes with alters
    for i in range(len(alter_id)):
        alterAsFrom = Transfer.query.filter_by(fromId=alter_id[i])
        for a in alterAsFrom:
            if a.toId in alter_id:
                clubFrom = Club.query.filter_by(id=alter_id[i]).first()
                clubTo = Club.query.filter_by(id=a.toId).first()
                temp = [clubFrom.name, clubTo.name, alter_id[i], a.toId]
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
                pair = [clubFrom.name, clubTo.name, alter_id[i], a.toId]
                pair_clubs.append(pair)

        alterAsTo = Transfer.query.filter_by(toId=alter_id[i])
        for a in alterAsTo:
            if a.fromId in alter_id:
                clubFrom = Club.query.filter_by(id=a.fromId).first()
                clubTo = Club.query.filter_by(id=alter_id[i]).first()
                temp = [clubFrom.name, clubTo.name, a.toId, alter_id[i]]
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
                pair = [clubFrom.name, clubTo.name, alter_id[i], a.toId]
                pair_clubs.append(pair)

    if pair_clubs:
        df = pd.DataFrame(pair_clubs, columns=['From', 'To', 'From Id', 'To Id'])
    else:
        data = {'From': ['Invalid Filter'],
                'To': ['Invalid Filter'],
                'From Id': '-',
                'To Id': '-'
                }
        df = pd.DataFrame(data, columns=['From', 'To', 'From Id', 'To Id'])

    if s17_18:
        df17_18 = pd.DataFrame(s17_18, columns=['From', 'To', 'From Id', 'To Id'])
    else:
        data = {'From': ['Invalid Filter'],
                'To': ['Invalid Filter'],
                'From Id': '-',
                'To Id': '-'
                }
        df17_18 = pd.DataFrame(data, columns=['From', 'To', 'From Id', 'To Id'])

    if s18_19:
        df18_19 = pd.DataFrame(s18_19, columns=['From', 'To', 'From Id', 'To Id'])
    else:
        data = {'From': ['Invalid Filter'],
                'To': ['Invalid Filter'],
                'From Id': '-',
                'To Id': '-'
                }
        df18_19 = pd.DataFrame(data, columns=['From', 'To', 'From Id', 'To Id'])

    if s19_20:
        df19_20 = pd.DataFrame(s19_20, columns=['From', 'To', 'From Id', 'To Id'])
    else:
        data = {'From': ['Invalid Filter'],
                'To': ['Invalid Filter'],
                'From Id': '-',
                'To Id': '-'
                }
        df19_20 = pd.DataFrame(data, columns=['From', 'To', 'From Id', 'To Id'])

        df = pd.DataFrame(data, columns=['From', 'To', 'From Id', 'To Id'])

    # Populate the table
    items = []
    records = 0
    for clubName in df_table['name']:
        spent = u"\xA3" + str(float("{0:.2f}".format(df_table['spent'][clubName]))) + 'm'
        received = u"\xA3" + str(float("{0:.2f}".format(df_table['received'][clubName]))) + 'm'
        net = u"\xA3" + str(float("{0:.2f}".format(df_table['net'][clubName]))) + 'm'

        items.append(dict(name=df_table['name'][clubName], league=df_table['league'][clubName],
                          country=df_table['country'][clubName], transfer_in=df_table['transfer_in'][clubName],
                          transfer_out=df_table['transfer_out'][clubName],
                          total_transfer=df_table['total_transfer'][clubName],
                          spent=spent, received=received, net=net))
        records += 1

    egotab = dict(data=items)

    graphJSON = plot(df, df17_18, df18_19, df19_20, 're', False)
    return graphJSON, egotab


# --------------Stats table-----------------------------------------------------------------
@app.route('/statistics/')
def statistics():
    # this function is responsible to display the statistics table in the statistic page

    # default filter values
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

    # to populate the values of the dropdown lists at the filtering section of the page
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

    country_list = sorted(list(dict.fromkeys(country_list)), key=str)
    season_list = sorted(list(dict.fromkeys(season_list)), key=str)
    position_list = sorted(list(dict.fromkeys(position_list)), key=str)
    nationality_list = sorted(list(dict.fromkeys(nationality_list)), key=str)

    table = create_plot('statistics', season, leagueid, country, position, nationality, ageFrom, ageTo, valueFrom,
                        valueTo, dateFrom, dateTo)

    return render_template('statistics.html', table=table[0], seasons=season_list,
                           leagues=league_lists, countries=country_list,
                           positions=position_list, nationalities=nationality_list, numer=table[1], denom=table[2],
                           reciprocity=table[3])


@app.route('/re_statistics/')
def re_statistics():
    # this function is responsible to  receive request from client side for statistic page and return a cuztomized
    # statistic page based on the filter value sent from client side
    season = request.args['season']
    league = request.args['league']
    country = request.args['country']
    position = request.args['position']
    nationality = request.args['nationality']
    level = request.args['level']
    ageFrom = request.args['ageFrom']
    ageTo = request.args['ageTo']
    valueFrom = request.args['valueFrom']
    valueTo = request.args['valueTo']
    dateFrom = request.args['dateFrom']
    dateTo = request.args['dateTo']

    if level == 'club':
        tables = create_plot('statistics2', season, league, country, position, nationality, ageFrom, ageTo, valueFrom,
                             valueTo, dateFrom, dateTo)
    elif level == 'league':
        tables = create_plot_league('statistics2', season, country, position, nationality, ageFrom, ageTo, valueFrom,
                                    valueTo, dateFrom, dateTo)
    else:
        tables = create_plot_country('statistics2', season, position, nationality, ageFrom, ageTo, valueFrom,
                                     valueTo, dateFrom, dateTo)

    return json.dumps(tables)


def stats_table(df, status):
    # this function is responsible to draw the centrality table and calculate reciprocity for statistic page
    items = []

    # centrality calculations using libraries from networkx
    G = assign_nodes_edges(df)
    bc = nx.betweenness_centrality(G)
    cc = nx.closeness_centrality(G)
    ec = nx.eigenvector_centrality(G)
    for node in G.degree:
        items.append(dict(name=node[0], deg=node[1], bet=round(bc[node[0]], 4), clo=round(cc[node[0]], 4), eig=round(ec[node[0]], 4)))

    numer = 0
    denom = 0
    for i in range(len(df)):
        x = df['From'][i]
        y = df['To'][i]
        denom += 1
        if not df.loc[(df['From'] == y) & (df['To'] == x)].empty:
            numer += 1

    reciprocity = numer/denom
    if status == 'init':
        return items, numer, denom, round(reciprocity, 4)
    elif status == 're':
        table = dict(data=items)
        return table, numer, denom, round(reciprocity, 4)


# --------------------------league level----------------------------------------------------
# ------------------------------------------------------------------------------------------
@app.route('/explore_league/')
@cache.cached(timeout=50)
def explore_league():
    # this function is for the 'explore - network by leagues' page

    # default filter parameters
    season = 'all'
    country = 'England'
    position = 'all'
    nationality = 'all'
    ageFrom = ''
    ageTo = ''
    valueFrom = ''
    valueTo = ''
    dateFrom = ''
    dateTo = ''

    country_list = []
    season_list = []
    position_list = []
    nationality_list = []

    # populate values for dropdown lists
    leagues = League.query.all()
    for league in leagues:
        country_list.append(league.country)

    transfers = Transfer.query.all()
    for transfer in transfers:
        season_list.append(transfer.season)

    players = Player.query.all()
    for player in players:
        position_list.append(player.position)
        nationality_list.append(player.nationality)

    # remove duplicates
    country_list = sorted(list(dict.fromkeys(country_list)), key=str)
    season_list = sorted(list(dict.fromkeys(season_list)), key=str)
    position_list = sorted(list(dict.fromkeys(position_list)), key=str)
    nationality_list = sorted(list(dict.fromkeys(nationality_list)), key=str)

    plots = create_plot_league('explore_league', season, country, position, nationality, ageFrom, ageTo, valueFrom,
                                   valueTo, dateFrom, dateTo)

    plot1 = plots[0]
    table1 = plots[1]

    return render_template('explore_league.html', plot=plot1, seasons=season_list, countries=country_list,
                           positions=position_list, nationalities=nationality_list, table1=table1)


def create_plot_league(page, season, country, position, nationality, ageFrom, ageTo, valueFrom, valueTo, dateFrom, dateTo):
    # this function is to retrieve relevant data from database based on the filter parameters,
    # and return graphs + tables for the page

    df_table = pd.DataFrame(columns=['name', 'country', 'transfer_in', 'transfer_out', 'total_transfer', 'spent',
                                     'received', 'net', 'link'])

    # filtering process starts...
    transfers = Transfer.query
    if country != 'all':
        transfers = transfers.filter(and_(Transfer.fromCountry == country, Transfer.toCountry == country))
    # position
    if position != 'all':
        transfers = transfers.join(Player).filter(Player.position == position)
    # nationality
    if nationality != 'all':
        if position != 'all':
            transfers = transfers.filter(Player.nationality == nationality)
        else:
            transfers = transfers.join(Player).filter(Player.nationality == nationality)

    # age
    if ageFrom != '':
        if position != 'all' or nationality != 'all':
            transfers = transfers.filter(Player.age >= ageFrom)
        else:
            transfers = transfers.join(Player).filter(Player.age >= ageFrom)

    if ageTo != '':
        if position != 'all' or nationality != 'all' or ageFrom != '':
            transfers = transfers.filter(Player.age <= ageTo)
        else:
            transfers = transfers.join(Player).filter(Player.age <= ageTo)

    s17_18 = []
    s18_19 = []
    s19_20 = []
    pair_leagues = []

    for transfer in transfers:
        clubFrom = Club.query.filter_by(id=transfer.fromId).first()
        clubTo = Club.query.filter_by(id=transfer.toId).first()
        LeagueFrom = League.query.filter_by(id=clubFrom.leagueId).first()
        LeagueTo = League.query.filter_by(id=clubTo.leagueId).first()
        value = transfer.value

        date = datetime.utcfromtimestamp(int(transfer.timestamp)).strftime('%Y-%m-%d')

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

        temp = [LeagueFrom.name, LeagueTo.name, LeagueFrom.id, LeagueTo.id]
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

        pair = [LeagueFrom.name, LeagueTo.name, LeagueFrom.id, LeagueTo.id]
        pair_leagues.append(pair)

        if LeagueFrom.name in df_table.values:
            df_table.loc[df_table.name == LeagueFrom.name, 'transfer_out'] += 1
            df_table.loc[df_table.name == LeagueFrom.name, 'total_transfer'] += 1
            df_table.loc[df_table.name == LeagueFrom.name, 'received'] += value
            df_table.loc[df_table.name == LeagueFrom.name, 'net'] -= value
        else:
            df_table.loc[LeagueFrom.name] = [LeagueFrom.name, LeagueFrom.country, 0, 1, 1, 0, value, -value, LeagueFrom.href]

        if LeagueTo.name in df_table.values:
            df_table.loc[df_table.name == LeagueTo.name, 'transfer_in'] += 1
            df_table.loc[df_table.name == LeagueTo.name, 'total_transfer'] += 1
            df_table.loc[df_table.name == LeagueTo.name, 'spent'] += value
            df_table.loc[df_table.name == LeagueTo.name, 'net'] += value
        else:
            df_table.loc[LeagueTo.name] = [LeagueTo.name, LeagueTo.country, 1, 0, 1, value, 0, value, LeagueTo.href]
    # filtering process ends...

    if pair_leagues:
        df = pd.DataFrame(pair_leagues, columns=['From', 'To', 'From Id', 'To Id'])
    else:
        data = {'From': ['Invalid Filter'],
                'To': ['Invalid Filter'],
                'From Id': '-',
                'To Id': '-'
                }
        df = pd.DataFrame(data, columns=['From', 'To', 'From Id', 'To Id'])

    if s17_18:
        df17_18 = pd.DataFrame(s17_18, columns=['From', 'To', 'From Id', 'To Id'])
    else:
        data = {'From': ['Invalid Filter'],
                'To': ['Invalid Filter'],
                'From Id': '-',
                'To Id': '-'
                }
        df17_18 = pd.DataFrame(data, columns=['From', 'To', 'From Id', 'To Id'])

    if s18_19:
        df18_19 = pd.DataFrame(s18_19, columns=['From', 'To', 'From Id', 'To Id'])
    else:
        data = {'From': ['Invalid Filter'],
                'To': ['Invalid Filter'],
                'From Id': '-',
                'To Id': '-'
                }
        df18_19 = pd.DataFrame(data, columns=['From', 'To', 'From Id', 'To Id'])

    if s19_20:
        df19_20 = pd.DataFrame(s19_20, columns=['From', 'To', 'From Id', 'To Id'])
    else:
        data = {'From': ['Invalid Filter'],
                'To': ['Invalid Filter'],
                'From Id': '-',
                'To Id': '-'
                }
        df19_20 = pd.DataFrame(data, columns=['From', 'To', 'From Id', 'To Id'])

    if page == 'explore_league':
        graphJSON = plot(df, df17_18, df18_19, df19_20, 'init', False)
        myTable = create_table1(df_table, 'init', 2)
        return graphJSON, myTable
    elif page == 'explore_league2':
        graphJSON = plot(df, df17_18, df18_19, df19_20, 're', False)
        myTable = create_table1(df_table, 're', 2)
        return graphJSON, myTable
    elif page == 'statistics2':
        cen = stats_table(df, 're')
        return cen


@app.route('/explore_league_filter', methods=['GET', 'POST'])
def change_features_league():
    # this function is responsible to receive request from client side
    # and return customized graph and table based on value sent from client side

    season = request.args['season']
    country = request.args['country']
    position = request.args['position']
    nationality = request.args['nationality']
    ageFrom = request.args['ageFrom']
    ageTo = request.args['ageTo']
    valueFrom = request.args['valueFrom']
    valueTo = request.args['valueTo']
    dateFrom = request.args['dateFrom']
    dateTo = request.args['dateTo']

    graphJSON = create_plot_league('explore_league2', season, country, position, nationality, ageFrom, ageTo, valueFrom,
                                   valueTo, dateFrom, dateTo)
    return json.dumps(graphJSON, cls=plotly.utils.PlotlyJSONEncoder)


@app.route('/league_one', methods=['GET', 'POST'])
def changes_features_league_ego():
    # this function is responsible to receive request from client side
    # and return customized ego network graph and table based on value sent from client side

    clicked = request.args['clicked']
    season = request.args['season']
    country = request.args['country']
    position = request.args['position']
    nationality = request.args['nationality']
    ageFrom = request.args['ageFrom']
    ageTo = request.args['ageTo']
    valueFrom = request.args['valueFrom']
    valueTo = request.args['valueTo']
    dateFrom = request.args['dateFrom']
    dateTo = request.args['dateTo']

    graphJSON = create_plot_league_ego(clicked, season, country, position, nationality, ageFrom, ageTo, valueFrom,
                                       valueTo, dateFrom, dateTo)
    return json.dumps(graphJSON, cls=plotly.utils.PlotlyJSONEncoder)


def create_plot_league_ego(clicked, season, country, position, nationality, ageFrom, ageTo, valueFrom,
                           valueTo, dateFrom, dateTo):
    # this function is to retrieve relevant data from database based on the filter parameters,
    # and return customized ego network graphs + tables

    df_table = pd.DataFrame(columns=['name', 'country', 'transfer_in', 'transfer_out', 'total_transfer', 'spent',
                                     'received', 'net'])
    # filtering process starts...
    transfers = Transfer.query.filter(or_(Transfer.fromLeagueId == clicked, Transfer.toLeagueId == clicked))
    if country != 'all':
        transfers = transfers.filter(and_(Transfer.fromCountry == country, Transfer.toCountry == country))

    if position != 'all':
        transfers = transfers.join(Player).filter(Player.position == position)

    if nationality != 'all':
        if position != 'all':
            transfers = transfers.filter(Player.nationality == nationality)
        else:
            transfers = transfers.join(Player).filter(Player.nationality == nationality)

    if ageFrom != '':
        if position != 'all' or nationality != 'all':
            transfers = transfers.filter(Player.age >= ageFrom)
        else:
            transfers = transfers.join(Player).filter(Player.age >= ageFrom)

    if ageTo != '':
        if position != 'all' or nationality != 'all' or ageFrom != '':
            transfers = transfers.filter(Player.age <= ageTo)
        else:
            transfers = transfers.join(Player).filter(Player.age <= ageTo)
    pair_leagues = []
    alter_id = []
    s17_18 = []
    s18_19 = []
    s19_20 = []

    for transfer in transfers:
        clubFrom = Club.query.filter_by(id=transfer.fromId).first()
        clubTo = Club.query.filter_by(id=transfer.toId).first()
        leagueFrom = League.query.filter_by(id=clubFrom.leagueId).first()
        leagueTo = League.query.filter_by(id=clubTo.leagueId).first()

        value = transfer.value
        date = datetime.utcfromtimestamp(int(transfer.timestamp)).strftime('%Y-%m-%d')

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

        temp = [leagueFrom.name, leagueTo.name, leagueFrom.id, leagueTo.id]
        if transfer.season == '2017/2018':
            s17_18.append(temp)
        elif transfer.season == '2018/2019':
            s18_19.append(temp)
        elif transfer.season == '2019/2020':
            s19_20.append(temp)

        if clicked == leagueFrom.id:
            alter_id.append(transfer.toId)

        elif clicked == leagueTo.id:
            alter_id.append(transfer.fromId)
        else:
            continue

        if dateFrom != '':
            if date < dateFrom:
                continue

        if dateTo != '':
            if date > dateTo:
                continue

        if season != 'all':
            if transfer.season != season:
                continue

        pair = [leagueFrom.name, leagueTo.name, leagueFrom.id, leagueTo.id]
        pair_leagues.append(pair)

        # for the tables
        if leagueFrom.name in df_table.values:
            df_table.loc[df_table.name == leagueFrom.name, 'transfer_out'] += 1
            df_table.loc[df_table.name == leagueFrom.name, 'total_transfer'] += 1
            df_table.loc[df_table.name == leagueFrom.name, 'received'] += value
            df_table.loc[df_table.name == leagueFrom.name, 'net'] -= value
        else:
            df_table.loc[leagueFrom.name] = [leagueFrom.name, leagueFrom.country, 0, 1, 1, 0, value, -value]

        if leagueTo.name in df_table.values:
            df_table.loc[df_table.name == leagueTo.name, 'transfer_in'] += 1
            df_table.loc[df_table.name == leagueTo.name, 'total_transfer'] += 1
            df_table.loc[df_table.name == leagueTo.name, 'spent'] += value
            df_table.loc[df_table.name == leagueTo.name, 'net'] += value
        else:
            df_table.loc[leagueTo.name] = [leagueTo.name, leagueTo.country, 1, 0, 1, value, 0, value]
    # filtering process ends...

    for i in range(len(alter_id)):
        alterAsFrom = Transfer.query.filter_by(fromId=alter_id[i])
        for a in alterAsFrom:
            if a.toId in alter_id:
                clubFrom = Club.query.filter_by(id=alter_id[i]).first()
                clubTo = Club.query.filter_by(id=a.toId).first()
                leagueFrom = League.query.filter_by(id=clubFrom.leagueId).first()
                leagueTo = League.query.filter_by(id=clubTo.leagueId).first()
                temp = [leagueFrom.name, leagueTo.name, leagueFrom.id, leagueTo.id]
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
                pair = [leagueFrom.name, leagueTo.name, leagueFrom.id, leagueTo.id]
                pair_leagues.append(pair)

        alterAsTo = Transfer.query.filter_by(toId=alter_id[i])
        for a in alterAsTo:
            if a.fromId in alter_id:
                clubFrom = Club.query.filter_by(id=a.fromId).first()
                clubTo = Club.query.filter_by(id=alter_id[i]).first()
                leagueFrom = League.query.filter_by(id=clubFrom.leagueId).first()
                leagueTo = League.query.filter_by(id=clubTo.leagueId).first()
                temp = [leagueFrom.name, leagueTo.name, leagueFrom.id, leagueTo.id]
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
                pair = [leagueFrom.name, leagueTo.name, leagueFrom.id, leagueTo.id]
                pair_leagues.append(pair)

    if pair_leagues:
        df = pd.DataFrame(pair_leagues, columns=['From', 'To', 'From Id', 'To Id'])
    else:
        data = {'From': ['Invalid Filter'],
                'To': ['Invalid Filter'],
                'From Id': '-',
                'To Id': '-'
                }
        df = pd.DataFrame(data, columns=['From', 'To', 'From Id', 'To Id'])

    if s17_18:
        df17_18 = pd.DataFrame(s17_18, columns=['From', 'To', 'From Id', 'To Id'])
    else:
        data = {'From': ['Invalid Filter'],
                'To': ['Invalid Filter'],
                'From Id': '-',
                'To Id': '-'
                }
        df17_18 = pd.DataFrame(data, columns=['From', 'To', 'From Id', 'To Id'])

    if s18_19:
        df18_19 = pd.DataFrame(s18_19, columns=['From', 'To', 'From Id', 'To Id'])
    else:
        data = {'From': ['Invalid Filter'],
                'To': ['Invalid Filter'],
                'From Id': '-',
                'To Id': '-'
                }
        df18_19 = pd.DataFrame(data, columns=['From', 'To', 'From Id', 'To Id'])

    if s19_20:
        df19_20 = pd.DataFrame(s19_20, columns=['From', 'To', 'From Id', 'To Id'])
    else:
        data = {'From': ['Invalid Filter'],
                'To': ['Invalid Filter'],
                'From Id': '-',
                'To Id': '-'
                }
        df19_20 = pd.DataFrame(data, columns=['From', 'To', 'From Id', 'To Id'])

        df = pd.DataFrame(data, columns=['From', 'To', 'From Id', 'To Id'])

    # Populate the table
    items = []
    records = 0
    for leagueName in df_table['name']:
        spent = u"\xA3" + str(float("{0:.2f}".format(df_table['spent'][leagueName]))) + 'm'
        received = u"\xA3" + str(float("{0:.2f}".format(df_table['received'][leagueName]))) + 'm'
        net = u"\xA3" + str(float("{0:.2f}".format(df_table['net'][leagueName]))) + 'm'

        items.append(dict(name=df_table['name'][leagueName], country=df_table['country'][leagueName],
                          transfer_in=df_table['transfer_in'][leagueName],
                          transfer_out=df_table['transfer_out'][leagueName],
                          total_transfer=df_table['total_transfer'][leagueName],
                          spent=spent, received=received, net=net))
        records += 1

    graphJSON = plot(df, df17_18, df18_19, df19_20, 're', False)
    ego_tab = dict(data=items)
    return graphJSON, ego_tab


# ------------------------country level-----------------------------------------------------
# ------------------------------------------------------------------------------------------
@app.route('/explore_country/')
@cache.cached(timeout=50)
def explore_country():
    # this function is for the 'explore - network by leagues' page

    # default filter values
    season = 'all'
    position = 'Forward'
    nationality = 'England'
    ageFrom = ''
    ageTo = ''
    valueFrom = ''
    valueTo = ''
    dateFrom = ''
    dateTo = ''

    season_list = []
    position_list = []
    nationality_list = []

    # populate values for dropdown menus at the filtering section
    transfers = Transfer.query.all()
    for transfer in transfers:
        season_list.append(transfer.season)

    players = Player.query.all()
    for player in players:
        position_list.append(player.position)
        nationality_list.append(player.nationality)

    # remove duplicates
    season_list = sorted(list(dict.fromkeys(season_list)), key=str)
    position_list = sorted(list(dict.fromkeys(position_list)), key=str)
    nationality_list = sorted(list(dict.fromkeys(nationality_list)), key=str)

    plots = create_plot_country('explore_country', season, position, nationality, ageFrom, ageTo, valueFrom, valueTo,
                                dateFrom, dateTo)

    plot1 = plots[0]
    table1 = plots[1]

    return render_template('explore_country.html', plot=plot1, seasons=season_list,
                           positions=position_list, nationalities=nationality_list, table1=table1)


def create_plot_country(page, season, position, nationality, ageFrom, ageTo, valueFrom, valueTo, dateFrom, dateTo):
    # this function is to retrieve relevant data from database based on the filter parameters,
    # and return graphs + tables for the page

    df_table = pd.DataFrame(columns=['name', 'transfer_in', 'transfer_out', 'total_transfer', 'spent', 'received', 'net', 'link'])

    # filtering process starts...
    transfers = Transfer.query
    # position
    if position != 'all':
        transfers = transfers.join(Player).filter(Player.position == position)
    # nationality
    if nationality != 'all':
        if position != 'all':
            transfers = transfers.filter(Player.nationality == nationality)
        else:
            transfers = transfers.join(Player).filter(Player.nationality == nationality)

    # age
    if ageFrom != '':
        if position != 'all' or nationality != 'all':
            transfers = transfers.filter(Player.age >= ageFrom)
        else :
            transfers = transfers.join(Player).filter(Player.age >= ageFrom)

    if ageTo != '':
        if position != 'all' or nationality != 'all' or ageFrom != '':
            transfers = transfers.filter(Player.age <= ageTo)
        else:
            transfers = transfers.join(Player).filter(Player.age <= ageTo)
    s17_18 = []
    s18_19 = []
    s19_20 = []
    pair_countries = []

    for transfer in transfers:
        clubFrom = Club.query.filter_by(id=transfer.fromId).first()
        clubTo = Club.query.filter_by(id=transfer.toId).first()
        value = transfer.value
        country_from = clubFrom.country
        country_to = clubTo.country
        date = datetime.utcfromtimestamp(int(transfer.timestamp)).strftime('%Y-%m-%d')

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

        temp = [country_from, country_to, 1, 1]
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

        pair = [country_from, country_to, 1, 1]
        pair_countries.append(pair)

        if country_from in df_table.values:
            df_table.loc[df_table.name == country_from, 'transfer_out'] += 1
            df_table.loc[df_table.name == country_from, 'total_transfer'] += 1
            df_table.loc[df_table.name == country_from, 'received'] += value
            df_table.loc[df_table.name == country_from, 'net'] -= value
        else:
            df_table.loc[country_from] = [country_from, 0, 1, 1, 0, value, -value, '#']

        if country_to in df_table.values:
            df_table.loc[df_table.name == country_to, 'transfer_in'] += 1
            df_table.loc[df_table.name == country_to, 'total_transfer'] += 1
            df_table.loc[df_table.name == country_to, 'spent'] += value
            df_table.loc[df_table.name == country_to, 'net'] += value
        else:
            df_table.loc[country_to] = [country_to, 1, 0, 1, value, 0, value, '#']
    # filtering process ends...

    if pair_countries:
        df = pd.DataFrame(pair_countries, columns=['From', 'To', 'From Id', 'To Id'])
    else:
        data = {'From': ['Invalid Filter'],
                'To': ['Invalid Filter'],
                'From Id': '-',
                'To Id': '-'
                }
        df = pd.DataFrame(data, columns=['From', 'To', 'From Id', 'To Id'])

    if s17_18:
        df17_18 = pd.DataFrame(s17_18, columns=['From', 'To', 'From Id', 'To Id'])
    else:
        data = {'From': ['Invalid Filter'],
                'To': ['Invalid Filter'],
                'From Id': '-',
                'To Id': '-'
                }
        df17_18 = pd.DataFrame(data, columns=['From', 'To', 'From Id', 'To Id'])

    if s18_19:
        df18_19 = pd.DataFrame(s18_19, columns=['From', 'To',  'From Id', 'To Id'])
    else:
        data = {'From': ['Invalid Filter'],
                'To': ['Invalid Filter'],
                'From Id': '-',
                'To Id': '-'
                }
        df18_19 = pd.DataFrame(data, columns=['From', 'To', 'From Id', 'To Id'])

    if s19_20:
        df19_20 = pd.DataFrame(s19_20, columns=['From', 'To', 'From Id', 'To Id'])
    else:
        data = {'From': ['Invalid Filter'],
                'To': ['Invalid Filter'],
                'From Id': '-',
                'To Id': '-'
                }
        df19_20 = pd.DataFrame(data, columns=['From', 'To', 'From Id', 'To Id'])

    if page == 'explore_country':
        graphJSON = plot(df, df17_18, df18_19, df19_20, 'init', False)
        myTable = create_table1(df_table, 'init', 0)
        return graphJSON, myTable
    elif page == 'explore_country2':
        graphJSON = plot(df, df17_18, df18_19, df19_20, 're', False)
        myTable = create_table1(df_table, 're', 0)
        return graphJSON, myTable
    elif page == 'statistics2':
        cen = stats_table(df, 're')
        return cen


@app.route('/explore_country_filter', methods=['GET', 'POST'])
def change_features_country():
    # this function is responsible to receive request from client side
    # and return customized graph and table based on value sent from client side

    season = request.args['season']
    position = request.args['position']
    nationality = request.args['nationality']
    ageFrom = request.args['ageFrom']
    ageTo = request.args['ageTo']
    valueFrom = request.args['valueFrom']
    valueTo = request.args['valueTo']
    dateFrom = request.args['dateFrom']
    dateTo = request.args['dateTo']

    graphJSON = create_plot_country('explore_country2', season, position, nationality, ageFrom, ageTo, valueFrom,
                                    valueTo, dateFrom, dateTo)
    return json.dumps(graphJSON, cls=plotly.utils.PlotlyJSONEncoder)


# -------------------------network by players (ego network)---------------------------------
# ------------------------------------------------------------------------------------------
@app.route('/explore_player')
@cache.cached(timeout=50)
def explore_player():
    # this function is for the 'explore - network by leagues' page

    # default filter values
    season = 'all'
    position = 'all'
    nationality = 'Brazil'
    ageFrom = ''
    ageTo = ''
    valueFrom = ''
    valueTo = ''
    dateFrom = ''
    dateTo = ''
    country = 'all'

    country_list = []
    season_list = []
    position_list = []
    nationality_list = []

    # populate values for dropdown menus
    leagues = League.query.all()
    for league in leagues:
        country_list.append(league.country)

    transfers = Transfer.query.all()
    for transfer in transfers:
        season_list.append(transfer.season)

    players = Player.query.all()
    for player in players:
        position_list.append(player.position)
        nationality_list.append(player.nationality)

    # remove duplicates
    country_list = sorted(list(dict.fromkeys(country_list)), key=str)
    season_list = sorted(list(dict.fromkeys(season_list)), key=str)
    position_list = sorted(list(dict.fromkeys(position_list)), key=str)
    nationality_list = sorted(list(dict.fromkeys(nationality_list)), key=str)

    plots = create_plot_player('explore_player', season, country, position, nationality, ageFrom, ageTo, valueFrom,
                                   valueTo,
                                   dateFrom, dateTo)

    plot1 = plots[0]
    table1 = plots[1]

    return render_template('explore_player.html', plot=plot1, seasons=season_list, countries=country_list,
                           positions=position_list, nationalities=nationality_list, table1=table1)


def create_plot_player(page, season, country, position, nationality, ageFrom, ageTo, valueFrom, valueTo, dateFrom, dateTo):
    # this function is to retrieve relevant data from database based on the filter parameters,
    # and return graphs + tables for the page

    df_table = pd.DataFrame(columns=['player_nationality', 'destination', 'total_transfer'])

    # filtering process starts...
    transfers = Transfer.query
    if country != 'all':
        transfers = transfers.filter(Transfer.toCountry == country)
    # position
    if position != 'all':
        transfers = transfers.join(Player).filter(Player.position == position)
    # nationality
    if nationality != 'all':
        if position != 'all':
            transfers = transfers.filter(Player.nationality == nationality)
        else:
            transfers = transfers.join(Player).filter(Player.nationality == nationality)

    # age
    if ageFrom != '':
        if position != 'all' or nationality != 'all':
            transfers = transfers.filter(Player.age >= ageFrom)
        else:
            transfers = transfers.join(Player).filter(Player.age >= ageFrom)

    if ageTo != '':
        if position != 'all' or nationality != 'all' or ageFrom != '':
            transfers = transfers.filter(Player.age <= ageTo)
        else:
            transfers = transfers.join(Player).filter(Player.age <= ageTo)

    s17_18 = []
    s18_19 = []
    s19_20 = []
    pair_playerCountry = []

    for transfer in transfers:
        clubTo = Club.query.filter_by(id=transfer.toId).first()
        value = transfer.value
        country_to = clubTo.country
        player_nationality = Player.query.filter_by(id=transfer.playerId).first().nationality
        date = datetime.utcfromtimestamp(int(transfer.timestamp)).strftime('%Y-%m-%d')

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

        pval = player_nationality + ' - player'
        dval = country_to + ' - destination'
        temp = [pval, dval, '#', '#']
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

        pval = player_nationality + ' - player'
        dval = country_to + ' - destination'

        pair = [pval, dval, '#', '#']
        pair_playerCountry.append(pair)
        if not df_table.loc[(df_table['player_nationality'] == player_nationality) & (df_table['destination'] == country_to)].empty:
            df_table.loc[(df_table['player_nationality'] == player_nationality) & (
                        df_table['destination'] == country_to), 'total_transfer'] += 1
        else:
            temp_df = pd.DataFrame([[player_nationality, country_to, 1]],
                                   columns=['player_nationality', 'destination', 'total_transfer'])
            df_table = pd.concat([df_table, temp_df])
    # filtering process ends...

    if pair_playerCountry:
        df = pd.DataFrame(pair_playerCountry, columns=['From', 'To', 'From Id', 'To Id'])
    else:
        data = {'From': ['Invalid Filter'],
                'To': ['Invalid Filter'],
                'From Id': '-',
                'To Id': '-'
                }
        df = pd.DataFrame(data, columns=['From', 'To', 'From Id', 'To Id'])

    if s17_18:
        df17_18 = pd.DataFrame(s17_18, columns=['From', 'To', 'From Id', 'To Id'])
    else:
        data = {'From': ['Invalid Filter'],
                'To': ['Invalid Filter'],
                'From Id': '-',
                'To Id': '-'
                }
        df17_18 = pd.DataFrame(data, columns=['From', 'To', 'From Id', 'To Id'])

    if s18_19:
        df18_19 = pd.DataFrame(s18_19, columns=['From', 'To', 'From Id', 'To Id'])
    else:
        data = {'From': ['Invalid Filter'],
                'To': ['Invalid Filter'],
                'From Id': '-',
                'To Id': '-'
                }
        df18_19 = pd.DataFrame(data, columns=['From', 'To', 'From Id', 'To Id'])

    if s19_20:
        df19_20 = pd.DataFrame(s19_20, columns=['From', 'To', 'From Id', 'To Id'])
    else:
        data = {'From': ['Invalid Filter'],
                'To': ['Invalid Filter'],
                'From Id': '-',
                'To Id': '-'
                }
        df19_20 = pd.DataFrame(data, columns=['From', 'To', 'From Id', 'To Id'])

    if page == 'explore_player':
        graphJSON = plot(df, df17_18, df18_19, df19_20, 'init', True)
        myTable = create_table_player(df_table, 'init')
        return graphJSON, myTable
    elif page == 'explore_player2':
        graphJSON = plot(df, df17_18, df18_19, df19_20, 're', True)
        myTable = create_table_player(df_table, 're')
        return graphJSON, myTable


def create_table_player(df, status):
    # Populate the table
    items = df.to_dict(orient='records')

    if status == 'init':
        return items
    elif status == 're':
        proper_json = dict(data=items)
        return proper_json


@app.route('/explore_player_filter', methods=['GET', 'POST'])
def change_features_player():
    # this function is responsible to receive request from client side
    # and return customized graph and table based on value sent from client side

    season = request.args['season']
    country = request.args['country']
    position = request.args['position']
    nationality = request.args['nationality']
    ageFrom = request.args['ageFrom']
    ageTo = request.args['ageTo']
    valueFrom = request.args['valueFrom']
    valueTo = request.args['valueTo']
    dateFrom = request.args['dateFrom']
    dateTo = request.args['dateTo']

    graphJSON = create_plot_player('explore_player2', season, country, position, nationality, ageFrom, ageTo, valueFrom,
                                   valueTo, dateFrom, dateTo)
    return json.dumps(graphJSON, cls=plotly.utils.PlotlyJSONEncoder)
