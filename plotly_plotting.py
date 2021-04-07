import numpy as np
from . import hgcalntuptool

def plotly_tree(tree, colorwheel=None):
    import plotly.graph_objects as go
    data = []
    info = {}
    if colorwheel is None: colorwheel = hgcalntuptool.IDColor()

    all_hits = tree.nphits_recursively()
    all_energy = all_hits[:,3]
    energy_scale = 20./np.average(all_energy)
    
    xmin=np.min(all_hits[:,0])
    xmax=np.max(all_hits[:,0])
    ymin=np.min(all_hits[:,1])
    ymax=np.max(all_hits[:,1])
    zmin=np.min(all_hits[:,2])
    zmax=np.max(all_hits[:,2])
    info = {
        'xmin' : xmin, 'xmax' : xmax,
        'ymin' : ymin, 'ymax' : ymax,
        'zmin' : zmin, 'zmax' : zmax,
        }

    # Draw HGCAL front face
    data.append(go.Scatter3d(
        x=[320.5 for i in range(4)], y=[xmin, xmax, xmax, xmin], z=[ymin, ymin, ymax, ymax],
        mode='lines',
        surfaceaxis=0,
        line=dict(color='#bacfbe'),
        opacity=0.25,
        name='HGCAL front',
        hoverinfo='skip',
        ))

    info['n_tracks_with_hits'] = 0
    for track in tree.traverse():
        if track.nhits == 0: continue
        info['n_tracks_with_hits'] += 1

        # First draw hits
        hits = track.nphits()
        energy = hits[:,3]            
        sizes = np.maximum(0., np.minimum(3., np.log(energy_scale*energy)))

        data.append(go.Scatter3d(
            x=hits[:,2], y=hits[:,0], z=hits[:,1],
            mode='markers', 
            marker=dict(
                line=dict(width=0),
                size=sizes,
                color=colorwheel(int(track.trackid)),
                ),
            hovertemplate=(
                'x: %{{z:0.2f}}<br>y: %{{x:0.2f}}<br>z: %{{y:0.2f}}<br>pdgId: {}<br>'
                .format(track.pdgid)
                ),
            name=str(int(track.trackid)), 
            ))

        # Second, draw track from boundary crossing to hit centroid
        bpos = track.average_boundary_pos()
        data.append(go.Scatter3d(
            x=[bpos[2], track.centroid[2]], y=[bpos[0], track.centroid[0]], z=[bpos[1], track.centroid[1]],
            mode='lines+markers',
            marker=dict(
                size=[4, 10],
                symbol=['x', 'diamond']
                ),
            line=dict(
                width=3,
                color=colorwheel(int(track.trackid)),
                ),
            hovertemplate=(
                'x: %{{y:.2f}}<br>y: %{{z:.2f}}<br>z: %{{x:.2f}}<br>E: {energy:.2f} GeV<br>pdgid: {pdgid}<br>nhits: {nhits}<br>'
                .format(
                    energy = track.energyAtBoundary, pdgid = track.pdgid,
                    nhits = track.nhits
                    )
                ),
            name=str(int(track.trackid)), 
            ))
        
    return data, info


