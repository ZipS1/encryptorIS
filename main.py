from PIL import Image # TODO: make seed


class Encryptor:
    def __init__(self):
        self.curpix = (0, 0)

    def _set_to_start(self):
        self.curpix = (0, 0)

    def _text_to_ascii(self, text):
        ascii_seq = []
        for char in text:
            ascii_seq.append(ord(char))
        return ascii_seq

    def _try_get_image(self, image_path):
        image = Image.open(image_path)
        image.load()
        return image

    def _set_next_pixel(self, image):
        xsize, ysize = image.size
        x, y = self.curpix

        if x < xsize - 1:
            self.curpix = (x + 1, y)
        else:
            self.curpix = (0, y + 1)

    def _split_char_to_channels(self, char):
        ascii_char = ord(char)
        bin_char = bin(ascii_char)[2:].rjust(8, "0")  # convert dec to 8 bit bin
        rcomp = bin_char[:3]
        gcomp = bin_char[3:5]
        bcomp = bin_char[5:]
        return (rcomp, gcomp, bcomp)

    def _encrypt_pixel(self, char, pix_rgb):
        ascii_comps = self._split_char_to_channels(char)
        new_rgb = []
        for ch_ind in range(3):
            ascii_comp = ascii_comps[ch_ind]
            bin_channel = bin(pix_rgb[ch_ind])[2:]
            new_channel = bin_channel[:-len(ascii_comp)] + ascii_comp
            new_rgb.append(new_channel)
        new_rgb = [int(i, 2) for i in new_rgb]
        return tuple(new_rgb)

    def encrypt(self, image_path, text, encrypted_image_name):
        self._set_to_start()
        image = self._try_get_image(image_path)

        for char in text:
            pix_rgb = image.getpixel(self.curpix)
            encrypted_rgb = self._encrypt_pixel(char, pix_rgb)
            image.putpixel(self.curpix, encrypted_rgb)
            print(self.curpix, encrypted_rgb)
            self._set_next_pixel(image)

        self._put_end_symbol(image)
        image.save(encrypted_image_name, "BMP")  # quality=100, subsampling=0

    def _put_end_symbol(self, image):
        pix_rgb = image.getpixel(self.curpix)
        encrypted_rgb = self._encrypt_pixel("\0", pix_rgb)
        image.putpixel(self.curpix, encrypted_rgb)

    def _decrypt_pixel(self, pix_rgb):
        pix_rgb = list(pix_rgb)
        pix_rgb = [bin(i)[2:] for i in pix_rgb]

        bin_char = pix_rgb[0][-3:] + pix_rgb[1][-2:] + pix_rgb[2][-3:]
        return chr(int(bin_char, 2))

    def decrypt(self, image_path):
        self._set_to_start()
        image = self._try_get_image(image_path)

        text = ""
        symbol = ""

        while symbol != "\0":
            rgb = image.getpixel(self.curpix)
            symbol = self._decrypt_pixel(rgb)
            text += symbol
            self._set_next_pixel(image)
        return text


if __name__ == '__main__':
    enc = Encryptor()

    enc.encrypt("img.jpg", "Lorem Ipsum", "enc.bmp")
    # print(enc.decrypt("r.jpg"))
