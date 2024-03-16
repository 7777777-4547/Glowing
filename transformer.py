from PIL import Image
import os
import shutil


def transformLightToAlpna(image: Image.Image):

    data = image.getdata()
    
    newData = []
    
    for pixel in data:

        red, green, blue, alpha = pixel

        if alpha == 0:
            newData.append(pixel)
        else:
            light = int(red*0.3 + green*0.59 + blue*0.11) - 1
            newData.append((0, 0, 0, light if light < 255 else 254))
        
    newImage = Image.new(image.mode, image.size)
    newImage.putdata(newData)
    
    return newImage



def transformLightToAlpnaGlobally(image: Image.Image):

    data = image.getdata()
    
    newData, tempData = [], []
    temp_R, temp_G, temp_B = 0, 0, 0
    
    for pixel in data:
        
        red, green, blue, alpha = pixel
        
        if alpha != 0:
            tempData.append(pixel)
            temp_R += red
            temp_G += green
            temp_B += blue
        
    tempDataLen = len(tempData)
    lightGlobal = (temp_R + temp_G + temp_B)//3//tempDataLen
    #print(lightGlobal)
                
    for pixel in data:

        red, green, blue, alpha = pixel

        if alpha == 0:
            newData.append(pixel)
        else:
            newData.append((0, 0, 0, lightGlobal))
        
    newImage = Image.new(image.mode, image.size)
    newImage.putdata(newData)
    
    return newImage




def main(path: str, entityMode = False):
    
    for root, _, files in os.walk(path):

        for file in files:

            if file.endswith("_e.png"):
                
                file = os.path.join(root, file).replace("\\", "/")
                
                image = Image.open(file)
                width, height = image.size
                
                if image.mode != "RGBA":
                    image = image.convert("RGBA")
                
                if height//width != 1 and entityMode == False:
                    invertedImage = transformLightToAlpnaGlobally(image)
                    invertedImage.save(file.replace("_e.png","_e_s.png"))
                    
                else:
                    invertedImage = transformLightToAlpna(image)
                    invertedImage.save(file.replace("_e.png","_e_s.png"))

                print(f"{file} -> {file.replace("_e.png","_e_s.png")}")
                
            elif file.endswith("_e.png.mcmeta"):
                
                file = os.path.join(root, file).replace("\\", "/")
                
                if os.path.exists(file.replace("_e.png.mcmeta","_e_s.png.mcmeta")):
                    os.remove(file.replace("_e.png.mcmeta","_e_s.png.mcmeta"))
                
                shutil.copy2(file, file.replace("_e.png.mcmeta","_e_s.png.mcmeta"))
                
                print(f"{file} -> {file.replace("_e.png.mcmeta","_e_s.png.mcmeta")}")


main("./assets/minecraft/textures/block")
main("./assets/minecraft/textures/entity",True)
main("./assets/minecraft/textures/item")

main("./assets/minecraft/textures/trims/items")
main("./assets/minecraft/textures/trims/models",True)