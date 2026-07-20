from wagtail import hooks
from wagtail.images.image_operations import FilterOperation


class CropToContentOperation(FilterOperation):
    def construct(self):
        pass

    def run(self, willow, image, env):        
        willow.image = willow.image.crop(box=willow.image.getbbox())        
        return willow


@hooks.register("register_image_operations")
def register_image_operations():
    return [
        ("crop_to_content", CropToContentOperation),
    ]