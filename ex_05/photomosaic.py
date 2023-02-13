import os
from PIL import Image


# 读入小块图像：
def getImages(imageDir):
    """
       从给定目录里加载所有替换图像
       @param {str} imageDir 目录路径
       @return {List[Image]} 替换图像列表
    """
    files = os.listdir(imageDir)  # 调用 os.listdir() 将 imageDir 目录中的文件放入一个列表
    images = []
    # 迭代遍历列表中的每个文件，将它载入为一个 PIL Image 对象:
    for file in files:
        # os.path.abspath()和 os.path.join()来获取图像的完整文件名
        # 以确保代码既能在相对路径下工作（如 foo\bar)，也能在绝对路径下工作，并且能跨操作系统，不同的操作系统有不同的目录命名惯例（Windows 用 \ 而 Linux 用 /)
        # 得到文件绝对路径:
        filePath = os.path.abspath(os.path.join(imageDir, file))
        """ 要将文件加载为PIL的Image对象，可以将每个文件名传入Image.open()方法，
        但如果照片马赛克文件夹中有几百张甚至几千张图片，这样做非常消耗系统资源。
        作为替代，可以用Python分别打开每个小块图像，利用Image.open()将文件句柄fp传入PIL。
        图像加载完成后，立即关闭文件句柄释放系统资源"""
        try:
            fp = open(filePath, "rb")  # open() 是一个惰性操作，所以接下来需要强制调用 Image.load()，强制 im 加载文件中的图像数据
            im = Image.open(fp)  # Image.open() 确定了图像，但它实际上没有读取全部图像数据，直到使用该图像时才会那么做
            images.append(im)
            im.load()
            # 用完关闭文件，防止资源泄露
            fp.close()
        except:
            # 加载某个图像识别，出现异常时直接跳过
            print("Invalid image: %s" % (filePath,))

    return images


# 计算输入图像的平均颜色值：
def getAverageRGB(image):
    """
        计算图像的平均 RGB 值
        将图像包含的每个像素点的 R、G、B 值分别累加，然后除以像素点数，就得到图像的平均 R、G、B
        值
        @param {Image} image PIL Image 对象
        @return {Tuple[int, int, int]} 平均 RGB 值
    """
    # 计算像素点数：
    npixels = image.size[0] * image.size[1]
    # 获得图像包含的每种颜色及其计数，结果类似
    # 返回结果是一个元祖，每个元素的格式如下： (44, (72, 64, 55, 255))，其中(72,64,55,255)表示RGBA颜色，A就是透明度，44表示outofmemory.cn.png这张图片中包含了44个这种颜色。
    # [(c1, (r1, g1, b1)), (c2, (r2, g2, b2)), ...]
    cols = image.getcolors(npixels)
    # 获得每种颜色的 R、G、B 累加值，结果类似
    # [(c1 * r1, c1 * g1, c1 * b1), (c2 * r2, c2 * g2, c2 * b2), ...]
    sumRGB = [(x[0] * x[1][0], x[0] * x[1][1], x[0] * x[1][2]) for x in cols]
    # 先用 zip 方法对 sumRGB 列表里的元组对象按列进行合并，结果类似
    # [(c1 * r1, c2 * r2, ...), (c1 * g1, c2 * g2, ...),
    # (c1 * b1, c2 * b2, ...)]
    # 然后计算所有颜色的 R、G、B 平均值，算法为
    # (sum(ci * ri) / np, sum(ci * gi) / np, sum(ci * bi) / np)
    avg = tuple([int(sum(x) / npixels) for x in zip(*sumRGB)])
    return avg


# 将目标图像分割成网络
def splitImage(image, size):
    W, H = image.size[0], image.size[1]  # 得到目标图像的维度
    m, n = size  # 得到尺寸
    w, h = int(W / m), int(H / n)  # 计算目标图像中每一小块的尺寸
    imgs = []
    # 先按行再按列裁剪出 m * n 个小图像
    for j in range(m):
        for i in range(n):
            # 根据网格的维度进行迭代遍历，分割并将每一小块保存为单独的图像:
            # image.crop() 利用左上角图像坐标和裁剪图像的维度作为参数，裁剪出图像的一部分
            imgs.append(image.crop((i * w, j * h, (i + 1) * w, (j + 1) * h)))
    return imgs


# 寻找小块的最佳匹配:
def getBestMatchIndex(input_avg, avgs):
    """
        找出颜色值最接近的索引
        把颜色值看做三维空间里的一个点，依次计算目标点跟列表里每个点在三维空间里的距离，从而得到距
        离最近的那个点的索引。
        @param {Tuple[int, int, int]} input_avg 目标颜色值
        @param {List[Tuple[int, int, int]]} avgs 要搜索的颜色值列表
        @return {int} 命中元素的索引
    """
    index = 0
    min_index = 0
    min_dist = float("inf")
    for val in avgs:
        # 三维空间两点距离计算公式 (x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2)
        # + (z1 - z2) * (z1 - z2)，这里只需要比较大小，所以无需求平方根值
        dist = ((val[0] - input_avg[0]) * (val[0] - input_avg[0]) +
                (val[1] - input_avg[1]) * (val[1] - input_avg[1]) +
                (val[2] - input_avg[2]) * (val[2] - input_avg[2]))
        if dist < min_dist:
            min_dist = dist
            min_index = index
        index += 1

    return min_index


# 创建图像网格：往这个网格中填入小块图像，就可以创建出照片马赛克
def createImageGrid(images, dims):
    """
        将图像列表里的小图像按先行后列的顺序拼接为一个大图像

        @param {List[Image]} images 小图像列表
        @param {Tuple[int, int]} dims 大图像的行数和列数
        @return Image 拼接得到的大图像
    """
    m, n = dims
    assert m * n == len(images)
    # 计算所有小图像的最大宽度和高度
    width = max([img.size[0] for img in images])
    height = max([img.size[1] for img in images])

    # 创建大图像对象:
    grid_img = Image.new("RGB", (n * width, m * height))  # 创建一个空的 Image，大小符合网格中的所有图像,小块图像会粘贴到这个图像，填充图像网格

    # 依次将每个小图像粘贴到大图像里:
    for index in range(len(images)):
        # 计算要粘贴到网格的哪行
        row = int(index / n)
        # 计算要粘贴到网格的哪列
        col = index - n * row
        # 根据行列数以及网格的大小得到网格的左上角坐标，把小图像粘贴到这里
        grid_img.paste(images[index], (col * width, row * height))

    return grid_img


# 创建照片马赛克:
def createPhotomosaic(target_image, input_images, grid_size,
                      reuse_images=True):
    """
    图片马赛克生成

    @param {Image} target_image 目标图像
    @param {List[Image]} input_images 替换图像列表
    @param {Tuple[int, int]} grid_size 网格行数和列数
    @param {bool} reuse_images 是否允许重复使用替换图像
    @return {Image} 马赛克图像
    """

    # 将目标图像切成网格小图像
    print('splitting input image...')
    target_images = splitImage(target_image, grid_size)

    # 为每个网格小图像在替换图像列表里找到颜色最相似的替换图像
    print('finding image matches...')
    output_images = []
    # 分 10 组进行，每组完成后打印进度信息，避免用户长时间等待
    count = 0
    batch_size = int(len(target_images) / 10)

    # 计算替换图像列表里每个图像的颜色平均值
    avgs = []
    for img in input_images:
        avgs.append(getAverageRGB(img))

    # 对每个网格小图像，从替换图像列表找到颜色最相似的那个，添加到 output_images 里
    for img in target_images:
        # 计算颜色平均值
        avg = getAverageRGB(img)
        # 找到最匹配的那个小图像，添加到 output_images 里
        match_index = getBestMatchIndex(avg, avgs)
        output_images.append(input_images[match_index])
        # 如果完成了一组，打印进度信息
        if count > 0 and batch_size > 10 and count % batch_size == 0:
            print('processed %d of %d...' % (count, len(target_images)))
        count += 1
        # 如果不允许重用替换图像，则用过后就从列表里移除
        if not reuse_images:
            input_images.remove(match_index)

    # 将 output_images 里的图像按网格大小拼接成一个大图像
    print('creating mosaic...')
    mosaic_image = createImageGrid(output_images, grid_size)

    return mosaic_image


def main(target_image, input_folder, grid_size, outfile):
    # # 定义程序接收的命令行参数
    # parser = argparse.ArgumentParser(
    #     description='Creates a photomosaic from input images')
    # parser.add_argument('--target-image', dest='target_image', required=True)
    # parser.add_argument('--input-folder', dest='input_folder', required=True)
    # parser.add_argument('--grid-size', nargs=2,
    #                     dest='grid_size', required=True)
    # parser.add_argument('--output-file', dest='outfile', required=False)
    #
    # # 解析命令行参数
    # args = parser.parse_args()

    # 网格大小
    grid_size = (int(grid_size[0]), int(grid_size[1]))

    # 马赛克图像保存路径，默认为 mosaic.png
    output_filename = 'mosaic.png'
    if outfile:
        output_filename = outfile

    # 打开目标图像
    print('reading targe image...')
    target_image = Image.open(target_image)

    # 从指定文件夹下加载所有替换图像
    print('reading input images...')
    input_images = getImages(input_folder)
    # 如果替换图像列表为空则退出程序
    if input_images == []:
        print('No input images found in %s. Exiting.' % (input_folder,))
        exit()

    # 将所有替换图像缩放到指定的网格大小
    print('resizing images...')
    dims = (int(target_image.size[0] / grid_size[1]),
            int(target_image.size[1] / grid_size[0]))
    for img in input_images:
        img.thumbnail(dims)

    # 生成马赛克图像
    print('starting photomosaic creation...')
    mosaic_image = createPhotomosaic(target_image, input_images, grid_size)

    # 保存马赛克图像
    mosaic_image.save(output_filename, 'PNG')
    print("saved output to %s" % (output_filename,))

    print('done.')


if __name__ == '__main__':
    target_image = "../labfile_image/a.jpg"
    input_folder = "../labfile_image/set1"
    grid_size = (100, 100)
    outfile = "./mosaic.png"  # 合成的马赛克图像保存到当前目录下
    main(target_image, input_folder, grid_size, outfile)
