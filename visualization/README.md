# TileScope Visualization

A browser-based visualization tool for the TileScope algorithm that shows the search process for finding combinatorial specifications of permutation classes.

## Overview

The TileScope algorithm starts with a permutation class (defined by avoiding certain patterns) and systematically builds a universe of related "tilings" - grid-based combinatorial objects. It then searches this universe using various strategies to find a specification that describes the structure of the original permutation class.

This visualization shows:
- **Search Tree**: Interactive tree of all tilings explored during the search
- **Tiling Details**: Visual representation of individual tilings with their constraints
- **Strategy Applications**: Which strategies were applied and their results
- **Timeline**: Chronological view of the search progression
- **Final Specification**: The resulting combinatorial specification

## Quick Start

### Real-time Visualization (Recommended)
1. **Start the real-time demo:**
   ```bash
   python3 demo_realtime.py
   ```
   Then click "Start Real-time Search" in the browser and watch the algorithm explore tilings live!

### Static Visualization
1. **Generate visualization data and launch server:**
   ```bash
   python3 run_visualization.py
   ```

2. **Or run specific pattern:**
   ```bash
   python3 run_visualization.py "231"
   ```

3. **Or just launch server with existing data:**
   ```bash
   python3 server.py
   ```

The visualization will open in your browser at `http://localhost:8000`.

## Files Structure

```
visualization/
├── README.md                    # This file
├── tilescope_visualizer.py     # Enhanced TileScope with data capture
├── test_visualization.py       # Simple test script
├── run_visualization.py        # Complete example runner
├── server.py                   # HTTP server for web interface
└── web/                        # Web interface files
    ├── index.html              # Main HTML page
    ├── style.css               # Styling
    ├── script.js               # Interactive JavaScript
    └── visualization_data.json # Generated data file
```

## Usage Examples

### Basic Example (Avoiding 231)
```bash
python3 run_visualization.py "231"
```

### Custom Pattern
```bash
python3 run_visualization.py "1324"
```

### Interactive Mode
```bash
python3 run_visualization.py --interactive
```

### Generate Data Only
```bash
python3 run_visualization.py "231" --no-server
```

## Real-time Features ⚡

### Live Search Visualization
- **Start Real-time Search**: Click the green button to start a live search
- **Choose Pattern**: Enter any permutation pattern (e.g., "123", "321", "1324")
- **Watch Live Updates**: See nodes appear in real-time as the algorithm explores
- **Pause/Resume**: Use the pause button to stop and examine the current state
- **Continuous Updates**: The visualization updates every second with new discoveries

### Why Use Pattern "123"?
Pattern "123" (increasing sequence) is perfect for demonstrations because:
- It generates a very large search tree
- The search will run indefinitely, giving you time to explore
- You can see many different strategies being applied
- Perfect for testing pause/resume functionality

## Understanding the Visualization

### Search Tree Tab
- **Root Node** (blue): Starting permutation class
- **Expanded Nodes** (orange): Tilings that had strategies applied
- **Specification Nodes** (green): Tilings that are part of the final combinatorial specification
- **Other Nodes** (gray): Explored tilings not used in the final specification
- **Links**: Show parent-child relationships from strategy applications

### Tiling Details
When you click a node, you'll see:
- **ASCII representation** of the tiling grid
- **Obstructions**: Forbidden patterns in specific cells
- **Requirements**: Patterns that must appear
- **Dimensions**: Size of the tiling grid
- **Active cells**: Cells that can contain permutations

### Timeline Tab
Shows the chronological progression of strategy applications and how many children each generated.

### Specification Tab
Displays the final combinatorial specification if one was found.

## Technical Details

### Data Capture
The `VisualizationTileScope` class extends the standard TileScope to capture:
- Every tiling explored
- Strategy applications and their results
- Parent-child relationships
- Verification status
- Timestamps

### Web Interface
- **D3.js** for interactive tree visualization
- **Responsive design** that works on different screen sizes
- **Real-time updates** during long searches
- **Zoom and pan** for large search trees

## Customization

### Adding New Strategy Packs
You can test different strategy packs by modifying `generate_example_data()`:

```python
# Instead of:
pack = TileScopePack.point_placements()

# Try:
pack = TileScopePack.insertion_point_placements()
# or
pack = TileScopePack.regular_insertion_encoding(3)
```

### Extending Visualization
The data format is JSON-based and easily extensible. See `tilescope_visualizer.py` to add more fields to capture.

## Troubleshooting

### Port Already in Use
```bash
python3 server.py --port 8080
```

### Missing Dependencies
Make sure you have the main Tilings repository properly set up with all dependencies.

### Large Search Trees
For complex patterns that generate large search trees, the visualization may take time to render. Use the browser's developer tools to monitor performance.

## Example Patterns to Try

- `"231"` - Simple example, quick to compute
- `"123"` - Increasing pattern
- `"321"` - Decreasing pattern
- `"1324"` - More complex, longer search
- `"2143"` - Interesting structure

## Technical Architecture

1. **Data Extraction Layer**: `VisualizationTileScope` captures search data
2. **Web Server**: Simple HTTP server serves the interface
3. **Frontend**: HTML/CSS/JS with D3.js for interactive visualization
4. **Data Format**: JSON with nodes, edges, and metadata

The visualization is designed to be:
- **Self-contained**: No external dependencies beyond D3.js
- **Extensible**: Easy to add new views and data
- **Interactive**: Click, zoom, and explore the search process
- **Educational**: Helps understand how TileScope works