from PIL import Image
import os
import shutil


class transformerLogger:
    
    def Logger(char):
        print(char)
        
    def transformFile(rawName, newName):
        print(f" \033[34m|\033[0m {rawName} \033[34m->\033[0m {newName}")


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
        
        rootPath = root.replace("\\", "/")
        transformerLogger.Logger(f"\n{rootPath}")

        for file in files:
            
            fileName = file
            
            emissiveSuffix = "_e"
            shaderSuffix = "_s"
            
            rawSuffix = f"{emissiveSuffix}.png"
            newSuffix = f"{emissiveSuffix}{shaderSuffix}.png"
            
            if file.endswith(rawSuffix):
                
                rawFile = os.path.join(root, file).replace("\\", "/")
                newFile = rawFile.replace(rawSuffix, newSuffix)
                
                image = Image.open(rawFile)
                width, height = image.size
                
                if image.mode != "RGBA":
                    image = image.convert("RGBA")
                
                if height//width != 1 and entityMode == False:
                    invertedImage = transformLightToAlpnaGlobally(image)
                    invertedImage.save(newFile)
                    
                else:
                    invertedImage = transformLightToAlpna(image)
                    invertedImage.save(newFile)

                transformerLogger.transformFile(fileName, fileName.replace(rawSuffix, newSuffix))
                
            elif file.endswith(f"{rawSuffix}.mcmeta"):
                
                rawFile = os.path.join(root, file).replace("\\", "/")
                newFile = rawFile.replace(f"{rawSuffix}.mcmeta", f"{newSuffix}.mcmeta")
                
                if os.path.exists(newFile):
                    os.remove(newFile)
                
                shutil.copy2(rawFile, newFile)
                
                transformerLogger.transformFile(fileName, fileName.replace(f"{rawSuffix}.mcmeta", f"{newSuffix}.mcmeta"))
                
                

transformerLogger.Logger("\nTransformer Starting...")

main("./assets/minecraft/textures/block")
main("./assets/minecraft/textures/entity",True)
main("./assets/minecraft/textures/item")

main("./assets/minecraft/textures/trims/items")
main("./assets/minecraft/textures/trims/models",True)

transformerLogger.Logger("\n\033[32m Transform Success \033[0m\n")