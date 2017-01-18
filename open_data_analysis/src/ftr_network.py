# coding=utf-8
import snap
import pandas as pd
import geopandas as gp


def ftr_network_SgAsNd(path_segs, path_ftr_seg_as_node, directionality_column=None, is_dird=False):
    from constants import index_seg
    from geom_helper import intxn_from_segs
    print '----segments as nodes network----'
    intxn_matrix = intxn_from_segs(path_segs, directionality_column=directionality_column)
    print 'got intxn_matrix'
    edges = intxn_matrix.values
    nodes = pd.unique(edges.flatten())
    features_SgAsNd = ftr_segs_as_nodes(nodes, edges, is_dird)
    print 'got ftr sgasnd'
    df_ftr = pd.DataFrame.from_dict(features_SgAsNd).T
    df_ftr.index.name = index_seg
    df_ftr.to_csv(path_ftr_seg_as_node)


def ftr_for_dc(path_intxn, path_segs, path_ftr_seg_as_node):
    from constants import index_seg
    gpdf_segs = gp.read_file(path_segs)
    df_intxn = pd.read_csv(path_intxn)
    edges = df_intxn[['STREET1SEGID','STREET2SEGID']].values
    nodes = pd.unique(edges.flatten())
    features = ftr_segs_as_nodes(nodes, edges, True)
    df_ftr = pd.DataFrame.from_dict(features).T
    df_ftr.index.name = 'STREETSEGID'
    df = gpdf_segs[['STREETSEGID']].reset_index().merge(df_ftr.reset_index())
    df.columns = [index_seg] + list(df.columns[1:])
    df.to_csv(path_ftr_seg_as_node)
    return df


def ftr_segs_as_nodes(nodes, edges, is_dird=False):
    # TODO: modify the feature name and function name, add SgAsNd
    # TODO: reconsider the function name, because processs of building network of SgAsNd and SgAsEg is quite different

    from collections import defaultdict
    nodes_size = len(nodes)
    G = snap.TNGraph.New()
    for n in nodes:
        G.AddNode(int(n))
    for ein, eout in edges:
        G.AddEdge(int(ein), int(eout))
    UG = snap.ConvertGraph(snap.PUNGraph, G)
    print 'node size = {}, directed edges = {}, undirected edges = {}'.format(nodes_size, len([0 for e in G.Edges()]), len([0 for e in UG.Edges()]))
    features = defaultdict(lambda: defaultdict(int))
    if is_dird:
        ftr_directed(G, features, nodes_size)
        print 'got ftr directed'
    ftr_undirected(UG, features)
    print 'got ftr undirected'
    return features


def ftr_directed(G, features, nodes_size):

    for NI in G.Nodes():
        nid = NI.GetId()
        features[nid]['d_in_deg'] = float(NI.GetInDeg())/(nodes_size-1)
        features[nid]['d_out_deg'] = float(NI.GetOutDeg())/(nodes_size-1)
        features[nid]['d_node_ecc'] = snap.GetNodeEcc(G, nid, True)
        features[nid]['d_clo_cntr'] = snap.GetClosenessCentr(G, nid, True, True)
        features[nid]['d_far_cntr'] = snap.GetFarnessCentr(G, nid, True, True)
    print 'a'
    Nodes = snap.TIntFltH()
    Edges = snap.TIntPrFltH()
    snap.GetBetweennessCentr(G, Nodes, Edges, 1.0, True)
    for nid in Nodes:
        features[nid]['d_btw_cntr'] = Nodes[nid]
    print 'between'
    PRankH = snap.TIntFltH()
    snap.GetPageRank(G, PRankH)
    for nid in PRankH:
        features[nid]['d_page_rank'] = PRankH[nid]
    print 'page'
    NIdHubH = snap.TIntFltH()
    NIdAuthH = snap.TIntFltH()
    snap.GetHits(G, NIdHubH, NIdAuthH)
    for nid in NIdHubH:
        features[nid]['d_hub_score'] = NIdHubH[nid]
    for nid in NIdAuthH:
        features[nid]['d_auth_score'] = NIdAuthH[nid]
    print 'his'

def ftr_undirected(UG, features):
    for NI in UG.Nodes():
        nid = NI.GetId()
        features[nid]['ud_deg_cntr'] = snap.GetDegreeCentr(UG, nid)
        features[nid]['ud_node_ecc'] = snap.GetNodeEcc(UG, nid, False)
        features[nid]['ud_clo_cntr'] = snap.GetClosenessCentr(UG, nid, True, False)
        features[nid]['ud_far_cntr'] = snap.GetFarnessCentr(UG, nid, True, False)
    print 'nodes'
    NIdEigenH = snap.TIntFltH()
    snap.GetEigenVectorCentr(UG, NIdEigenH)
    for nid in NIdEigenH:
        features[nid]['ud_eig_cntr'] = NIdEigenH[nid]
    print 'eigen'
    Nodes = snap.TIntFltH()
    Edges = snap.TIntPrFltH()
    snap.GetBetweennessCentr(UG, Nodes, Edges, 1.0, False)
    for nid in Nodes:
        features[nid]['ud_btw_cntr'] = Nodes[nid]
    print 'btw'
    PRankH = snap.TIntFltH()
    snap.GetPageRank(UG, PRankH)
    for nid in PRankH:
        features[nid]['ud_page_rank'] = PRankH[nid]
    print 'page ud'
    NIdHubH = snap.TIntFltH()
    NIdAuthH = snap.TIntFltH()
    snap.GetHits(UG, NIdHubH, NIdAuthH)
    for nid in NIdHubH:
        features[nid]['ud_hub_score'] = NIdHubH[nid]
    for nid in NIdAuthH:
        features[nid]['ud_auth_score'] = NIdAuthH[nid]
    print 'hit ud'
    ArtNIdV = snap.TIntV()
    snap.GetArtPoints(UG, ArtNIdV)
    for nid in ArtNIdV:
        features[nid]['ud_art_pt']=1
    print 'artpoint'
    EdgeV = snap.TIntPrV()
    snap.GetEdgeBridges(UG, EdgeV)
    for edge in EdgeV:
        features[edge.GetVal1()]['ud_bridge']+=1
        features[edge.GetVal2()]['ud_bridge']+=1

