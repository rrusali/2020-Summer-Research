import os
import matplotlib.pyplot as plt
from PIL import Image

name_path = 'D:/Research Files/Orientational Order Parameter/Counties/'
area_names = [dI for dI in os.listdir(name_path) if os.path.isdir(os.path.join(name_path,dI))]

while True:
    print('Your options are: \n')
    for area in area_names:
        print(area)

    name = input('\nChoose your area: ')
    name = [i for i in area_names if i.startswith(name)][0]

    img_path = name_path + '%s/%s_hex_map.png' % (name, name)
    img = Image.open(img_path)
    img.show()

    while True:
        answer = str(input('\nGet another area? [y/n]: '))
        if answer in ('y', 'n'):
            break
        print("invalid input.")
    if answer == 'y':
        continue
    else:
        print("\nThanks for using this tool!")
        break
