import streamlit as st
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
import numpy as np
import pandas as pd
from simulation import *
import matplotlib.pyplot as plt
import seaborn as sns

"""
# Network Epidemic Playground
Continuous-time stochastic simulation of epidemic spreading on human-to-human contact networks:
"""


def colors():
    colors = {'S': sns.xkcd_rgb['denim blue'], 'E': sns.xkcd_rgb['bright orange'], 'I1': sns.xkcd_rgb['light red'],
              'I': sns.xkcd_rgb['light red'],
              'I2': sns.xkcd_rgb['pinkish red'], 'I3': sns.xkcd_rgb['deep pink'], 'R': sns.xkcd_rgb['medium green'],
              'D': sns.xkcd_rgb['black'], 'V': sns.xkcd_rgb['jade']}
    colors['I_total'] = 'gray'  # need to add states from finalize
    return colors


'''
## Epidemic Model
'''
option_model = st.selectbox('Spreading Model', ('SI model', 'SEIRS model', 'Corona model', 'Custom'))

if option_model == 'SI model':
    st.markdown(f'States: `S,I`')
    # r1 = st.slider('S->I', min_value=1.0, max_value=200.0, value=20.0)
    r1 = st.slider('I+S->I+I', min_value=0.0, max_value=20.0, value=0.5, key='si_r1')
    states_eval = ["S", "I"]
    rules_eval = [(("I", "S"), ("I", "I"), float(r1))]
elif option_model == 'SEIRS model':
    st.markdown(f'States: `S,E,I,R`')
    # r1 = st.slider('S->I', min_value=1.0, max_value=200.0, value=20.0)
    r1 = st.slider('I+S->I+E', min_value=0.0, max_value=20.0, value=0.5, key='seirs_r1')
    r2 = st.slider('E->I', min_value=0.0, max_value=20.0, value=0.5, key='seirs_r2')
    r3 = st.slider('I->R', min_value=0.0, max_value=20.0, value=0.5, key='seirs_r3')
    r4 = st.slider('R->S', min_value=0.0, max_value=20.0, value=0.5, key='seirs_r4')
    states_eval = ["S", "E", "I", "R"]
    rules_eval = [(("I", "S"), ("I", "I"), float(r1)), ("E", "I", float(r2)), ("I", "R", float(r3)),
                  ("R", "S", float(r4))]
elif option_model == 'Corona model':
    st.markdown(f'States: `S,E,I1,I2,I3,R,V,D`')
    states_eval = ["S", "E", "I1", "I2", "I3", "R", "V", "D"]

    r1 = st.slider('I1+S->I1+E', min_value=0.0, max_value=20.0, value=0.5, key='CH_r1')
    r2 = st.slider('I2+S->I2+E', min_value=0.0, max_value=20.0, value=0.5, key='CH_r2')
    r3 = st.slider('I3+S->I3+E', min_value=0.0, max_value=20.0, value=0.5, key='CH_r3')

    r4 = st.slider('E->I1', min_value=0.0, max_value=20.0, value=0.5, key='CH_r4')
    r5 = st.slider('I1->I2', min_value=0.0, max_value=20.0, value=0.5, key='CH_r5')
    r6 = st.slider('I2->I3', min_value=0.0, max_value=20.0, value=0.5, key='CH_r6')
    r7 = st.slider('I3->D', min_value=0.0, max_value=20.0, value=0.5, key='CH_r7')

    r8 = st.slider('I1->R', min_value=0.0, max_value=20.0, value=0.5, key='CH_r8')
    r9 = st.slider('I2->R', min_value=0.0, max_value=20.0, value=0.5, key='CH_r9')
    r10 = st.slider('I3->R', min_value=0.0, max_value=20.0, value=0.5, key='CH_10')

    rules_eval = [(("I1", "S"), ("I1", "E"), float(r1)), (("I2", "S"), ("I2", "E"), float(r2)),
                  (("I3", "S"), ("I3", "E"), float(r3)), ("E", "I1", float(r4)), ("I1", "I2", float(r5)),
                  ("I2", "I3", float(r6)), ("I3", "D", float(r7)), ("I1", "R", float(r8)), ("I2", "R", float(r9)),
                  ("I3", "R", float(r10))]

else:
    states = ["S", "I", "R"]
    rules = [("I", "R", 1.0),  # spontaneous rule  I -> R with rate 1.0
             ("R", "S", 0.7),  # spontaneous rule R -> S with rate 0.7
             (("I", "S"), ("I", "I"), 0.8)]
    rules_text = [repr(r) for r in rules]
    rules_text = '\n'.join(rules_text)
    epidemic_states_text = st.text_input("Enter states/compartments (separated by comma):", value='S,I,R')
    epidemic_model_text = st.text_area("Enter interaction rules (separated by line):", value=rules_text)
    states_eval = eval('"' + epidemic_states_text.replace(',', '","') + '"')
    rules_eval = eval('[' + epidemic_model_text.replace('\n', ',') + ' ]')

states_eval = sorted(list(set(states_eval)))

'''
## Contact Network
'''
import networkx as nx

option_network = st.selectbox('Contact Network', ('Karate', '2D-Grid', 'Geometric', 'Custom'))
pos = None

if option_network == 'Karate':
    G = nx.karate_club_graph()
    edges = list(G.edges)
    st.markdown('Edges: `{}`'.format(repr(edges)))
elif option_network == '2D-Grid':
    dim = st.slider('Dimension', min_value=1.0, max_value=10.0, value=5.0, step=1.0, key='2d_dim')
    dim = int(dim)
    G = nx.grid_2d_graph(dim, dim)
    edges = list(G.edges)
    st.markdown('Edges: `{}`'.format(repr(edges)))
elif option_network == 'Geometric':
    nodenum = st.slider('Node-Num', min_value=1.0, max_value=300.0, value=200.0, step=1.0, key='nodenum')
    density = st.slider('Density', min_value=0.01, max_value=0.5, value=0.125, key='density')
    nodenum = int(nodenum)
    G = nx.random_geometric_graph(nodenum, density, seed=42)
    edges = list(G.edges)
    pos = {i: G.nodes[i]['pos'] for i in G.nodes()}
    st.markdown('Edges: `{}`'.format(repr(edges)))
else:
    edgelist_text = (
    [(0, 4), (0, 1), (1, 5), (1, 2), (2, 6), (2, 3), (3, 7), (4, 8), (4, 5), (5, 9), (5, 6), (6, 10), (6, 7), (7, 11),
     (8, 12), (8, 9), (9, 13), (9, 10), (10, 14), (10, 11), (11, 15), (12, 13), (13, 14), (14, 15)])
    edgelist_text = [repr(e) for e in edgelist_text]
    edgelist_text = ','.join(edgelist_text)
    network_text = st.text_area("Enter contact networks as edgelist:", value=edgelist_text)

    # network eval
    network_eval = eval('[' + network_text + ' ]')
    G = nx.from_edgelist(network_eval)

G = nx.convert_node_labels_to_integers(G)

# write graph info
st.write(str(nx.info(G)))
if G.number_of_nodes() < 251:
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    # ax.scatter([1,2,3],[1,2,3])
    if pos is None:
        pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos=pos, node_color='black', edgelist=list(), alpha=0.5, linewidths=0.0)
    nx.draw(G, pos=pos, node_color='black', nodelist=list())
    st.write(fig, width=0.5)

'''
## Initial State
'''

# eval


# st.write(str(G.nodes))
node_num = G.number_of_nodes()

states_slider = dict()
for s in states_eval:
    x = st.slider('Init Number ' + str(s), min_value=0.0, max_value=float(node_num), value=1.0, step=1.0,
                  key='init_' + str(s) + str(node_num))
    states_slider[s] = x

slider_sum = np.sum(list(states_slider.values()))
states_slider_normal = dict()
for s, v in states_slider.items():
    states_slider_normal[s] = int(v / slider_sum * G.number_of_nodes())
slider_sum_normal = np.sum(list(states_slider_normal.values()))
s0 = states_eval[0]
slider_sum_normal_expects1 = slider_sum_normal - states_slider_normal[s0]
states_slider_normal[s0] = int(G.number_of_nodes() - slider_sum_normal_expects1)

'''
## Run Simulation
'''
horizon_slider = st.slider('Horizon', min_value=1.0, max_value=200.0, value=20.0, key='H')

click_run = st.button('Run Simulation')

click_gif = False
if 'click_gif' in st.session_state:
    click_gif = st.session_state.click_gif

if click_run or 'chart_data' in st.session_state or click_gif:
    if click_run:
        chart_data, label_data = run_simulation(G, states_eval, rules_eval, states_slider_normal, horizon_slider)
        st.session_state['chart_data'] = chart_data  # Dictionary like API
        st.session_state['horizon'] = horizon_slider
        st.session_state['label_data'] = label_data
        st.session_state['graph'] = G
        st.session_state['pos'] = pos
        st.session_state['click_gif'] = False
    else:
        chart_data = st.session_state['chart_data']
        label_data = st.session_state['label_data']
        G = st.session_state['graph']
        pos = st.session_state['pos']
    # st.write(str(states_eval))
    # st.write(str(G.nodes))
    # st.write(str(G.edges))
    # st.write(str(rules_eval))
    # st.write(repr(states_slider))
    # st.write(slider_sum)
    st.line_chart(chart_data)
    # st.write(repr(states_slider_normal))
    # st.write(horizon_slider)
    if 'ct_value' in st.session_state:
        ct_value = st.session_state.ct_value
    else:
        ct_value = 0.0
    current_time_slider = st.slider('Timepoint', min_value=0.0, max_value=st.session_state['horizon'], value=0.0,
                                    step=0.1, key='current_time')
    st.session_state['ct_value'] = current_time_slider

    chart_data_filtered = chart_data.reset_index()
    chart_data_filtered['simple_count'] = list(range(len(chart_data_filtered['time'])))
    # st.write(chart_data_filtered.head(30))
    # st.write(current_time_slider)
    chart_data_filtered = chart_data_filtered[chart_data_filtered.time <= float(current_time_slider)]

    current_row = chart_data_filtered.tail(1)
    # st.write(current_row)
    cuttent_df_id = int(current_row['simple_count'])
    current_labels = label_data[cuttent_df_id]
    # st.write(current_labels)
    current_labels_dict = {n: current_labels[n] for n in range(len(current_labels))}

    if G.number_of_nodes() < 251:
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        colordict = colors()#{'S': 'yellow', 'I': 'red', 'R': 'green'}
        colorlist = [colordict.get(l, 'black') for l in current_labels]
        nx.draw(G, pos=pos, edgelist=list(), alpha=1.0, linewidths=0.0, labels=current_labels_dict, font_color='gray',
                node_color=colorlist)
        nx.draw(G, pos=pos, node_color='black', nodelist=list())
        st.write(fig, width=0.5)

    click_gif = st.button('Create Gif', key='creategif')
    if click_gif:
        import os, imageio, glob

        os.system('rm -rf imagedata')
        os.system('mkdir imagedata')
        node_size = 1.0 / G.number_of_nodes() * 200 * 70

        for i, current_labels in enumerate(label_data):
            plt.close()
            plt.clf()
            fig = plt.figure()
            ax = fig.add_subplot(1, 1, 1)
            colordict = colors()  # {'S': 'yellow', 'I': 'red', 'R': 'green'}
            colorlist = [colordict.get(l, 'black') for l in current_labels]
            nx.draw(G, pos=pos, edgelist=list(), alpha=0.8, linewidths=0.0,  # labels=current_labels_dict,
                    font_color='gray', node_color=colorlist, node_size=node_size, width=0.8)
            nx.draw(G, pos=pos, edge_color='black', nodelist=list(), alpha=0.5)
            plt.savefig('imagedata/labels_' + str(i).zfill(7) + '.png')
            with imageio.get_writer('movie.gif', mode='I', fps=2.0) as writer:
                for filename in sorted(glob.glob('imagedata/*.png')):
                    image = imageio.imread(filename)
                    writer.append_data(image)

        # st.markdown("![Alt Text](./movie.gif)")
        st.image("movie.gif")

    #
# st.graphviz_chart('''
#     graph {
#         run -- intr
#         intr -- runbl
#         runbl -- run
#     }
# ''')
#
# #import pygraphviz
# #from networkx.drawing.nx_agraph import write_dot
# #write_dot(G, "grid.dot")
#
#
#
# import streamlit as st
# fig = plt.figure()
# ax = fig.add_subplot(1,1,1)
# plt.scatter([1,2,3],[1,2,3])
# st.write(fig)
