from grids import *
from permuta import Perm, PermSet


tiling = Tiling({(0, 0): PermSet.avoiding(Perm((0, 1))),
                 (0, 3): PermSet.avoiding(Perm((0, 1, 3, 2))),
                 (0, 1): Block.point,
                 (1, 2): PermSet.avoiding(Perm((0, 1, 2))),
                 (1, 1): PermSet.avoiding(Perm((1, 0)))})

print("The tiling used:")
print(tiling)

ttn3 = TilingTreeNode(tiling, [])
ttn2 = TilingTreeNode(tiling, [])
ttn1 = TilingTreeNode(tiling, [ttn2, ttn3])
tree = TilingTree(ttn1)

print()
print("A node json")
ttn_json = ttn1.to_json(indent="    ")
print(ttn_json)
print()

ttn_back = TilingTreeNode.from_json(ttn_json)
print("A node gotten back from the json")
print(ttn_back)
print(ttn_back.tiling)
print(ttn_back.children)


tree_json = tree.to_json(indent="    ")

print()
print(tree_json)
print()

tree.pretty_print()

tree2 = TilingTree.from_json(tree_json)

print("Tree from JSON:")
print(tree2)
print()
print(tree2.root)
print(tree2.root.tiling)
print(tree2.root.children)
print()
print(tree2.root.children[0])
print(tree2.root.children[0].tiling)
print(tree2.root.children[0].children)


tree2.pretty_print()
