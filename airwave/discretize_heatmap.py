#!/usr/bin/env python3

from PIL import Image, ImageFilter, ImageStat, ImageDraw

WHITE = (255, 255, 255, 255)

SIGNAL_45 = (170, 70, 70, 255)
SIGNAL_55 = (245, 200, 90, 255)
SIGNAL_65 = (185, 255, 145, 255)

class HeatmapImage:
    def __init__(self, filepath):
        self._image = Image.open(filepath)

        window_width, window_height = self._image.size

        # Find div boundaries
        for div_left in range(window_width//2):
            if not self.pixel_is_white(div_left, window_height//2):
                break
#        print(div_left)
        for div_upper in range(window_height-1, 0, -1):
            if not self.pixel_is_white(div_left+2, div_upper):
                break
#        print(div_upper)

        # Find grid boundaries
        for grid_left in range(div_left+5, window_width//2):
            if not self.pixel_is_white(grid_left, window_height//2):
                break
#        print(grid_left)
        for grid_right in range(grid_left, window_width):
            if self.pixel_is_white(grid_right+1, window_height//2):
                break
#        print(grid_right)
        for grid_upper in range(div_upper+5, window_height//2):
            if not self.pixel_is_white(grid_right-5, grid_upper):
                break
#        print(grid_upper)

        # Crop
        self._image = self._image.crop((grid_left, grid_upper, grid_right, 
                    window_height))

        # Determine coarse grid scale
        x = 1
        while self.pixel_is_white(x, 1):
            x += 1
        self._coarse_scale = x

        self._fine_scale = 28

    def pixel_is_white(self, x, y):
        pixel = self._image.getpixel((x, y))
        return pixel[0] > 250 and pixel[1] > 250 and pixel[2] > 250

    def estimate_fine_scale(self):
        self._image.show()
        grid_x = int(input("Grid X? "))
        grid_y = int(input("Grid Y? "))
        grid_square = self.get_coarse_square(grid_x, grid_y)
        grid_square.show()
        percent_x = float(input("Percent X? "))
        percent_y = float(input("Percent Y? "))
        x = int(self.coarse_scale * (grid_x + percent_x))
        y = int(self.coarse_scale * (grid_y + percent_y))
        base = self._image.getpixel((x, y))
        left = x
        while left > 0 and self._image.getpixel((left, y)) == base:
            left = left - 1
        right = x
        while (right < self._image.width and 
                self._image.getpixel((right, y)) == base):
            right = right + 1
        upper = y
        while upper > 0 and self._image.getpixel((x, upper)) == base:
            upper = upper - 1
        lower = y
        while (lower < self._image.height and 
                self._image.getpixel((x, lower)) == base):
            lower = lower + 1

        width = right - left
        height = lower - upper
        self._fine_scale = min(width, height)

    @property 
    def coarse_size(self):
        image_width, image_height = self._image.size
        return (image_width/self.coarse_scale, image_height/self.coarse_scale)

    @property
    def coarse_scale(self):
        return self._coarse_scale

    def get_square(self, x, y, scale):
        left = x * scale
        upper = y * scale
        right = left + scale
        lower = upper + scale
        return self._image.crop((left, upper, right, lower))

    def get_coarse_square(self, x, y):
        return self.get_square(x, y, self._coarse_scale)

    def get_fine_square(self, x, y):
        return self.get_square(x, y, self._fine_scale)

    def get_fine_color(self, x, y):
        square = self.get_fine_square(x, y)
        return ImageStat.Stat(square).median

    @property
    def fine_size(self):
        image_width, image_height = self._image.size
        return (image_width/self.fine_scale, image_height/self.fine_scale)

    @property
    def fine_scale(self):
        return self._fine_scale

    def test(self):
        self._image.filter(ImageFilter.CONTOUR).show()

    def show(self):
        self._image.show()

def load_image():
    return Image.open('Case_f3_5Ghz.png')

def get_coarse_grid_size(img):
    width, height = img.size
    width

def main():
    img = HeatmapImage('Case_f3_2Ghz.png')
    print("Coarse grid size:", img.coarse_size)
    print("Coarse grid scale:", img.coarse_scale)

    img.show()

#    img.test()

#    img.estimate_fine_scale()
    print("Fine grid size:", img.fine_size)
    print("Fine grid scale:", img.fine_scale)

#    fine = img.get_fine_square(8, 8)
#    fine.show()

    test = Image.new("RGBA", img._image.size, color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(test)
    fine_width, fine_height = img.fine_size
    for x in range(int(fine_width)):
        for y in range(int(fine_height)):
            color = tuple(img.get_fine_color(x, y))
            if not (color[0] > 240 and color[1] > 240 and color[2] > 240):
                draw.rectangle((x * img.fine_scale, y * img.fine_scale,
                            (x + 1) * img.fine_scale, 
                            (y + 1) * img.fine_scale), fill=color)
                print(color)
    test.show()

if __name__ == '__main__':
    main()
