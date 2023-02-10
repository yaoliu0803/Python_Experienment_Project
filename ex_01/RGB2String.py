# 图片转字符画：
# 可以使用灰度值公式, 将rgb图像值映射到灰度值范围(0,255). 白色为255，黑色为0
# gray = 0.2126 * r + 0.7152 * b +0.0722 * b

import os
from PIL import Image


# 定义RGB值转字符的函数：
def get_char(r, g, b, alpha=256):
    # rgb转灰度值：
    # gray = int(0.2126 * r + 0.7152 * g + 0.0722 * b)
    gray = (2126 * r + 7152 * g + 722 * b) / 10000
    # 定义转换字符：
    ascii_char = list("$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~") + \
                 list("<>i!lI;:,\"^`'.")
    # 将256灰度映射到70个字符：gray / 256 = x / len(ascii_char)
    if alpha == 0:
        return " "
    x = int((gray / (alpha + 1.0)) * len(ascii_char))  # 防止除数为0
    return ascii_char[x]


# 将字符画写入文件
def write_file(out_file_name, pix):
    with open(out_file_name, "w", encoding="utf-8") as f:
        f.write(pix)


# 解析图片：
def img_process(file_name="test.jpg", width=80, height=80, out_file_name="test.txt"):
    img = Image.open(file_name)
    img = img.resize(size=(width, height))
    txt = ""  # 存储字符
    for i in range(height):
        for j in range(width):
            # 获取每个点的像素值: 注意png是4通道
            pix = img.getpixel((j, i))
            txt += get_char(*pix)
        txt += "\n"  # 添加换行符，进行换行
    write_file(out_file_name, txt)
    print(txt)


if __name__ == '__main__':
    img_path = "../labfile_image/ascii_dora.png"
    # 在ex_01文件夹下创建文本，保存字符画
    out_filename = "test.txt"
    img_process(file_name=img_path, out_file_name=out_filename)
