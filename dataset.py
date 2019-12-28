import numpy as np
import torch
import skimage
from skimage import transform
import matplotlib.pyplot as plt
import os


class Dataset(torch.utils.data.Dataset):
    """
    dataset of image files of the form 
       stuff<number>_trans.pt
       stuff<number>_density.pt
    """

    def __init__(self, data_dir, direction='A2B', data_type='float32', index_slice=None, transform=None):
        self.data_dir = data_dir
        self.transform = transform
        self.direction = direction
        self.data_type = data_type

        lst_data = os.listdir(data_dir)

        # f_trans = [f for f in os.listdir(data_dir) if f.startswith('input')]
        # f_trans.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
        #
        # f_density = [f for f in os.listdir(data_dir) if f.startswith('label')]
        # f_density.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))

        if index_slice:
            lst_data = lst_data[index_slice]
            # f_trans = f_trans[index_slice]
            # f_density = f_density[index_slice]

        # self.names = (f_trans, f_density)
        self.names = lst_data

    def __getitem__(self, index):
        # data = plt.imread(os.path.join(self.data_dir, self.names[index])).astype(np.float32)
        data = skimage.io.imread(os.path.join(self.data_dir, self.names[index]), as_gray=True)
        # x = torch.load(os.path.join(self.data_dir, self.names[0][index]))
        # y = torch.load(os.path.join(self.data_dir, self.names[1][index]))
        # x = np.load(os.path.join(self.data_dir, self.names[0][index]))
        # y = np.load(os.path.join(self.data_dir, self.names[1][index]))
        # x = x.to(self.device)
        # y = y.to(self.device)

        if data.ndim == 2:
            data = np.expand_dims(data, axis=2)

        # sz = int(data.shape[0]/2)
        #
        # if self.data_type == 'float32':
        #     dataA = data[:, :sz, :].astype(np.float32)
        #     dataB = data[:, sz:, :].astype(np.float32)
        #
        # # x = np.expand_dims(np.expand_dims(x, axis=1), axis=2)
        # # y = np.expand_dims(np.expand_dims(y, axis=1), axis=2)
        #
        # if self.direction == 'A2B':
        #     data = {'dataA': dataA, 'dataB': dataB}
        # else:
        #     data = {'dataA': dataB, 'dataB': dataA}

        if self.transform:
            data = self.transform(data)

        return data

    def __len__(self):
        return len(self.names)


class ToTensor(object):
    """Convert ndarrays in sample to Tensors."""

    def __call__(self, data):
        # Swap color axis because numpy image: H x W x C
        #                         torch image: C x H x W

        # for key, value in data:
        #     data[key] = torch.from_numpy(value.transpose((2, 0, 1)))
        #
        # return data

        # dataA, dataB = data['dataA'], data['dataB']
        # dataA = dataA.transpose((2, 0, 1)).astype(np.float32)
        # dataB = dataB.transpose((2, 0, 1)).astype(np.float32)
        # return {'dataA': torch.from_numpy(dataA), 'dataB': torch.from_numpy(dataB)}

        data = data.transpose((2, 0, 1)).astype(np.float32)
        return torch.from_numpy(data)

class Normalize(object):
    def __call__(self, data):
        # Nomalize [0, 1] => [-1, 1]

        # for key, value in data:
        #     data[key] = 2 * (value / 255) - 1
        #
        # return data

        # dataA, dataB = data['dataA'], data['dataB']
        # dataA = 2 * (dataA / 255) - 1
        # dataB = 2 * (dataB / 255) - 1
        # return {'dataA': dataA, 'dataB': dataB}

        data = 2 * (data / 255) - 1
        return data

class RandomFlip(object):
    def __call__(self, data):
        # Random Left or Right Flip

        # for key, value in data:
        #     data[key] = 2 * (value / 255) - 1
        #
        # return data
        # dataA, dataB = data['dataA'], data['dataB']
        #
        # if np.random.rand() > 0.5:
        #     dataA = np.fliplr(dataA)
        #     dataB = np.fliplr(dataB)
        #
        # # if np.random.rand() > 0.5:
        # #     dataA = np.flipud(dataA)
        # #     dataB = np.flipud(dataB)
        #
        # return {'dataA': dataA, 'dataB': dataB}

        if np.random.rand() > 0.5:
            data = np.fliplr(data)

        return data


class Rescale(object):
  """Rescale the image in a sample to a given size

  Args:
    output_size (tuple or int): Desired output size.
                                If tuple, output is matched to output_size.
                                If int, smaller of image edges is matched
                                to output_size keeping aspect ratio the same.
  """

  def __init__(self, output_size):
    assert isinstance(output_size, (int, tuple))
    self.output_size = output_size

  def __call__(self, data):
    # dataA, dataB = data['dataA'], data['dataB']
    #
    # h, w = dataA.shape[:2]

    h, w = data.shape[:2]

    if isinstance(self.output_size, int):
      if h > w:
        new_h, new_w = self.output_size * h / w, self.output_size
      else:
        new_h, new_w = self.output_size, self.output_size * w / h
    else:
      new_h, new_w = self.output_size

    new_h, new_w = int(new_h), int(new_w)

    # dataA = transform.resize(dataA, (new_h, new_w))
    # dataB = transform.resize(dataB, (new_h, new_w))
    #
    # return {'dataA': dataA, 'dataB': dataB}

    data = transform.resize(data, (new_h, new_w))
    return data

class CenterCrop(object):
  """Crop randomly the image in a sample

  Args:
    output_size (tuple or int): Desired output size.
                                If int, square crop is made.
  """

  def __init__(self, output_size):
    assert isinstance(output_size, (int, tuple))
    if isinstance(output_size, int):
      self.output_size = (output_size, output_size)
    else:
      assert len(output_size) == 2
      self.output_size = output_size

  def __call__(self, data):
    # dataA, dataB = data['dataA'], data['dataB']
    #
    # h, w = dataA.shape[:2]

    h, w = data.shape[:2]

    new_h, new_w = self.output_size

    top = int(abs(h - new_h) / 2)
    left = int(abs(w - new_w) / 2)

    # dataA = dataA[top: top + new_h, left: left + new_w]
    # dataB = dataB[top: top + new_h, left: left + new_w]
    #
    # return {'dataA': dataA, 'dataB': dataB}

    data = data[top: top + new_h, left: left + new_w]

    return data


class RandomCrop(object):
  """Crop randomly the image in a sample

  Args:
    output_size (tuple or int): Desired output size.
                                If int, square crop is made.
  """

  def __init__(self, output_size):
    assert isinstance(output_size, (int, tuple))
    if isinstance(output_size, int):
      self.output_size = (output_size, output_size)
    else:
      assert len(output_size) == 2
      self.output_size = output_size

  def __call__(self, data):
    # dataA, dataB = data['dataA'], data['dataB']
    #
    # h, w = dataA.shape[:2]

    h, w = data.shape[:2]

    new_h, new_w = self.output_size

    top = np.random.randint(0, h - new_h)
    left = np.random.randint(0, w - new_w)

    # dataA = dataA[top: top + new_h, left: left + new_w]
    # dataB = dataB[top: top + new_h, left: left + new_w]
    #
    # return {'dataA': dataA, 'dataB': dataB}

    data = data[top: top + new_h, left: left + new_w]
    return data

class ToNumpy(object):
    """Convert ndarrays in sample to Tensors."""

    def __call__(self, data):
        # Swap color axis because numpy image: H x W x C
        #                         torch image: C x H x W

        # for key, value in data:
        #     data[key] = value.transpose((2, 0, 1)).numpy()
        #
        # return data

        data.to('cpu').detach().numpy()

        if data.ndim == 3:
            data.transpose(1, 2, 0)
        elif data.ndim == 4:
            data.transpose(0, 2, 3, 1)

        return data

        # input, label = data['input'], data['label']
        # input = input.transpose((2, 0, 1))
        # label = label.transpose((2, 0, 1))
        # return {'input': input.detach().numpy(), 'label': label.detach().numpy()}


class Denomalize(object):
    def __call__(self, data):
        # Denomalize [-1, 1] => [0, 1]

        # for key, value in data:
        #     data[key] = (value + 1) / 2 * 255
        #
        # return data

        return (data + 1) / 2

        # input, label = data['input'], data['label']
        # input = (input + 1) / 2 * 255
        # label = (label + 1) / 2 * 255
        # return {'input': input, 'label': label}