""" ENCRYPTING PRINCIPLE
Каждый символ переводится в ASCII-число, затем в двоичную СС
RGB каналы пикселя также переводятся в двоичную СС

Двоичное представление числа делится на 3 части:
3, 2, 3 бита на каждый канал соответственно

Далее эти части вставляются в младшие разряды двоичного представления
каждого канала
"""

from PIL import Image  # TODO: make seed
import os
from sys import platform
import sys
import random as rd


class Encryptor:
    def __init__(self):
        self.curpix = None
        self.image = None
        self.used_pixels = []

    def _setup(self, image_path, seed):
        self.image = Image.open(image_path)
        self.image.load()
        self.used_pixels = []
        rd.seed(seed)

    def _get_next_pixel(self):
        xsize, ysize = self.image.size

        curpix = (rd.randint(0,xsize-1),rd.randint(0,ysize-1))
        while curpix in self.used_pixels:
            curpix = (rd.randint(0,xsize-1),rd.randint(0,ysize-1))
        self.used_pixels.append(curpix)
        return curpix

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

    def encrypt(self, image_path, text, encrypted_image_name, seed):
        self._setup(image_path, seed)
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

    def decrypt(self, image_path, seed):
        self._setup(image_path, seed)
        self.curpix = self._get_next_pixel()

        text = ""
        symbol = ""

        while symbol != "\0":
            rgb = self.image.getpixel(self.curpix)
            symbol = self._decrypt_pixel(rgb)
            text += symbol
            self.curpix = self._get_next_pixel()
        return text


class ConsoleUI():
    def __init__(self):
        self.enc = Encryptor()
        self.PROGRAM_OPTIONS = {"encrypt": self._encrypt_UI,
                                "decrypt": self._decrypt_UI}
        self.TEXT_INPUT_OPTIONS = {"manual text input": self._input_text,
                                "load text from file": self._text_from_file}
        self.TEXT_OUTPUT_OPTIONS = {"console output": self._print_text,
                                     "file output": self._file_output}

    def run(self):
        self._clearwin()
        print("Welcome to Picture Encryptor")
        print("All files should be "
              "in the same directory as this program")
        self._run_menu(self.PROGRAM_OPTIONS)

    def _run_menu(self, options_dict, *args):
        """Runs menu where user choosing option, then run fucntion
        providing this option. Also passes option arguments if needed.
        """
        print("\nEnter number of option:")
        for i in range(len(options_dict)):
            print(f"{i+1} - {list(options_dict.keys())[i]}")

        valid_inputs = [str(i) for i in range(1, len(options_dict)+ 1)]

        user_choice = input(": ")
        while user_choice not in valid_inputs:
            print("Incorrect input!")
            user_choice = input(": ")

        return list(options_dict.values())[int(user_choice)-1](*args)

    def _encrypt_UI(self):
        self._clearwin()
        image_name = input("Enter picture name: ")
        text = self._run_menu(self.TEXT_INPUT_OPTIONS)
        seed = input("\nEnter seed: ")
        output_image = input("\nEnter encrypted image filename: ")

        print("\nEncrypting...")
        self.enc.encrypt(image_name, text, output_image, seed)
        print("Encrypting completed successfully!")
        os.system("pause")
        self._clearwin()
        sys.exit()

    def _decrypt_UI(self):
        self._clearwin()
        image_name = input("Enter picture name: ")
        seed = input("\nEnter seed: ")
        print("Decrypting...")
        text = self.enc.decrypt(image_name, seed)
        print("Decrypting completed successfully!")

        self._run_menu(self.TEXT_OUTPUT_OPTIONS, text)
        os.system("pause")
        self._clearwin()
        sys.exit()

    def _input_text(self):
        return input("\nEnter text: ")

    def _text_from_file(self):
        filename = input("\nEnter filename: ")
        with open(filename, "r") as f:
            text = f.read()

        return text

    def _print_text(self, text):
        print(f"\nTEXT BELOW\n{text}")

    def _file_output(self, text):
        filename  = input("\nEnter output file name: ")
        with open(filename, "w") as f:
            f.write(text)
        print(f"Text was written to {filename}")

    def _clearwin(self):
        if platform == "win32":
            os.system("cls")
        elif platform in ("linux", "darwin"):
            os.system("clear")
        else:
            print("Error: unknown OS")


def main():
    UI = ConsoleUI()
    UI.run()


if __name__ == '__main__':
    main()
