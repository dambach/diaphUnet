# -*- coding: utf-8 -*-
"""U-Net_diaph.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/141kJ75vs-mh-zaQsSmtC8fcl0lrEevkC
"""

import numpy as np                        # pour effectuer des opérations sur les array/tableaux
import torch                              # pour construire le modèle de réseaux de neurones
from torch.optim import Adam              # pour optimiser la fonction perte

def ConvUnet(K_in, K_out, ker = 3, pad = 1):
  conv = torch.nn.Sequential(
      torch.nn.Conv2d(K_in, K_out, kernel_size = ker, stride = 1, 
                      padding = pad, bias = False),
      torch.nn.BatchNorm2d(K_out),
      torch.nn.ReLU(),
      torch.nn.Conv2d(K_out, K_out, kernel_size = ker, stride = 1, 
                      padding = pad, bias = False),
      torch.nn.BatchNorm2d(K_out),
      torch.nn.ReLU(),
      torch.nn.Dropout2d(p = 0.2),
  )
  return conv

def crop_image(img1, img2):
  N_img1 = img1.size(2)
  M_img1 = img1.size(3)

  N_img2 = img1.size(2)
  M_img2 = img2.size(3)

  N_img = N_img1 - N_img2
  N_img = N_img // 2
  M_img = M_img1 - M_img2
  M_img = M_img // 2
  return img1[:,:, N_img:N_img1 - N_img, M_img:M_img1 - M_img]

class U_Net(torch.nn.Module):

    def __init__(self):
        super(U_Net, self).__init__()

        self.pool = torch.nn.MaxPool2d(2, 2)
        C = 16

        #Encoder
        self.conv1 = ConvUnet(1, C)

        self.conv2 = ConvUnet(C, 2*C)

        self.conv3 = ConvUnet(2*C, 4*C)

        self.conv4 = ConvUnet(4*C, 8*C)

        self.conv5 = ConvUnet(8*C, 16*C)

        self.conv6 = ConvUnet(16*C, 32*C)

        #self.conv7 = ConvUnet(4*C, 8*C)

        #self.conv8 = ConvUnet(8*C, 8*C)

        #Decoder
        #self.up_conv1 = torch.nn.ConvTranspose2d(8*C, 8*C, kernel_size = 2, stride = 2)
        #self.conv9 = ConvUnet(16*C, 8*C)

        #self.up_conv2 = torch.nn.ConvTranspose2d(8*C, 4*C, kernel_size = 2, stride = 2)
        #self.conv10 = ConvUnet(8*C, 4*C)

        self.up_conv3 = torch.nn.ConvTranspose2d(32*C, 16*C, kernel_size = 2, stride = 2)
        self.conv11 = ConvUnet(32*C, 16*C)

        self.up_conv4 = torch.nn.ConvTranspose2d(16*C, 8*C, kernel_size = 2, stride = 2)
        self.conv12 = ConvUnet(16*C, 8*C)

        self.up_conv5 = torch.nn.ConvTranspose2d(8*C, 4*C, kernel_size = 2, stride = 2)
        self.conv13 = ConvUnet(8*C, 4*C)

        self.up_conv6 = torch.nn.ConvTranspose2d(4*C, 2*C, kernel_size = 2, stride = 2)
        self.conv14 = ConvUnet(4*C, 2*C)

        self.up_conv7 = torch.nn.ConvTranspose2d(2*C, C, kernel_size = 2, stride = 2)
        self.conv15 = ConvUnet(2*C, C)

        self.conv16 = torch.nn.Conv2d(C, 1, kernel_size = 1)  

    def forward(self, x):
        batch_size, Ch, N, M = x.size()
        C = 16
        
        # Permet de traiter des entrées de tailles quelconques
        k1, k2 = [], []
        kernel = 2*np.ones((5, 2), dtype=int)
        for i in range(5):
          k1.append(int(N/2**i))
          k2.append(int(M/2**i))
          if k1[i] % 2 == 0 and k2[i] % 2 == 0:
            kernel[i,:] = np.array([2, 2])
          elif k1[i] % 2 != 0 and k2[i] % 2 == 0:
            kernel[i,:] = np.array([3, 2])
          elif k1[i] % 2 == 0 and k2[i] % 2 != 0:
            kernel[i,:] = np.array([2, 3])
          elif k1[i] % 2 != 0 and k2[i] % 2 != 0:
            kernel[i,:] = np.array([3, 3])
          else:
            kernel[i,:] = np.array([3, 3])
        
        # Augmente le kernel si l'image est jugée grande 
        if N > 400 or M > 400:
          self.conv1 = ConvUnet(1, C, ker = 5, pad = 2)
          self.conv2 = ConvUnet(C, 2*C, ker = 5, pad = 2)
          self.conv14 = ConvUnet(4*C, 2*C, ker = 5, pad = 2)
          self.conv15 = ConvUnet(2*C, C, ker = 5, pad = 2)

        # Encoder
        x1 = self.conv1(x) # 2 CROP
        pool1 = self.pool(x1) # 114x150 190x150

        x2 = self.conv2(pool1) # 2 CROP
        pool2 = self.pool(x2) # 57x75 95x75

        x3 = self.conv3(pool2) # 4 CROP
        pool3 = self.pool(x3) # 28x37 47x37

        x4 = self.conv4(pool3) # 4 CROP
        pool4 = self.pool(x4) # 14x18 23x18
        
        x5 = self.conv5(pool4) # 8 CROP
        pool5 = self.pool(x5) # 7x9 11x9

        x6 = self.conv6(pool5) # 8 CROP
        #pool6 = self.pool(x6) # 3x4 5x4

        #x7 = self.conv7(pool6) # 16 CROP
        #pool7 = self.pool(x7) # 1x2 2x2

        #x8 = self.conv8(pool7) # 16 CROP

        # Decoder
        #x9 = self.up_conv1(x8) # 3x3
        #y1 = crop_image(x7, x9)
        #x10 = torch.cat((y1, x9), dim = 1)
        #x11 = self.conv9(x10)

        #x12 = self.up_conv2(x11) # 7x6
        #y2 = crop_image(x6, x12)
        #x13 = torch.cat((y2, x12), dim = 1)
        #x14 = self.conv10(x13)
        
        self.up_conv3 = torch.nn.ConvTranspose2d(32*C, 16*C, kernel_size = kernel[-1,:], stride = 2).to(device)
        x15 = self.up_conv3(x6) # 14x18 23x18
        y3 = crop_image(x5, x15)
        x16 = torch.cat((y3, x15), dim = 1)
        x17 = self.conv11(x16)


        self.up_conv4 = torch.nn.ConvTranspose2d(16*C, 8*C, kernel_size = kernel[-2,:], stride = 2).to(device)
        x18 = self.up_conv4(x17) # 28x37 47x37
        y4 = crop_image(x4, x18)
        x19 = torch.cat((y4, x18), dim = 1)
        x20 = self.conv12(x19)

        self.up_conv5 = torch.nn.ConvTranspose2d(8*C, 4*C, kernel_size = kernel[-3,:], stride = 2).to(device)
        x21 = self.up_conv5(x20) # 57x75 95x75
        y5 = crop_image(x3, x21)
        x22 = torch.cat((y5, x21), dim = 1)
        x23 = self.conv13(x22)

        self.up_conv6 = torch.nn.ConvTranspose2d(4*C, 2*C, kernel_size = kernel[-4,:], stride = 2).to(device)
        x24 = self.up_conv6(x23) # 114x150 190x150
        y6 = crop_image(x2, x24)
        x25 = torch.cat((y6, x24), dim = 1)
        x26 = self.conv14(x25)

        self.up_conv7 = torch.nn.ConvTranspose2d(2*C, C, kernel_size = kernel[-5,:], stride = 2).to(device)
        x27 = self.up_conv7(x26) # 228x330 380x300
        y7 = crop_image(x1, x27)
        x28 = torch.cat((y7, x27), dim = 1)
        x29 = self.conv15(x28)
        
        out = self.conv16(x29)
        return out

model = U_Net().to(device)
criterion = torch.nn.BCEWithLogitsLoss()
optimizer = torch.optim.Adam(model.parameters(), lr = 1e-4)