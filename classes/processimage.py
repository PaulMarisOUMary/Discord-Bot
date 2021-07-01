from PIL import Image, ImageDraw, ImageFont
import io

class ProcessImage():
    def __init__(self, width, height, type = "RGB", bg = (47,47,47)) -> None:
        self.width = width
        self.height = height
        self.product = Image.new(mode=type, size=(width, height), color=bg)
        self.pen = ImageDraw.Draw(self.product)

    def place(self, x, y, width, height):
        return (x, y, x + width - 1, y + height - 1)

    def rectangle(self, place, color):
        self.pen.rectangle(place, fill = color)

    def line(self, place, color):
        self.pen.line(place, fill = color)

    def text(self, place, color, text, fontsize, font = "arial.ttf"):
        self.pen.text(place, text, font = ImageFont.truetype(font, fontsize), fill = color)

    def textCentered(self, widthC, heightC, color, text, fontsize, font = "arial.ttf"):
        size = self.getTextsize(text, fontsize)
        self.text(self.place(widthC/2 - size[0]/2, heightC/2 - size[1]/2, size[0], size[1]), color, text, fontsize, font)

    def getTextsize(self, text, fontsize, font = "arial.ttf"):
        width = 0
        for char in text:
            size = ImageFont.truetype(font, fontsize).getsize(char)
            width += size[0]
        return (width, size[1])

    def saveAs(self, path):
        self.product.save(path, 'PNG')

    def saveBinary(self):
        product_binary = io.BytesIO()
        self.saveAs(product_binary)
        product_binary.seek(0)

        return product_binary