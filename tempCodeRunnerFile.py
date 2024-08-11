import matplotlib.pyplot as plt
import matplotlib.image as mpimg

bg_img = mpimg.imread(f"./data/left.png")
fig, ax = plt.subplots()
ax.imshow(bg_img, extent=[-3, 10, -4, 10], aspect='auto')
plt.show()