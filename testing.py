from tilings.tilescope import *
import json
import requests

from permuta import *

# def find_bases_of_size(n, size):
#     res = []
#     from itertools import combinations
#     from permuta.permutils.symmetry import lex_min
#     from permuta.permutils import is_insertion_encodable
#     count = 0
#     for basis in combinations(Perm.of_length(n), size):
#         if tuple(sorted(list(basis))) == lex_min(list(basis)) and not is_insertion_encodable(
#             basis
#         ):
#             res.append("_".join(str(p) for p in basis))
#             count += 1
#     print(f"Found {count} bases of size {size} for n={n}")
#     return res

# for size in range(1, 13):
#     bases = find_bases_of_size(4, size)
#     print(f"Size {size}: {len(bases)}")
#     # Save the bases to a file
#     with open(f"bases_size_{size}.json", "w") as f:
#         json.dump(bases, f)

# # Test loading the bases from the files and counting them
# for size in range(1, 13):
#     with open(f"bases_size_{size}.json", "r") as f:
#         bases = json.load(f)
#     print(f"Size {size}: {len(bases)}")

all_sizes = []
for size in range(1, 13):
    with open(f"bases_size_{size}.json", "r") as f:
        bases = json.load(f)
    all_sizes.extend(bases)
    print(f"Size {size}: {len(bases)}")

all_sizes = all_sizes
collect_all_packs = []
for basis in all_sizes:
    if basis == "0213":
        continue
    print("Getting packs for basis", basis)
    uri = f"https://permpal.com/perms/raw_data_json/basis/{basis}"
    response = requests.get(uri)
    json_data = response.json()
    for bla in json_data["specs_and_eqs"]:
        # print(bla["pack_name"])
        # print(bla["pack_json"])
        # If the (pack_name, pack_json) pair is not already in the list, add it
        if (bla["pack_name"], bla["pack_json"]) not in collect_all_packs:
            collect_all_packs.append((bla["pack_name"], bla["pack_json"]))

print(len(collect_all_packs))

# Save all packs to a file
with open("all_packs.json", "w") as f:
    json.dump(collect_all_packs, f)

# Test loading all the packs
with open("all_packs.json", "r") as f:
    loaded_packs = json.load(f)

for name, pack_dict in loaded_packs:
    pack = TileScopePack.from_dict(pack_dict)
    print(name, pack)

# basis = "0123_0213"
# uri = f"https://permpal.com/perms/raw_data_json/basis/{basis}"
# json = requests.get(uri).json()

# print(json["name"])

# for bla in json["specs_and_eqs"]:
#     for k in bla.keys():
#         if k == "pack_name":
#             print(f"{k}: {bla[k]}")
#         if k == "pack_json":
#             print(f"{k}: {bla[k]}")
#     print()


# pack = TileScopePack.from_dict(json["specs_and_eqs"][4]["pack_json"])
# print(pack)

# tilescope = TileScope(basis, pack)
# spec = tilescope.auto_search()
# print(spec)


# pack = TileScopePack.point_placements()

# tilescope = TileScope("231", pack)
# spec = tilescope.auto_search()
# print(spec)
