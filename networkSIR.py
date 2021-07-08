import streamlit as st
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
import numpy as np
import pandas as pd
from simulation import *
import matplotlib.pyplot as plt

"""
# Network Epidemic Simulator
Continuous-time stochastic simulation of epidemic spreading on human-to-human contact networks:
"""

'''
## Epidemic Model
'''
option_model = st.selectbox('Spreading Model', ('SI model', 'SEIRS model', 'Custom'))

if option_model == 'SI model':
    st.markdown(f'States: `S,I`')
    #r1 = st.slider('S->I', min_value=1.0, max_value=200.0, value=20.0)
    r1 = st.slider('I+S->I+I', min_value=0.0, max_value=20.0, value=0.5, key='si_r1')
    states_eval = ["S", "I"]
    rules_eval = [(("I", "S"), ("I", "I"), float(r1))]
elif option_model == 'SEIRS model':
    st.markdown(f'States: `S,E,I,R`')
    #r1 = st.slider('S->I', min_value=1.0, max_value=200.0, value=20.0)
    r1 = st.slider('I+S->I+E', min_value=0.0, max_value=20.0, value=0.5, key='seirs_r1')
    r2 = st.slider('E->I', min_value=0.0, max_value=20.0, value=0.5, key='seirs_r2')
    r3 = st.slider('I->R', min_value=0.0, max_value=20.0, value=0.5, key='seirs_r3')
    r4 = st.slider('R->S', min_value=0.0, max_value=20.0, value=0.5, key='seirs_r4')
    states_eval = ["S", "E", "I", "R"]
    rules_eval = [(("I", "S"), ("I", "I"), float(r1)), ("E", "I", float(r2)),("I", "R", float(r3)),("R", "S", float(r4))]
else:
    states = ["S", "I", "R"]
    rules = [("I", "R", 1.0),  # spontaneous rule  I -> R with rate 1.0
             ("R", "S", 0.7),  # spontaneous rule R -> S with rate 0.7
             (("I", "S"), ("I", "I"), 0.8)]
    rules_text = [repr(r) for r in rules]
    rules_text = '\n'.join(rules_text)
    epidemic_states_text = st.text_input("Enter states/compartments (separated by comma):", value='S,I,R')
    epidemic_model_text = st.text_area("Enter interaction rules (separated by line):", value=rules_text)
    states_eval = eval('"' + epidemic_states_text.replace(',','","')+'"')
    rules_eval = eval('[' + epidemic_model_text.replace('\n',',') + ' ]')

states_eval = sorted(list(set(states_eval)))

'''
## Contact Network
'''
import networkx as nx
option_network = st.selectbox('Contact Network', ('Karate', '2D-Grid', 'Geometric', 'Custom'))

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
    density = st.slider('Node-Num', min_value=0.01, max_value=0.5, value=0.125, key='density')
    nodenum = int(nodenum)
    G = nx.random_geometric_graph(nodenum, density, seed=42)
    edges = list(G.edges)
    st.markdown('Edges: `{}`'.format(repr(edges)))
else:
    edgelist_text = ([(0, 4), (0, 1), (1, 5), (1, 2), (2, 6), (2, 3), (3, 7), (4, 8), (4, 5), (5, 9), (5, 6), (6, 10), (6, 7), (7, 11), (8, 12), (8, 9), (9, 13), (9, 10), (10, 14), (10, 11), (11, 15), (12, 13), (13, 14), (14, 15)])
    edgelist_text = [repr(e) for e in edgelist_text]
    edgelist_text = ','.join(edgelist_text)
    network_text = st.text_area("Enter contact networks as edgelist:", value=edgelist_text)

    # network eval
    network_eval = eval('[' + network_text + ' ]')
    G = nx.from_edgelist(network_eval)

G = nx.convert_node_labels_to_integers(G)

#write graph info
st.write(str(nx.info(G)))
fig = plt.figure()
ax = fig.add_subplot(1,1,1)
#ax.scatter([1,2,3],[1,2,3])
pos = nx.spring_layout(G, seed=42)
nx.draw(G, pos=pos, node_color='black', edgelist=list(), alpha=0.5, linewidths=0.0)
nx.draw(G, pos=pos, node_color='black', nodelist=list())
st.write(fig, width=0.5)

'''
## Initial State
'''

# eval


#st.write(str(G.nodes))
node_num = G.number_of_nodes()


states_slider = dict()
for s in states_eval:
    x = st.slider('Init Number '+str(s), min_value=0.0, max_value=float(node_num), value=1.0,step=1.0, key='init_'+str(s)+str(node_num))
    states_slider[s] = x

slider_sum = np.sum(list(states_slider.values()))
states_slider_normal = dict()
for s, v in states_slider.items():
    states_slider_normal[s] = int(v/slider_sum * G.number_of_nodes())
slider_sum_normal = np.sum(list(states_slider_normal.values()))
s0 = states_eval[0]
slider_sum_normal_expects1 = slider_sum_normal - states_slider_normal[s0]
states_slider_normal[s0] = int(G.number_of_nodes() - slider_sum_normal_expects1)

'''
## Run Simulation
'''
horizon_slider = st.slider('Horizon', min_value=1.0, max_value=200.0, value=20.0, key='H')

click_run = st.button('Run Simulation')



if click_run or 'chart_data' in st.session_state:
    if click_run:
        chart_data, label_data = run_simulation(G, states_eval, rules_eval, states_slider_normal, horizon_slider)
        st.session_state['chart_data'] = chart_data  # Dictionary like API
        st.session_state['horizon'] = horizon_slider
        st.session_state['label_data'] = label_data
        st.session_state['graph'] = G
        st.session_state['pos'] = pos
    else:
        chart_data = st.session_state['chart_data']
        label_data = st.session_state['label_data']
        G = st.session_state['graph']
        pos = st.session_state['pos']
    #st.write(str(states_eval))
    #st.write(str(G.nodes))
    #st.write(str(G.edges))
    #st.write(str(rules_eval))
    #st.write(repr(states_slider))
    #st.write(slider_sum)
    st.line_chart(chart_data)
    #st.write(repr(states_slider_normal))
    #st.write(horizon_slider)
    if 'ct_value' in st.session_state:
        ct_value = st.session_state.ct_value
    else:
        ct_value = 0.0
    current_time_slider = st.slider('Timepoint', min_value=0.0, max_value=st.session_state['horizon'], value=0.0, step=0.1, key='current_time')
    st.session_state['ct_value'] = current_time_slider


    chart_data_filtered = chart_data.reset_index()
    chart_data_filtered['simple_count'] = list(range(len(chart_data_filtered['time'])))
    #st.write(chart_data_filtered.head(30))
    #st.write(current_time_slider)
    chart_data_filtered = chart_data_filtered[chart_data_filtered.time <= float(current_time_slider)]

    current_row = chart_data_filtered.tail(1)
    #st.write(current_row)
    cuttent_df_id = int(current_row['simple_count'])
    current_labels = label_data[cuttent_df_id]
    #st.write(current_labels)
    current_labels_dict = {n: current_labels[n] for n in range(len(current_labels))}

    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    colordict = {'S': 'yellow', 'I':'red', 'R':'green'}
    colorlist = [colordict.get(l, 'black') for l in current_labels]
    nx.draw(G, pos=pos, edgelist=list(), alpha=1.0, linewidths=0.0, labels=current_labels_dict, font_color='gray', node_color = colorlist)
    nx.draw(G, pos=pos, node_color='black', nodelist=list())
    st.write(fig, width=0.5)


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
