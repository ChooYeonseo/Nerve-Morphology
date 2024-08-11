from morpho import LegModel
from morpho import NerveMap
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import json

model_setting = 'run' #"set" or "run"
current_model = "23-21R"

def get_morpho_value():
    Nerve = []
    Nerve_number = int(input("Please enter the Nerve Number: "))
    print("Please enter the Nerve Orientation: ")
    for i in range(Nerve_number):
        Nerve.append(list(map(int, input().split())))
    return Nerve_number, Nerve

print("===============================")
print("Welcome to Nerve Morpho Program")
print("===============================")


L = LegModel(current_model)
leg_coord, landmark = L.get_coord()

N = NerveMap(leg_coord, landmark, current_model)
N.keyorderprinter()

Lx, Ly = zip(*leg_coord)
Mx, My = zip(*landmark)
annote_leg = ["TIP", "MID", "CP", "MID12", "MID10", "LAT"]

fig, ax = plt.subplots()
ax.plot(Lx, Ly, zorder=0)
ax.scatter(Mx, My, color="red", zorder=1)

for i, txt in enumerate(annote_leg):
    ax.annotate(txt, (Mx[i], My[i]))

# Nerve point plotting
number_of_NP, dictionary_nerve = N.NervePlottingPoints()
for i in range(number_of_NP):
    ax.scatter(dictionary_nerve[i+1][0], dictionary_nerve[i+1][1], color="orange", zorder=2)


plt.show()
file_dir = './data/data.json'
with open(file_dir, 'r') as file:
    data = json.load(file)
# Nerve = [] # Nerve = [[1, 2, 4, 6], [1, 2, 4, 7], [1, 3, 5, 8, 10], [1, 3, 5, 9, 11]]
# Nerve_number = 0 # Nerve_number = 4
if model_setting == "set":
    print(data)
    if current_model in data.keys():
        print("{} data already exists.".format(current_model))
        move_yn = input("Do you want to update the value?[Y/N]: ")
        if move_yn == 'Y':
            Nerve_number, Nerve = get_morpho_value()
            data[current_model] = {"Nerve": Nerve, "Nerve_number": Nerve_number}
            print(data)

            with open(file_dir, 'w') as file:
                json.dump(data, file, indent=4)
        elif move_yn == 'N':
            print("Program END")
    else:
        Nerve_number, Nerve = get_morpho_value()
        data[current_model] = {"Nerve": Nerve, "Nerve_number": Nerve_number}
        print(data)
        with open(file_dir, 'w') as file:
            json.dump(data, file, indent=4)
    
    
    
elif model_setting == "run":
    if current_model not in data.keys():
        print("{} data does not exists. Please change the model setting to SET".format(current_model))
    Nerve_number = data[current_model]["Nerve_number"]
    Nerve = data[current_model]["Nerve"]

    fig, ax = plt.subplots()
    fig.set_figheight(10)
    ax.set_xlim(-40, 40)
    ax.set_aspect('equal')


    ax.plot(Lx, Ly, color="black", zorder=0)
    ax.scatter(Mx, My, color="red", zorder=1)

    for i in range(len(Nerve)):
        for j in range(len(Nerve[i])):
            Nerve[i][j] = dictionary_nerve[Nerve[i][j]]
    zo = 2
    for Ni in Nerve:
        x_coords = [point[0] for point in Ni]
        y_coords = [point[1] for point in Ni]
        ax.plot(x_coords, y_coords, color = "orange", zorder=zo)
        zo += 1

    annote_leg = ["TIP", "MID", "CP", "MID12", "MID10", "LAT"]
    for i, txt in enumerate(annote_leg):
        ax.annotate(txt, (Mx[i], My[i]), zorder=100)

    # bg_img = mpimg.imread(f"./data/left.png")
    # img_height, img_width = bg_img.shape[:2]
    # print(img_height, img_width)
    # plt.imshow(bg_img, extent=[-3, 10, -4, 10], aspect='auto')
    plt.savefig("./svg/{}_NerveMorpho.svg".format(current_model))
    plt.show()