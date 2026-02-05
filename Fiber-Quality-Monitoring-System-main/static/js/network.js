// Network Visualization using vis.js
document.addEventListener('DOMContentLoaded', function() {
    // Initialize network container
    const container = document.getElementById('network-container');
    
    // Sample initial nodes and edges
    let nodes = new vis.DataSet([]);
    let edges = new vis.DataSet([]);

    // Network configuration
    const options = {
        nodes: {
            shape: 'dot',
            size: 30,
            font: {
                size: 14
            },
            borderWidth: 2,
            shadow: true
        },
        edges: {
            width: 2,
            smooth: {
                type: 'continuous'
            }
        },
        physics: {
            stabilization: true,
            barnesHut: {
                gravitationalConstant: -2000,
                springLength: 200
            }
        },
        interaction: {
            hover: true
        }
    };

    // Create network
    const network = new vis.Network(container, { nodes, edges }, options);

    // WebSocket handling
    const socket = io();

    // Handle network updates
    socket.on('network_update', function(data) {
        const newNodes = [];
        const newEdges = [];

        // Convert server data to vis.js format
        Object.entries(data).forEach(([name, nodeData]) => {
            newNodes.push({
                id: name,
                label: name,
                color: getNodeColor(nodeData.status),
                title: `
                    Status: ${nodeData.status}
                    Power: ${nodeData.power.toFixed(1)}dBm
                    Latency: ${nodeData.latency.toFixed(1)}ms
                `
            });

            // Create connections
            if (name === 'Nairobi') {
                newEdges.push({ from: 'Nairobi', to: 'Mombasa' });
                newEdges.push({ from: 'Nairobi', to: 'Kisumu' });
            }
        });

        nodes.update(newNodes);
        edges.update(newEdges);
    });

    // Node color based on status
    function getNodeColor(status) {
        return {
            background: status === 'online' ? '#4CAF50' : '#F44336',
            border: status === 'online' ? '#388E3C' : '#D32F2F',
            highlight: {
                background: status === 'online' ? '#81C784' : '#EF9A9A',
                border: status === 'online' ? '#4CAF50' : '#F44336'
            }
        };
    }

    // Double-click handler
    network.on('doubleClick', function(params) {
        if (params.nodes.length) {
            const nodeId = params.nodes[0];
            socket.emit('manual_trigger', {
                type: 'status_check',
                node: nodeId
            });
        }
    });
});
