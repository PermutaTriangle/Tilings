import sys

from permuta import Perm, PermSet

from .JsonAble import JsonAble
from .Tiling import Tiling


__all__ = ["TilingTree", "TilingTreeNode"]


class TilingTreeNode(JsonAble):
    def __init__(self, tiling, children=[]):
        self.tiling = tiling
        self.children = list(children)

    @classmethod
    def _prepare_attr_dict(cls, attr_dict):
        attr_dict["tiling"] = Tiling._from_attr_dict(attr_dict["tiling"])
        attr_dict["children"] = map(cls._from_attr_dict,
                                    attr_dict["children"])
        return attr_dict

    def _to_json(self):
        attr_dict = super(TilingTreeNode, self)._to_json()
        attr_dict["children"] = [child._to_json()
                                 for child
                                 in attr_dict["children"]]
        return attr_dict


class TilingTree(JsonAble):
    """A where tilings are the main value of the nodes."""

    _NODE_CLASS = TilingTreeNode
    __PRETTY_PRINT_DICT = dict(L="└─────", pipe="│     ", T="├─────", empty="      ")

    def __init__(self, root):
        self.root = root

    @classmethod
    def _prepare_attr_dict(cls, attr_dict):
        Node = cls._NODE_CLASS
        attr_dict["root"] = Node._from_attr_dict(attr_dict["root"])
        return attr_dict

    def pretty_print(self, file=sys.stdout):
        legend = [["label counter:", 0]]
        self._pretty_print(self.root, 0, legend, file=file)
        for label, tiling in legend:
            if isinstance(tiling, int):
                continue
            print(file=file)
            print("Label:", label, file=file)
            print(file=file)
            print(tiling, file=file)

    def _pretty_print(self, root, depth, legend, prefix="root: ", tail=False, file=sys.stdout):
        tp_L = TilingTree.__PRETTY_PRINT_DICT["L"]
        tp_pipe = TilingTree.__PRETTY_PRINT_DICT["pipe"]
        tp_tee = TilingTree.__PRETTY_PRINT_DICT["T"]
        tp_empty = TilingTree.__PRETTY_PRINT_DICT["empty"]
        label_counter = legend[0][1]
        print(prefix, label_counter, sep="", file=file)
        legend.append([label_counter, root.tiling])
        legend[0][1] += 1
        for subtree_number in range(len(root.children)-1):
            self._pretty_print(root.children[subtree_number],
                               depth+1,
                               legend,
                               prefix[:-6] + (tp_pipe if tail else tp_empty) + tp_tee,
                               True,
                               file)
        if len(root.children) > 1:
            self._pretty_print(root.children[-1],
                               depth+1,
                               legend,
                               prefix[:-6] + (tp_pipe if tail else tp_empty) + tp_L,
                               False,
                               file)
