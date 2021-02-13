# 2021-02-13

import h5py
import numpy as np
import os
import SimpleITK as sitk

# 将 ims 影像文件导出为适当的图片进行存储

# init args
file_path = 'ims/YMY128X134_F2-1-T.ims' # 原文件路径
export_prefix = 'YMY128X134_F2-1-'      # 导出文件前缀
export_dir = 'exports'                  # 导出文件夹

def export():

  # create export dir
  if not os.path.exists(export_dir):
    print('create folder: ', export_dir)
    os.mkdir(export_dir)

  imsFile = h5py.File(file_path, 'r')

  info = imsFile['DataSetInfo']['Image']

  # 影像实际大小
  ext0 = float(info.attrs['ExtMax0'].tobytes()) - float(info.attrs['ExtMin0'].tobytes())
  ext1 = float(info.attrs['ExtMax1'].tobytes()) - float(info.attrs['ExtMin1'].tobytes())
  ext2 = float(info.attrs['ExtMax2'].tobytes()) - float(info.attrs['ExtMin2'].tobytes())
  unit = info.attrs['Unit'].tobytes().decode('utf-8')
  print("Real Size: {} x {} x {} {}".format(ext0, ext1, ext2, unit))
  # 原始影像大小
  xPixels = int(info.attrs['X'].tobytes())
  yPixels = int(info.attrs['Y'].tobytes())
  zPixels = int(info.attrs['Z'].tobytes())
  print("Image Size: {} x {} x {} pixels".format(xPixels, yPixels, zPixels))

  def to_255(image):
    npArr = np.array(image)
    # to 255
    pmin = npArr.min()
    pmax = npArr.max()
    rescale = (npArr - pmin) / (pmax - pmin) * 255
    return rescale.astype(np.uint8)

  def write_file(image, voxelSize, export_file_path):
    sitkImage = sitk.GetImageFromArray(image)
    sitkImage.SetSpacing(voxelSize)
    sitk.WriteImage(sitkImage, export_file_path)

  # start reading...
  resolution_level_keys = list(imsFile['DataSet'].keys())
  for resolution_level_key in resolution_level_keys:
    time_point_keys = list(imsFile['DataSet'][resolution_level_key])
    for time_point_key in time_point_keys:
      channel_keys = list(imsFile['DataSet'][resolution_level_key][time_point_key])
      for channel_key in channel_keys:
        channel = imsFile['DataSet'][resolution_level_key][time_point_key][channel_key] # ['Data', 'Histogram', 'Histogram1024']
        # print('processing...', channel)
        rawdata = channel['Data']
        imageSizeX = int(channel.attrs['ImageSizeX'].tobytes())
        imageSizeY = int(channel.attrs['ImageSizeY'].tobytes())
        imageSizeZ = int(channel.attrs['ImageSizeZ'].tobytes())
        voxelSize = (imageSizeX, imageSizeY, imageSizeZ)
        image = rawdata[:imageSizeZ, :imageSizeY, :imageSizeX]
        
        imageUInt8 = to_255(image)

        # save file
        resolution_name = resolution_level_key.split(' ')[1]
        dir_path = export_dir + '/resolution_' + resolution_name
        if not os.path.exists(dir_path):
          os.mkdir(dir_path)

        # as: YMY128X134_F2-1-T9-YFP
        timepoint_name = 'T' + str(int(time_point_key.split(' ')[1]) + 1)
        channel_name = ['mCherry', 'BF', 'CFP', 'YFP'][int(channel_key.split(' ')[1])]
        filepath_prefix = dir_path + '/' + export_prefix + timepoint_name + '-' + channel_name
        
        # save the 7 photos
        # for i in range(len(imageUInt8)):
        #   export_file_path = filepath_prefix + '_' + str(i) + '.tiff'
        #   # 從 NumPy 轉為 SimpleITK 影像
        #   write_file(imageUInt8, voxelSize, export_file_path)

        # save merged photo
        mergedImageUInt8 = to_255(merge(image))
        export_merged_file_path = filepath_prefix + '_Merge.tiff'
        write_file(mergedImageUInt8, voxelSize, export_merged_file_path)

        print('file export success: ', filepath_prefix)

  print('Done!')

def merge(imageArrs):
  # 聪明的我肯定只用了求平均的算法来做 merge，更多方法参考：https://docs.newvfx.com/docs/7132.html
  image = imageArrs[0]
  for i in range(1, len(imageArrs)):
    image = image + imageArrs[i]
  return image

# run it
export()
