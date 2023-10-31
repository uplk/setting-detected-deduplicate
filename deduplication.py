

from Siamese.siamese import Siamese
from PIL import Image


pictures = []
def get_data(filename):
    pass

def predict(imgae_name):

    model = Siamese()
        
    image = Image.open(imgae_name)

    probability = model.detect_image(image_1,image_2)
    print(probability)