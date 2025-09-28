from tilings.tilescope import *
import json
from permuta import *

# Getting all bases from files
# It might be better to have one file for each size of basis
all_sizes = []
for size in range(1, 13):
    with open(f"bases_size_{size}.json", "r") as f:
        bases = json.load(f)
    all_sizes.extend(bases)
    print(f"Size {size}: {len(bases)}")

# Loading all packs from file
with open("all_packs.json", "r") as f:
    loaded_packs = json.load(f)

# Creating the first pack
pack = TileScopePack.from_dict(loaded_packs[0][1])

# Using the first pack and an easy basis
tilescope = TileScope("231", pack)
spec = tilescope.auto_search()
print(spec)
