import json
import readline

from tqdm import tqdm

from tilings import GriddedPerm, Tiling, TrackingAssumption

with open("tiling_data.txt", "r") as f:
    all_lines = f.readlines()

for i in tqdm(range(len(all_lines) // 2)):
    json_data = all_lines[2 * i]
    compare = all_lines[2 * i + 1]

    data = json.loads(json_data)
    data[0] = [GriddedPerm.from_dict(d) for d in data[0]]
    data[1] = [[GriddedPerm.from_dict(r) for r in req] for req in data[1]]
    data[2] = [TrackingAssumption.from_dict(ass) for ass in data[2]]
    # print(data[0])
    # print(data[1])
    # print(data[2])
    # print(data[3])
    # print(data[4])
    # print(data[5])
    # print(data[6])
    # print(data[7])
    T = Tiling(*data, check=False)
    assert repr(T) == compare.strip()
