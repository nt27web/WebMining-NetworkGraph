import json
import urllib
from os import system

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd


def analyse_graph():

    # get airport data dump
    airport_json = get_airport_data()
    # prepare a subset of the data with limited columns
    airport_df = pd.DataFrame.from_records(airport_json, columns=['city_code', 'country_code','name','code'])
    # print(json.dumps(airport_json, indent=4, ))
    # filter dataframe to use US airports only
    airport_us = airport_df.query('country_code == "US"')
    # get a ist of indexes with US airports for filtering of route data
    airport_us_in = airport_us['code']

    # get routes data dump
    routes_df = get_routes_data()
    # print(json.dumps(routes_df, indent=4, ))
    # prepare seubset of data with limited columns
    routes_us = pd.DataFrame.from_records(routes_df, columns=['departure_airport_iata', 'arrival_airport_iata'])
    # add a column to count flights between two airports
    routes_us['flights'] = len(routes_df[0]["planes"])
    # filtered routes for origin ad destination airports within US
    routes_us_f = routes_us.loc[(routes_us['departure_airport_iata'].isin(airport_us_in)) &
                          (routes_us['arrival_airport_iata'].isin(airport_us_in))]
    # calculate the count between two airports in any direction
    routes_us_g = pd.DataFrame(routes_us_f.groupby(['departure_airport_iata', 'arrival_airport_iata']).size().reset_index(name='counts'))
    # filter routes based on number connections more than 5
    routes_us_g = routes_us_g[routes_us_g['counts'] > 3]
    # pass this dataframe to draw the network graph of connectivities
    draw_graph(routes_us_g)
    # calculate and show centralities(Closeness, Betweenness)
    show_centrality(routes_us_g)


def get_routes_data():
    url = "http://api.travelpayouts.com/data/routes.json"
    with urllib.request.urlopen(url) as url:
        data = json.loads(url.read().decode("utf-8"))
    return data


def get_airport_data():
    url = 'https://api.travelpayouts.com/data/en/airports.json'
    with urllib.request.urlopen(url) as url:
        airport_json = json.loads(url.read().decode("utf-8"))
    return airport_json


def draw_graph(data):
    plt.figure(figsize=(50, 50))
    # 1. Create the graph
    g = nx.from_pandas_edgelist(data, source='departure_airport_iata', target='arrival_airport_iata')

    # 2. Create a layout for our nodes
    layout = nx.spring_layout(g, iterations=50)
    # 3. Draw the parts we want
    nx.draw_networkx_edges(g, layout, edge_color='#AAAAAA')

    dest = [node for node in g.nodes() if node in data.arrival_airport_iata.unique()]
    size = [g.degree(node) * 80 for node in g.nodes() if node in data.arrival_airport_iata.unique()]
    nx.draw_networkx_nodes(g, layout, nodelist=dest, node_size=size, node_color='lightblue')

    orig = [node for node in g.nodes() if node in data.departure_airport_iata.unique()]
    nx.draw_networkx_nodes(g, layout, nodelist=orig, node_size=100, node_color='#AAAAAA')

    high_degree_orig = [node for node in g.nodes() if node in data.departure_airport_iata.unique() and g.degree(node) > 1]
    nx.draw_networkx_nodes(g, layout, nodelist=high_degree_orig, node_size=100, node_color='#fc8d62')

    orig_dict = dict(zip(orig, orig))
    nx.draw_networkx_labels(g, layout, labels=orig_dict)

    # 4. Turn off the axis because I know you don't want it
    plt.axis('off')
    plt.title("Connections between Airports(US))")
    # 5. Tell matplotlib to show it
    plt.show()
    plt.savefig('routes_us.png')


def show_centrality(data):
    # prepare graph object using dataset
    g = nx.from_pandas_edgelist(data, source='departure_airport_iata', target='arrival_airport_iata')
    # calculate degree centrality
    deg_cen = nx.degree_centrality(g)
    print(deg_cen)
    # calculate closeness centrality
    cl_cen = nx.closeness_centrality(g)
    print(cl_cen)
    # calculate betweenness centrality
    bet_cen = nx.betweenness_centrality(g)
    print(bet_cen)
    # test


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    analyse_graph()
