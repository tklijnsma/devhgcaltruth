import numpy as np
import devhgcaltruth as ht

def plotly_tree(tree, colorwheel=None, noinfo=False, draw_tracks=True):
    import plotly.graph_objects as go
    data = []
    info = {}
    if colorwheel is None: colorwheel = ht.IDColor()

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

    for track in sorted(filter(lambda t: t.nhits>0, tree.traverse()), key=lambda t: -t.nhits):
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
                'x: %{{y:0.2f}}<br>y: %{{z:0.2f}}<br>z: %{{x:0.2f}}<br>pdgId: {}<br>'
                .format(track.pdgid)
                ),
            name=str(int(track.trackid)),
            legendgroup=str(int(track.trackid))
            ))

        if draw_tracks:
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
                legendgroup=str(int(track.trackid)),
                showlegend=False
                ))
    
    return data if noinfo else (data, info)


def side_by_side_trees(tree1, tree2, colorwheel=None, **kwargs):
    if colorwheel is None: colorwheel = ht.IDColor()
    data1, info1 = ht.plotly.plotly_tree(tree1, colorwheel=colorwheel)
    data2 = ht.plotly.plotly_tree(tree2, colorwheel=colorwheel, noinfo=True)
    return side_by_side_html(data1, data2, info1, **kwargs)



def single_html(data, info=None, title=None, width=600, height=None, include_plotlyjs='cdn'):
    import plotly.graph_objects as go
    if height is None: height = width
    scene = dict(
        xaxis_title='z', yaxis_title='x', zaxis_title='y',
        aspectmode='cube'
        )
    if info:
        scene.update(dict(
            xaxis_range=[320., info['zmax']],
            yaxis_range=[info['xmin'], info['xmax']],
            zaxis_range=[info['ymin'], info['ymax']],
            ))
    fig = go.Figure(data=data, **(dict(layout_title_text=title) if title else {}))
    fig.update_layout(width=width, height=height, scene=scene)
    fig_html = fig.to_html(full_html=False, include_plotlyjs=include_plotlyjs)
    return fig_html


def side_by_side_html(data1, data2, info=None, title1=None, title2=None, width=600, height=None, include_plotlyjs='cdn'):
    import plotly.graph_objects as go

    scene = dict(
        xaxis_title='z', yaxis_title='x', zaxis_title='y',
        aspectmode='cube'
        )
    if info:
        scene.update(dict(
            xaxis_range=[320., info['zmax']],
            yaxis_range=[info['xmin'], info['xmax']],
            zaxis_range=[info['ymin'], info['ymax']],
            ))

    if height is None: height = width
    fig1 = go.Figure(data=data1, **(dict(layout_title_text=title1) if title1 else {}))
    fig1.update_layout(width=width, height=height, scene=scene)

    fig2 = go.Figure(data=data2, **(dict(layout_title_text=title2) if title2 else {}))
    fig2.update_layout(width=width, height=height, scene=scene)

    fig1_html = fig1.to_html(full_html=False, include_plotlyjs=include_plotlyjs)
    fig2_html = fig2.to_html(full_html=False, include_plotlyjs=False)

    id1 = fig1_html.split('<div id="',1)[1].split('"',1)[0]
    id2 = fig2_html.split('<div id="',1)[1].split('"',1)[0]

    html = (
        f'<div style="width: 47%; display: inline-block">\n{fig1_html}\n</div>'
        f'\n<div style="width: 47%; display: inline-block">\n{fig2_html}\n</div>'
        +
        '\n<script>'
        +
        f'\nvar graphdiv1 = document.getElementById("{id1}");'
        f'\nvar graphdiv2 = document.getElementById("{id2}");'
        +
        '\nvar isUnderRelayout1 = false'
        '\ngraphdiv1.on("plotly_relayout", () => {'
        '\n    // console.log("relayout", isUnderRelayout1)'
        '\n    if (!isUnderRelayout1) {'
        '\n        Plotly.relayout(graphdiv2, {"scene.camera": graphdiv1.layout.scene.camera})'
        '\n        .then(() => { isUnderRelayout1 = false }  )'
        '\n        }'
        '\n    isUnderRelayout1 = true;'
        '\n    })'
        '\nvar isUnderRelayout2 = false'
        '\ngraphdiv2.on("plotly_relayout", () => {'
        '\n    // console.log("relayout", isUnderRelayout2)'
        '\n    if (!isUnderRelayout2) {'
        '\n        Plotly.relayout(graphdiv1, {"scene.camera": graphdiv2.layout.scene.camera})'
        '\n        .then(() => { isUnderRelayout2 = false }  )'
        '\n        }'
        '\n    isUnderRelayout2 = true;'
        '\n    })'
        '\n</script>'
        )
    return html

JS_LINK_LEGENDS = r"""
function isTrack(entry){
    return /^\d+$/.test(entry["name"])
    }

graphdiv2.on("plotly_restyle", () => {
    console.log('Restyling based on legend click')
    if (graphdiv2.data.every(entry => entry["visible"] === true)){
        // Shortcut if everything is on
        console.log("Detected everything turned on")
        Plotly.restyle(graphdiv1, {'visible' : true}, [...Array(graphdiv1.data.length).keys()])
        .then(() => {isUnderRestyle2 = false})
        }
    else{
        let visibleTracksIn2 = new Set(
            graphdiv2.data
            .filter(entry => isTrack(entry) && (entry["visible"] === true || !("visible" in entry)))
            .map(entry => entry["name"])
            )
        console.log(visibleTracksIn2)

        let visibleTracksIn1 = new Set()
        visibleTracksIn2.forEach(trackid => {
            mergemap[trackid].forEach(merged_trackid => visibleTracksIn1.add(merged_trackid))
            })
        console.log(visibleTracksIn1)

        updateIndicesVisible = []
        updateIndicesInvisible = []
        for (var i = 0; i < graphdiv1.data.length; i++) {
            let entry = graphdiv1.data[i]
            if (!isTrack(entry)){ continue }
            let name = entry["name"]
            if (visibleTracksIn1.has(name)){
                updateIndicesVisible.push(i)
                }
            else {
                updateIndicesInvisible.push(i)
                }
            }

        // console.log(updateIndicesVisible)
        // console.log(updateIndicesInvisible)

        Plotly.restyle(graphdiv1, {'visible' : true}, updateIndicesVisible)
        if (updateIndicesInvisible.length > 0){
            Plotly.restyle(graphdiv1, {'visible' : "legendonly"}, updateIndicesInvisible)
            }
        }
    })
"""

def side_by_side_unmerged_merged(unmerged, merged, outfile=None, **kwargs):
    kwargs.setdefault('title1', 'Unmerged')
    kwargs.setdefault('title2', 'Merged')
    html = side_by_side_trees(unmerged, merged, **kwargs)
    html = html.rsplit('\n',1)[0] # Split off last /script tag so more stuff can be added
    html += '\n' + parse_js_mergemap(merged) + '\n\n'
    html += JS_LINK_LEGENDS
    html += '\n</script>'
    if outfile:
        import os, os.path as osp
        outdir = osp.dirname(osp.abspath(outfile))
        if not osp.isdir(outdir): os.makedirs(outdir)
        with open(outfile, 'w') as f:
            f.write(html)
    return html



def parse_js_mergemap(tree, js_varname='mergemap'):
    js = ['var mergemap = {']
    for track in tree.children:
        js.append(
            '"{}" : {},'
            .format(
                track.trackid,
                '[' + ','.join('"'+str(int(t.trackid))+'"' for t in track.merged_tracks) + ']'
                )
            )
    js.append('}')
    return '\n    '.join(js)


def write_html(outfile, html):
    import os, os.path as osp
    outdir = osp.dirname(osp.abspath(outfile))
    if not osp.isdir(outdir): os.makedirs(outdir)
    with open(outfile, 'w') as f:
        f.write(html)
