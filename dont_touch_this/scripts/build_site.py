import glob

print("Hello world!")

with open("test.txt", "w") as f:
    f.write("test")

print(glob.glob("*.txt"))
