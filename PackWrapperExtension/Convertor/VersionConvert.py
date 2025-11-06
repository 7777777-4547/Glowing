from PIL import Image

# TODO: double-side chest image support.
def convert114_single_chest_image(chest_image_file_path: str):
    
    # Only work for single-side chest image
    
    def image_region_transpose(image: Image.Image, region: tuple[int,int,int,int], transpose_type: Image.Transpose):

        region_image = image.crop(region)
        region_image = region_image.transpose(transpose_type)
        
        image.paste(region_image, region)
        
        return image

    def image_region_move(image: Image.Image, region: tuple[int,int,int,int], offset: tuple[int,int]):

        new_image = image.copy()
        new_region: tuple = tuple(i+j for i,j in zip(region, offset*2))
        
        region_image = image.crop(region)
        new_image.paste((0,0,0,0), region)
        new_image.paste(region_image, new_region)
        
        
        return new_image

    def image_region_switch(image: Image.Image, move_region: tuple[int,int,int,int], cache_region: tuple[int,int,int,int], cache_release_region: tuple[int,int,int,int], offset: tuple[int,int]):
        image_cache = image.crop(cache_region)
        image = image_region_move(image, move_region, offset)
        image.paste(image_cache, cache_release_region)
        return image

    chest_image_lid_side_data = ((0,14,56,19), (0,14,42,19), (42,14,56,19), (0,14,14,19), (14,0))
    chest_image_trunk_side_data = ((0,33,56,43), (0,33,42,43), (42,33,56,43), (0,33,14,43), (14,0))
    chest_image_lock_side_data = ((0,1,6,5), (0,1,5,5), (5,1,6,5), (0,1,1,5), (1,0))
    chest_image_lid_column_data = ((14,0,42,14), (14,0,28,14), (28,0,42,14), (14,0,28,14), (14,0))
    chest_image_trunk_column_data = ((14,19,42,33), (14,19,28,33), (28,19,42,33), (14,19,28,33), (14,0))
    chest_image_lock_column_data = ((1,0,5,1), (1,0,3,1), (3,0,5,1), (1,0,3,1), (2,0))

    chest_image = Image.open(chest_image_file_path).convert("RGBA")
    for (a1,b1,c1,d1,e1), (a2,b2,c2,d2,e2) in zip(
        [chest_image_lid_side_data, chest_image_trunk_side_data, chest_image_lock_side_data], 
        [chest_image_lid_column_data, chest_image_trunk_column_data, chest_image_lock_column_data]
    ):
        
        chest_image = image_region_transpose(chest_image, a1, Image.Transpose.ROTATE_180)
        chest_image = image_region_switch(chest_image, b1, c1, d1, e1)
        
        chest_image = image_region_transpose(chest_image, a2, Image.Transpose.ROTATE_180)
        chest_image = image_region_transpose(chest_image, a2, Image.Transpose.FLIP_LEFT_RIGHT)
        chest_image = image_region_switch(chest_image, b2, c2, d2, e2)

    return chest_image

