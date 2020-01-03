from random import Random


class RotModificated:
    __CHANGE_ENG_LETTERS = "ĒđįĮ¦ěĚę¹ģĢġĠİĎº¼īĪĩĨħ½ĘėĖĕĔē¾×ï÷ÿ¤¨¢´µ¶·¸ĐğĞĝĜĭĬĦĥĤ"
    __CHANGE_RUS_LETTERS = "¥£ÀÐàðÁÑáñòâÒÂÃÓãóôäÔÄõåÕÅÆÖæöÇçøè¡©®ØÈÉÙéùúÊÚêûËëÛÌìüÜÝÍýíþîÞÎÏß¿"
    __RUSS_ALPH = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    __ENGL_ALPH = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    __ENCR_NUM = "ƛƞƗƕƍƄƀƾƱƏ"
    __DIGITS = "0123456789"
    __CRYPT_NUM = 0
    __CRYPT_WORD = ""

    def __init__(self, crypt_word: str, crypt_num: int):
        self.__CRYPT_WORD = crypt_word
        self.__CRYPT_NUM = crypt_num

    def encrypt(self, str_text: str):
        iterator = 31
        encrypt_txt = ""
        shift_symb_dynamically = 2
        crypt_word_len = len(self.__CRYPT_WORD)
        shift_n = 1
        for i in str_text:
            shift_n, iterator = self.__shift_count(shift_n, crypt_word_len, iterator)
            if 1040 <= ord(i) <= 1103 or i == 'ё' or i == 'Ё':
                shift_n %= 66
                encrypt_txt += self.__CHANGE_RUS_LETTERS[(self.__RUSS_ALPH.index(i) + shift_n) % 66]
            elif 'A' <= i <= 'Z' or 'a' <= i <= 'z':
                shift_n %= 52
                encrypt_txt += self.__CHANGE_ENG_LETTERS[(self.__ENGL_ALPH.index(i) + shift_n) % 52]
            elif 48 <= ord(i) <= 57:
                encrypt_txt += self.__ENCR_NUM[(ord(i) % 48 + shift_n) % 10]
            else:
                encrypt_txt += i
                shift_n -= shift_symb_dynamically
            shift_n += shift_symb_dynamically
        return encrypt_txt

    def decipher(self, str_text: str):
        iterator = 31
        decrypt = ""
        shift_symb_dynamically = 2
        shift_n = 1
        crypt_word_len = len(self.__CRYPT_WORD)
        for i in str_text:
            shift_n, iterator = self.__shift_count(shift_n, crypt_word_len, iterator)
            if i in self.__CHANGE_RUS_LETTERS:
                shift_n %= 66
                temp = self.__CHANGE_RUS_LETTERS.index(i)
                if temp - shift_n < 0:
                    decrypt += self.__RUSS_ALPH[temp + 66 - shift_n]
                else:
                    decrypt += self.__RUSS_ALPH[temp - shift_n]
            elif i in self.__CHANGE_ENG_LETTERS:
                shift_n %= 52
                temp = self.__CHANGE_ENG_LETTERS.index(i)
                if temp - shift_n < 0:
                    decrypt += self.__ENGL_ALPH[temp + 52 - shift_n]
                else:
                    decrypt += self.__ENGL_ALPH[temp - shift_n]
            elif i in self.__ENCR_NUM:
                temp = self.__ENCR_NUM.index(i)
                if temp - shift_n % 10 < 0:
                    decrypt += self.__DIGITS[temp + 10 - shift_n % 10]
                else:
                    decrypt += self.__DIGITS[temp - shift_n % 10]
            else:
                decrypt += i
                shift_n -= shift_symb_dynamically
            shift_n += shift_symb_dynamically
        return decrypt

    def __shift_count(self, shift_n: int, crypt_word_len: int, iterator: int):
        flg = True
        if self.__CRYPT_NUM != 0:
            rnd = Random(self.__CRYPT_NUM)
            shift_n += rnd.randint(1, 9)
        if crypt_word_len != 0:
            shift_n += ord(self.__CRYPT_WORD[iterator % crypt_word_len]) % 33
        if shift_n > 55:
            if iterator <= 0:
                flg = False
            elif iterator > 41:
                flg = True
            shift_n -= iterator
            if flg:
                iterator -= 2
            else:
                iterator += 3
        return shift_n, iterator


# if __name__ == '__main__':
#     cipher = RotModificated('привет', 10)
#     str1 = cipher.encrypt('Привет мир Hello world 123 !@#$%^&*()_')
#     print(str1)
#     print(cipher.decipher(str1))
