"""
TileScope Visualizer - Enhanced TileScope that captures search data for browser visualization.
"""
import json
import time
from typing import (
    Dict,
    List,
    Any,
    Optional,
    Tuple,
    Union,
    Iterable,
    Iterator,
    Set,
    cast,
)

from comb_spec_searcher import CombinatorialSpecification
from comb_spec_searcher.class_db import ClassDB
from comb_spec_searcher.class_queue import CSSQueue
from comb_spec_searcher.rule_db.abstract import RuleDBAbstract
from comb_spec_searcher.strategies.rule import AbstractRule
from comb_spec_searcher.typing import CombinatorialClassType, CSSstrategy
from permuta import Perm
from tilings import Tiling, GriddedPerm
from tilings.tilescope import TileScope, TileScopePack


class VisualizationTileScope(TileScope):
    """
    Enhanced TileScope that captures search progression data for visualization.
    """

    def __init__(
        self,
        start_class: Union[str, Iterable[Perm], Tiling],
        strategy_pack: TileScopePack,
        ruledb: Optional[RuleDBAbstract] = None,
        classdb: Optional[ClassDB] = None,
        classqueue: Optional[CSSQueue] = None,
        expand_verified: bool = False,
        debug: bool = False,
    ) -> None:
        # Initialize visualization data storage BEFORE calling super()
        self.search_data: Dict[str, Any] = {
            "start_time": time.time(),
            "nodes": {},  # node_id -> node data
            "edges": [],  # parent_id -> child_id relationships
            "search_tree": [],  # chronological order of search steps
            "strategies_applied": [],  # list of strategy applications
            "final_specification": None,
            "status_updates": [],
        }

        self.node_counter: int = 0
        self.current_level: int = 0

        # Map tiling string representations to node IDs for quick lookup
        self.tiling_to_node_id: Dict[str, int] = {}

        # Real-time visualization support
        self.is_paused: bool = False
        self.output_file: Optional[str] = None
        self.update_callbacks: List[Any] = []

        # Now call super() after data structures are initialized
        super().__init__(
            start_class=start_class,
            strategy_pack=strategy_pack,
            ruledb=ruledb,
            classdb=classdb,
            classqueue=classqueue,
            expand_verified=expand_verified,
            debug=debug,
        )

        # Add root node
        root_tiling = self.start_class
        self.add_node(root_tiling, is_root=True)
        self.save_incremental_update()

    def add_node(
        self,
        tiling: Tiling,
        parent_id: Optional[int] = None,
        strategy_name: str = "",
        is_root: bool = False,
    ) -> int:
        """Add a new tiling node to the visualization data."""
        tiling_str = str(tiling)

        # Check if we already have this tiling
        if tiling_str in self.tiling_to_node_id:
            return self.tiling_to_node_id[tiling_str]

        node_id = self.node_counter
        self.node_counter += 1

        # Calculate level based on parent
        if is_root:
            level = 0
        elif parent_id is not None and parent_id in self.search_data["nodes"]:
            level = self.search_data["nodes"][parent_id]["level"] + 1
        else:
            level = 0

        # Convert tiling to JSON-serializable format
        node_data = {
            "id": node_id,
            "tiling": self.tiling_to_dict(tiling),
            "parent_id": parent_id,
            "strategy_applied": strategy_name,
            "timestamp": time.time() - self.search_data["start_time"],
            "level": level,
            "is_root": is_root,
            "is_verified": False,
            "is_expanded": False,
        }

        self.search_data["nodes"][node_id] = node_data
        self.tiling_to_node_id[tiling_str] = node_id

        if parent_id is not None:
            self.search_data["edges"].append(
                {"parent": parent_id, "child": node_id, "strategy": strategy_name}
            )

        return node_id

    def tiling_to_dict(self, tiling: Tiling) -> Dict[str, Any]:
        """Convert a Tiling object to a JSON-serializable dictionary."""
        return {
            "dimensions": tiling.dimensions,
            "obstructions": [
                self.griddedperm_to_dict(obs) for obs in tiling.obstructions
            ],
            "requirements": [
                [self.griddedperm_to_dict(gp) for gp in req]
                for req in tiling.requirements
            ],
            "assumptions": [str(ass) for ass in tiling.assumptions],
            "active_cells": list(tiling.active_cells),
            "empty_cells": list(tiling.empty_cells),
            "ascii_repr": str(tiling),
        }

    def griddedperm_to_dict(self, gp: GriddedPerm) -> Dict[str, Any]:
        """Convert a GriddedPerm to a dictionary."""
        return {"pattern": str(gp.patt), "positions": list(gp.pos)}

    def _rules_from_strategy(
        self, comb_class: CombinatorialClassType, strategy: CSSstrategy
    ) -> Iterator[AbstractRule]:
        """Override to capture strategy applications."""
        # Check if search is paused
        self.check_pause()

        strategy_name = str(strategy)

        # Get the parent node ID for this tiling using string representation
        parent_id = None
        tiling_str = str(comb_class)
        if tiling_str in self.tiling_to_node_id:
            parent_id = self.tiling_to_node_id[tiling_str]

        strategy_info = {
            "strategy_name": strategy_name,
            "parent_tiling": tiling_str,
            "parent_id": parent_id,
            "timestamp": time.time() - self.search_data["start_time"],
            "children": [],
        }

        # Get rules from parent method
        rules = list(super()._rules_from_strategy(comb_class, strategy))

        # Add children nodes for each rule
        children_added = False
        for rule in rules:
            for child in rule.children:
                child_id = self.add_node(child, parent_id, strategy_name)
                strategy_info["children"].append(child_id)
                children_added = True

        self.search_data["strategies_applied"].append(strategy_info)

        # Mark parent as expanded
        if parent_id is not None:
            self.search_data["nodes"][parent_id]["is_expanded"] = True

        # Save incremental update for real-time visualization
        if children_added:
            self.save_incremental_update()
            # Add a small delay to make visualization updates more visible
            # and prevent file I/O race conditions
            time.sleep(0.5)

        return iter(rules)

    def check_pause(self) -> None:
        """Check if the search should be paused and wait if necessary."""
        while self.is_paused:
            time.sleep(0.1)  # Small sleep to avoid busy waiting

    def pause_search(self) -> None:
        """Pause the search."""
        self.is_paused = True
        self.add_status_update("Search paused")

    def resume_search(self) -> None:
        """Resume the search."""
        self.is_paused = False
        self.add_status_update("Search resumed")

    def save_incremental_update(self) -> None:
        """Save current state for real-time updates."""
        if self.output_file:
            # Convert any remaining non-serializable objects
            data_copy = json.loads(json.dumps(self.search_data, default=str))

            with open(self.output_file, "w") as f:
                json.dump(data_copy, f, indent=2)

    def mark_verified(self, tiling: Tiling, verification_strategy: str) -> None:
        """Mark a tiling as verified."""
        tiling_str = str(tiling)
        if tiling_str in self.tiling_to_node_id:
            node_id = self.tiling_to_node_id[tiling_str]
            self.search_data["nodes"][node_id]["is_verified"] = True
            self.search_data["nodes"][node_id][
                "verification_strategy"
            ] = verification_strategy

    def add_status_update(self, message: str) -> None:
        """Add a status update for the visualization."""
        self.search_data["status_updates"].append(
            {
                "timestamp": time.time() - self.search_data["start_time"],
                "message": message,
            }
        )

    def auto_search(self, **kwargs) -> Optional[CombinatorialSpecification]:
        """Override auto_search to capture the final specification."""
        self.add_status_update("Starting auto search...")

        result = super().auto_search(**kwargs)

        if result:
            # Get the combinatorial classes used in the specification
            used_classes = set()
            if hasattr(result, "rules_dict"):
                for rule in result.rules_dict:
                    used_classes.add(str(rule))
                    # If the rule has children, add them too
                    if (
                        hasattr(result.rules_dict[rule], "children")
                        and result.rules_dict[rule].children
                    ):
                        for child in result.rules_dict[rule].children:
                            used_classes.add(str(child))

            # Find all nodes that match the specification classes
            spec_node_ids = set()
            for node_id_str, node_data in self.search_data["nodes"].items():
                tiling_str = node_data["tiling"]["ascii_repr"]
                if tiling_str in used_classes:
                    spec_node_ids.add(int(node_id_str))

            # Also include all ancestor nodes that lead to specification nodes
            all_used_node_ids = set(spec_node_ids)

            def add_ancestors(node_id):
                """Recursively add all ancestors of a node"""
                if str(node_id) in self.search_data["nodes"]:
                    parent_id = self.search_data["nodes"][str(node_id)]["parent_id"]
                    if parent_id is not None and parent_id not in all_used_node_ids:
                        all_used_node_ids.add(parent_id)
                        add_ancestors(parent_id)

            # Add ancestors for all specification nodes
            for node_id in spec_node_ids:
                add_ancestors(node_id)

            # Mark nodes that are used in the specification or are ancestors
            used_node_ids = []
            for node_id_str, node_data in self.search_data["nodes"].items():
                node_id = int(node_id_str)
                if node_id in all_used_node_ids:
                    node_data["used_in_specification"] = True
                    used_node_ids.append(node_id)
                else:
                    node_data["used_in_specification"] = False

            self.search_data["final_specification"] = {
                "rules": str(result),
                "rule_count": len(result.rules_dict)
                if hasattr(result, "rules_dict")
                else 0,
                "used_node_ids": used_node_ids,
                "timestamp": time.time() - self.search_data["start_time"],
            }
            self.add_status_update("Specification found!")
            # Save the final specification to file
            self.save_incremental_update()
        else:
            self.add_status_update("No specification found.")
            self.save_incremental_update()

        return result

    def save_visualization_data(self, filepath: str = "visualization_data.json") -> str:
        """Save the captured visualization data to a JSON file."""
        # Set output file for real-time updates
        self.output_file = filepath

        # Convert any remaining non-serializable objects
        data_copy = json.loads(json.dumps(self.search_data, default=str))

        with open(filepath, "w") as f:
            json.dump(data_copy, f, indent=2)

        print(f"Visualization data saved to {filepath}")
        return filepath

    def start_realtime_search(
        self, filepath: str = "web/visualization_data.json"
    ) -> Optional[CombinatorialSpecification]:
        """Start search with real-time visualization updates."""
        self.output_file = filepath
        self.save_incremental_update()  # Save initial state
        return self.auto_search()
