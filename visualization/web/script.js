// TileScope Visualization JavaScript

class TileScopeVisualizer {
    constructor() {
        this.data = null;
        this.selectedNode = null;
        this.treeData = null;
        this.svg = null;
        this.tooltip = null;
        this.currentZoomTransform = null;

        this.initializeElements();
        this.setupEventListeners();
        this.createTooltip();
    }

    initializeElements() {
        this.elements = {
            startRealtimeBtn: document.getElementById('start-realtime'),
            pauseResumeBtn: document.getElementById('pause-resume'),
            stopServerBtn: document.getElementById('stop-server'),
            nodesCount: document.getElementById('nodes-count'),
            strategiesCount: document.getElementById('strategies-count'),
            maxDepth: document.getElementById('max-depth'),
            nodeDetails: document.getElementById('node-details'),
            tilingDisplay: document.getElementById('tiling-display'),
            specDisplay: document.getElementById('spec-display'),
            statusMessage: document.getElementById('status-message'),
            loadingIndicator: document.getElementById('loading-indicator'),
            treeSvg: document.getElementById('tree-svg'),
            timelineSvg: document.getElementById('timeline-svg')
        };
    }

    setupEventListeners() {

        // Real-time search
        this.elements.startRealtimeBtn.addEventListener('click', () => {
            this.startRealtimeSearch();
        });

        // Pause/Resume
        this.elements.pauseResumeBtn.addEventListener('click', () => {
            this.togglePauseResume();
        });

        this.elements.stopServerBtn.addEventListener('click', () => {
            this.stopServer();
        });

        // Tab switching
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });
    }

    createTooltip() {
        this.tooltip = d3.select('body')
            .append('div')
            .attr('class', 'tooltip')
            .style('opacity', 0);
    }

    showLoading(message = 'Loading...') {
        this.elements.statusMessage.textContent = message;
        this.elements.loadingIndicator.style.display = 'flex';
    }

    hideLoading() {
        this.elements.loadingIndicator.style.display = 'none';
    }

    updateStatus(message) {
        this.elements.statusMessage.textContent = message;
    }


    // Try to load default data on startup
    async loadDefaultData() {
        try {
            this.showLoading('Loading default visualization data...');
            const response = await fetch('/api/data');
            if (response.ok) {
                const data = await response.json();
                this.loadData(data);
                this.updateStatus('Default data loaded successfully');
            } else {
                this.updateStatus('No default data available - use "Load Data" to load a file');
            }
        } catch (error) {
            console.log('No default data available:', error);
            this.updateStatus('Ready - use "Load Data" to load visualization data');
        }
        this.hideLoading();
    }

    loadData(data) {
        this.data = data;
        this.updateStats();
        this.prepareTreeData();
        this.renderSearchTree();
        this.renderSpecification();
        this.renderTimeline();
        this.updateStatus('Visualization ready');
    }

    updateStats() {
        if (!this.data) return;

        this.elements.nodesCount.textContent = Object.keys(this.data.nodes).length;
        this.elements.strategiesCount.textContent = this.data.strategies_applied.length;

        const maxDepth = Math.max(...Object.values(this.data.nodes).map(n => n.level));
        this.elements.maxDepth.textContent = maxDepth;
    }

    prepareTreeData() {
        if (!this.data) return;

        // Convert flat node structure to hierarchical tree
        const nodes = this.data.nodes;
        const nodeMap = new Map();

        // Create node map
        Object.values(nodes).forEach(node => {
            nodeMap.set(node.id, {
                ...node,
                children: []
            });
        });

        // Build tree structure
        const root = nodeMap.get(0); // Root node should have id 0
        nodeMap.forEach(node => {
            if (node.parent_id !== null && nodeMap.has(node.parent_id)) {
                nodeMap.get(node.parent_id).children.push(node);
            }
        });

        this.treeData = root;
    }

    renderSearchTree() {
        if (!this.treeData) return;

        const container = this.elements.treeSvg;
        const containerRect = container.getBoundingClientRect();
        const width = containerRect.width || 800;
        const height = containerRect.height || 600;

        // Clear previous content
        d3.select(container).selectAll('*').remove();

        const svg = d3.select(container)
            .attr('width', width)
            .attr('height', height);

        const g = svg.append('g')
            .attr('transform', 'translate(50,50)');

        // Create tree layout (vertical: top to bottom)
        const tree = d3.tree()
            .size([width - 100, height - 100]);

        const root = d3.hierarchy(this.treeData);
        tree(root);

        // Add links (vertical layout)
        g.selectAll('.link')
            .data(root.links())
            .enter()
            .append('path')
            .attr('class', 'link')
            .attr('d', d3.linkVertical()
                .x(d => d.x)
                .y(d => d.y));

        // Add nodes (swapped x and y for vertical layout)
        const node = g.selectAll('.node')
            .data(root.descendants())
            .enter()
            .append('g')
            .attr('class', d => {
                let classes = 'node';
                if (d.data.is_root) classes += ' root';
                if (d.data.is_verified) classes += ' verified';
                if (d.data.is_expanded) classes += ' expanded';
                if (d.data.used_in_specification) classes += ' specification';
                return classes;
            })
            .attr('transform', d => `translate(${d.x},${d.y})`)
            .on('click', (event, d) => this.selectNode(d.data))
            .on('mouseover', (event, d) => this.showNodeTooltip(event, d.data))
            .on('mouseout', () => this.hideTooltip());

        node.append('circle')
            .attr('r', 8);

        node.append('text')
            .attr('dy', '0.31em')
            .attr('x', d => d.children ? 0 : 0)
            .attr('y', d => d.children ? -16 : 16)
            .style('text-anchor', 'middle')
            .text(d => `Node ${d.data.id}`);

        // Add zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 3])
            .on('zoom', (event) => {
                this.currentZoomTransform = event.transform;
                g.attr('transform', event.transform);
            });

        svg.call(zoom);

        // Restore previous zoom state if it exists
        if (this.currentZoomTransform) {
            svg.call(zoom.transform, this.currentZoomTransform);
        }
    }

    selectNode(nodeData) {
        this.selectedNode = nodeData;
        this.updateNodeDetails();
        this.updateTilingDisplay();

        // Highlight selected node
        d3.selectAll('.node').classed('selected', false);
        d3.selectAll('.node').filter(d => d.data.id === nodeData.id)
            .classed('selected', true);
    }

    updateNodeDetails() {
        if (!this.selectedNode) {
            this.elements.nodeDetails.innerHTML = '<p>Select a node to view details</p>';
            return;
        }

        const node = this.selectedNode;
        const html = `
            <div class="detail-item">
                <div class="detail-label">Node ID:</div>
                <div>${node.id}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Level:</div>
                <div>${node.level}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Strategy Applied:</div>
                <div>${node.strategy_applied || 'None'}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Status:</div>
                <div>${this.getNodeStatus(node)}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Timestamp:</div>
                <div>${node.timestamp.toFixed(3)}s</div>
            </div>
        `;

        this.elements.nodeDetails.innerHTML = html;
    }

    getNodeStatus(node) {
        if (node.is_root) return 'Root';
        if (node.is_verified) return 'Verified';
        if (node.is_expanded) return 'Expanded';
        return 'Active';
    }

    updateTilingDisplay() {
        if (!this.selectedNode) {
            this.elements.tilingDisplay.innerHTML = '<p>No tiling selected</p>';
            return;
        }

        const tiling = this.selectedNode.tiling;
        const html = `
            <div class="tiling-grid">${tiling.ascii_repr}</div>
            <div style="margin-top: 1rem;">
                <strong>Dimensions:</strong> ${tiling.dimensions[0]} × ${tiling.dimensions[1]}<br>
                <strong>Obstructions:</strong> ${tiling.obstructions.length}<br>
                <strong>Requirements:</strong> ${tiling.requirements.length}<br>
                <strong>Active Cells:</strong> ${tiling.active_cells.length}
            </div>
        `;

        this.elements.tilingDisplay.innerHTML = html;
    }

    renderSpecification() {
        if (!this.data || !this.data.final_specification) {
            this.elements.specDisplay.innerHTML = 'No specification data available';
            return;
        }

        const spec = this.data.final_specification;
        this.elements.specDisplay.innerHTML = `<pre>${spec.rules}</pre>`;
    }

    renderTimeline() {
        if (!this.data) return;

        const container = this.elements.timelineSvg;
        const containerRect = container.getBoundingClientRect();
        const width = containerRect.width || 800;
        const height = containerRect.height || 200;

        // Clear previous content
        d3.select(container).selectAll('*').remove();

        const svg = d3.select(container)
            .attr('width', width)
            .attr('height', height);

        const margin = { top: 20, right: 30, bottom: 40, left: 50 };
        const innerWidth = width - margin.left - margin.right;
        const innerHeight = height - margin.top - margin.bottom;

        const g = svg.append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);

        // Prepare timeline data
        const events = this.data.strategies_applied.map(strategy => ({
            timestamp: strategy.timestamp,
            strategy: strategy.strategy_name,
            children: strategy.children.length
        }));

        // Create scales
        const xScale = d3.scaleLinear()
            .domain(d3.extent(events, d => d.timestamp))
            .range([0, innerWidth]);

        const yScale = d3.scaleLinear()
            .domain([0, d3.max(events, d => d.children)])
            .range([innerHeight, 0]);

        // Add axes
        g.append('g')
            .attr('class', 'timeline-axis')
            .attr('transform', `translate(0,${innerHeight})`)
            .call(d3.axisBottom(xScale));

        g.append('g')
            .attr('class', 'timeline-axis')
            .call(d3.axisLeft(yScale));

        // Add events
        g.selectAll('.timeline-event')
            .data(events)
            .enter()
            .append('circle')
            .attr('class', 'timeline-event')
            .attr('cx', d => xScale(d.timestamp))
            .attr('cy', d => yScale(d.children))
            .attr('r', 4)
            .on('mouseover', (event, d) => {
                this.tooltip.transition()
                    .duration(200)
                    .style('opacity', .9);
                this.tooltip.html(`Strategy: ${d.strategy}<br/>Children: ${d.children}<br/>Time: ${d.timestamp.toFixed(3)}s`)
                    .style('left', (event.pageX + 10) + 'px')
                    .style('top', (event.pageY - 28) + 'px');
            })
            .on('mouseout', () => {
                this.hideTooltip();
            });

        // Add labels
        g.append('text')
            .attr('transform', 'rotate(-90)')
            .attr('y', 0 - margin.left)
            .attr('x', 0 - (innerHeight / 2))
            .attr('dy', '1em')
            .style('text-anchor', 'middle')
            .text('Children Generated');

        g.append('text')
            .attr('transform', `translate(${innerWidth / 2}, ${innerHeight + margin.bottom})`)
            .style('text-anchor', 'middle')
            .text('Time (seconds)');
    }

    showNodeTooltip(event, nodeData) {
        this.tooltip.transition()
            .duration(200)
            .style('opacity', .9);

        const tooltipContent = `
            Node ${nodeData.id}<br/>
            Level: ${nodeData.level}<br/>
            Strategy: ${nodeData.strategy_applied || 'None'}<br/>
            Status: ${this.getNodeStatus(nodeData)}
        `;

        this.tooltip.html(tooltipContent)
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 28) + 'px');
    }

    hideTooltip() {
        this.tooltip.transition()
            .duration(500)
            .style('opacity', 0);
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update tab panels
        document.querySelectorAll('.tab-panel').forEach(panel => {
            panel.classList.remove('active');
        });
        document.getElementById(tabName).classList.add('active');

        // Re-render if needed
        if (tabName === 'search-tree') {
            setTimeout(() => this.renderSearchTree(), 100);
        } else if (tabName === 'timeline') {
            setTimeout(() => this.renderTimeline(), 100);
        }
    }


    async startRealtimeSearch() {
        // Show confirmation dialog
        const pattern = prompt('Enter permutation pattern to analyze (e.g., "123", "321", "1324"):', '132');
        if (!pattern) return;

        try {
            this.elements.startRealtimeBtn.style.display = 'none';
            this.elements.pauseResumeBtn.style.display = 'inline-block';
            this.isRealtimeMode = true;
            this.isPaused = false;

            this.updateStatus(`Starting real-time search for pattern ${pattern}...`);

            // Start the search on the server
            const response = await fetch('/api/start-search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ pattern: pattern })
            });

            if (response.ok) {
                this.updateStatus('Real-time search started - polling for updates...');
                this.startPolling();
            } else {
                throw new Error(`Failed to start search: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Error starting real-time search:', error);
            this.updateStatus(`Error: ${error.message}`);
            this.stopRealtimeMode();
        }
    }

    togglePauseResume() {
        if (this.isPaused) {
            this.resumeSearch();
        } else {
            this.pauseSearch();
        }
    }

    async pauseSearch() {
        try {
            const response = await fetch('/api/pause-search', { method: 'POST' });
            if (response.ok) {
                this.isPaused = true;
                this.elements.pauseResumeBtn.textContent = 'Resume';
                this.elements.pauseResumeBtn.className = 'btn btn-success';
                this.updateStatus('Search paused');
            }
        } catch (error) {
            console.error('Error pausing search:', error);
        }
    }

    async resumeSearch() {
        try {
            const response = await fetch('/api/resume-search', { method: 'POST' });
            if (response.ok) {
                this.isPaused = false;
                this.elements.pauseResumeBtn.textContent = 'Pause';
                this.elements.pauseResumeBtn.className = 'btn btn-warning';
                this.updateStatus('Search resumed');
            }
        } catch (error) {
            console.error('Error resuming search:', error);
        }
    }

    async stopServer() {
        if (confirm('Are you sure you want to stop the server? This will close the application.')) {
            try {
                this.updateStatus('Stopping server...');
                const response = await fetch('/api/stop-server', { method: 'POST' });
                if (response.ok) {
                    this.updateStatus('Server stopped successfully');
                    // Give user time to see the message before page becomes unresponsive
                    setTimeout(() => {
                        document.body.innerHTML = '<div style="text-align: center; margin-top: 50px; font-family: Arial;"><h1>Server Stopped</h1><p>The TileScope visualization server has been shut down.</p><p>You can close this browser tab.</p></div>';
                    }, 1000);
                } else {
                    this.updateStatus('Failed to stop server');
                }
            } catch (error) {
                console.error('Error stopping server:', error);
                this.updateStatus('Error connecting to server');
            }
        }
    }

    startPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
        }

        console.log('Starting real-time polling...');

        this.pollingInterval = setInterval(async () => {
            if (!this.isRealtimeMode) return;

            try {
                const response = await fetch('/api/data?t=' + Date.now());
                if (response.ok) {
                    const newData = await response.json();

                    // Check if data has changed
                    const newNodeCount = Object.keys(newData.nodes).length;
                    const currentNodeCount = this.data ? Object.keys(this.data.nodes).length : 0;

                    console.log(`Polling: Current nodes=${currentNodeCount}, New nodes=${newNodeCount}`);

                    if (newNodeCount > currentNodeCount) {
                        console.log(`Updating visualization: ${newNodeCount} nodes`);
                        this.loadData(newData);
                        this.updateStatus(`Real-time update: ${newNodeCount} nodes explored`);
                    }

                    // Check if search is complete
                    console.log('Checking for final_specification:', newData.final_specification);
                    if (newData.final_specification) {
                        console.log('Specification found! Updating display...');
                        this.updateStatus('Search completed - specification found!');
                        this.loadData(newData); // Ensure the specification data is loaded
                        this.stopRealtimeMode();
                    }
                } else {
                    console.log('Failed to fetch data:', response.status);
                }
            } catch (error) {
                console.log('Polling error:', error);
            }
        }, 1500); // Poll every 1.5 seconds to give file writes time to complete
    }

    stopRealtimeMode() {
        this.isRealtimeMode = false;
        this.elements.startRealtimeBtn.style.display = 'inline-block';
        this.elements.pauseResumeBtn.style.display = 'none';

        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
    }
}

// Initialize the visualizer when the page loads
document.addEventListener('DOMContentLoaded', () => {
    const visualizer = new TileScopeVisualizer();

    // Try to load default data
    visualizer.loadDefaultData();

    // Make it globally accessible for debugging
    window.tileScopeVisualizer = visualizer;
});