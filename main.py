from PIL import Image  # TODO: make seed


class Encryptor:
    def __init__(self):
        self.curpix = None
        self.image = None

    def _text_to_ascii(self, text):
        ascii_seq = []
        for char in text:
            ascii_seq.append(ord(char))
        return ascii_seq

    def _setup_image(self, image_path):
        self.image = Image.open(image_path)
        self.image.load()

    def _get_next_pixel(self):
        if self.curpix is None:
            return (0, 0)

        xsize, ysize = self.image.size
        x, y = self.curpix

        if x < xsize - 1:
            return (x + 1, y)
        else:
            return (0, y + 1)

    def _split_char_to_channels(self, char):
        ascii_char = ord(char)
        bin_char = bin(ascii_char)[2:].rjust(8, "0")
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
        self._setup_image(image_path)
        self.curpix = self._get_next_pixel()

        for char in text:
            pix_rgb = self.image.getpixel(self.curpix)
            encrypted_rgb = self._encrypt_pixel(char, pix_rgb)
            self.image.putpixel(self.curpix, encrypted_rgb)
            self.curpix = self._get_next_pixel()

        self._put_end_symbol()
        self.image.save(encrypted_image_name, "BMP")

    def _put_end_symbol(self):
        pix_rgb = self.image.getpixel(self.curpix)
        encrypted_rgb = self._encrypt_pixel("\0", pix_rgb)
        self.image.putpixel(self.curpix, encrypted_rgb)

    def _decrypt_pixel(self, pix_rgb):
        pix_rgb = list(pix_rgb)
        pix_rgb = [bin(i)[2:] for i in pix_rgb]

        bin_char = pix_rgb[0][-3:] + pix_rgb[1][-2:] + pix_rgb[2][-3:]
        return chr(int(bin_char, 2))

    def decrypt(self, image_path):
        self._setup_image(image_path)
        self.curpix = self._get_next_pixel()

        text = ""
        symbol = ""

        while symbol != "\0":
            rgb = self.image.getpixel(self.curpix)
            symbol = self._decrypt_pixel(rgb)
            text += symbol
            self.curpix = self._get_next_pixel()
        return text


def main():
    enc = Encryptor()

    # enc.encrypt("img.jpg", "Lorem Ipsum", "enc.bmp")
    # print(enc.decrypt("enc.bmp"))

if __name__ == '__main__':
    main()
