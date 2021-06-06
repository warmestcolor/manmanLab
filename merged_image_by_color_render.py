
FILE_DIR = './merge_imgs'  # 待处理文件的目录
EXPORT_DIR = './export_imgs'
# 颜色参考：[red, green, blue] 调色比例，比例相同代表保持原灰度不变；'ORIGIN' 表示原色彩不变
COLOR_CONFIG = {           # 颜色配置
  'PRJ_w535': ([0,1,0], 1), # (调色比例, 权重)
  'REF_w-50': ('ORIGIN', 1),
}

import os
import numpy as np
# import matplotlib.pyplot as plt
from PIL import Image

def to_255(image):
  npArr = np.array(image)
  # to 255
  pmin = npArr.min()
  pmax = npArr.max()
  rescale = (npArr - pmin) / (pmax - pmin) * 255
  return rescale.astype(np.uint8)

def rgb2gray(rgb): # RGB->灰度转换
  return np.dot(rgb[...,:3], [0.2989, 0.5870, 0.1140])

def do_merge(file_dir, file_key, export_dir):
  print('start file: ' + file_key + '{}.tif')
  images = []
  size = None
  for type in COLOR_CONFIG.keys():
    (color_ratio, weight) = COLOR_CONFIG[type]
    file_path = os.path.join(file_dir, file_key + type + '.tif')
    # image = mpimg.imread(file_path)
    image = Image.open(file_path).convert('RGBA')
    # image.show()
    size = image.size
    if color_ratio == 'ORIGIN':
      imgArr = np.asarray(image)
    else:
      imgArr = rgb2gray(np.asarray(image))
    # plt.imshow(imgArr,cmap=plt.get_cmap('gray'),vmin=0, vmax=1)
    # plt.show()
    # print(imgArr)
    images.append((imgArr, color_ratio, weight))

  # start merge
  (height, width) = size
  target = np.zeros((height, width, 3))
  # image_ratio = 1 / len(images)
  for (image, color_ratio, weight) in images:
    if color_ratio == 'ORIGIN':
      # print('>> ORIGIN COLOR')
      for i in range(target.shape[0]):
          for j in range(target.shape[1]):
            [r,g,b,a] = image[i,j]
            origin_values = target[i, j]
            # target[i, j] = origin_values + [r,g,b]
            target[i, j] = origin_values + [r*weight,g*weight,b*weight]
    else:
      # print('COLOR RATIO:', color_ratio)
      total = color_ratio[0] + color_ratio[1] + color_ratio[2]
      red = (color_ratio[0] / total) * weight
      green = (color_ratio[1] / total) * weight
      blue = (color_ratio[2] / total) * weight

      for i in range(target.shape[0]):
          for j in range(target.shape[1]):
            grey_value = image[i,j]
            origin_values = target[i, j]
            target[i, j] = origin_values + [grey_value*red, grey_value*green, grey_value*blue]

  # print(target)
  # plt.imshow(target, vmin=0, vmax=1)
  # plt.show()
  result = Image.fromarray(to_255(target), 'RGB')
  result_path = os.path.join(export_dir, file_key + 'merged.tif')
  result.save(result_path)
  print('merged file: ' + result_path)


def start(file_dir, export_dir):
  file_keys = []
  file_types = COLOR_CONFIG.keys()
  # load files
  for file in os.listdir(file_dir):
    if file.endswith(".tif"):
      file_prefix = file
      for type in file_types:
        if type in file_prefix:
          file_prefix = file_prefix.replace(type+'.tif', '')
        else:
          continue
      # file_path = os.path.join(file_dir, file)
      # print('current_file: ', file_path)
      if file_prefix not in file_keys:
        file_keys.append(file_prefix)
  # pair
  # test: do_merge(file_dir, file_keys[0])
  for filekey in file_keys:
    do_merge(file_dir, filekey, export_dir)


start(FILE_DIR, EXPORT_DIR)
