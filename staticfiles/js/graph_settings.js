const options = {
    layout: {
        hierarchical: {
            enabled: true,
            direction: 'LR',
            sortMethod: 'directed',
            levelSeparation: 250,
            nodeSpacing: 200,
            treeSpacing: 250,
            edgeMinimization: true,
            blockShifting: true
        }
    },
    nodes: {
        shape: 'dot',
        size: 28,
        font: {
            size: 18,
            color: '#23272f',
            face: 'Inter, Segoe UI, Arial',
            bold: {
                color: '#23272f',
                size: 20,
                face: 'Inter, Segoe UI, Arial',
                mod: 'bold'
            }
        },
        borderWidth: 2
    },
    groups: {
        current: {
            color: {
                border: '#23272f',
                background: '#ffd166',
                highlight: {
                    border: '#23272f',
                    background: '#ffe29a'
                }
            }
        },
        blockers: {
            color: {
                border: '#ef476f',
                background: '#ffe5eb',
                highlight: {
                    border: '#ef476f',
                    background: '#ffc4d2'
                }
            }
        },
        blocked: {
            color: {
                border: '#118ab2',
                background: '#e0f7ff',
                highlight: {
                    border: '#118ab2',
                    background: '#b3ecff'
                }
            }
        },
        related: {
            color: {
                border: '#6c63ff',
                background: '#f5f6fa',
                highlight: {
                    border: '#6c63ff',
                    background: '#e0e7ff'
                }
            }
        }
    },
    edges: {
        color: {
            color: '#bdbdbd',
            highlight: '#6c63ff',
            hover: '#23272f',
            inherit: false
        },
        width: 2,
        smooth: false,
        arrows: {
            to: { enabled: true, scaleFactor: 1.2 }
        }
    },
    interaction: { hover: true },
    physics: false
};

const container = document.getElementById('graph');
const network = new vis.Network(container, graphData, options);

network.on("click", function (params) {
    if (params.nodes.length > 0) {
        const nodeId = params.nodes[0];
        const node = graphData.nodes.find(n => n.id === nodeId);
        if (node && node.url) {
            window.location.href = node.url;
        }
    }
});
