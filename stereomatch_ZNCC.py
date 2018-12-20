#!/usr/bin/env python
# --------------------------------------------------------------------
# Simple sum of squared differences (ZNCC) stereo-matching using Numpy
# --------------------------------------------------------------------

# Copyright (c) 2018 King
# Licensed under the UCAS License
#--------------------------------------------------------------------
#中文注释为我添加的注释
#--------------------------------------------------------------------
import numpy as np
import math
from PIL import Image
import sys,time#为了打印进度条

def stereo_match(left_img, right_img, kernel, max_offset):
    # Load in both images, assumed to be RGBA 8bit per channel images
    left_img = Image.open(left_img).convert('L')#图像打开
    left = np.asarray(left_img)#处理为二维数组
    right_img = Image.open(right_img).convert('L')#图像打开
    right = np.asarray(right_img)#处理为二维数组    
    w, h = left_img.size  # assume that both images are same size  
    left_eq = 0
    right_eq = 0 
    left_eq = np.mean(left) #窗口像素均值
    right_eq = np.mean(right)
    
    # Depth (or disparity) map
    depth = np.zeros((w, h), np.uint8)#初始化深度图像
    depth.shape = h, w
       
    kernel_half = int(kernel / 2)    
    offset_adjust = 255 / max_offset  # this is used to map depth map output to 0-255 range
    
    #for v in range(-kernel_half, kernel_half):
    #    for u in range(-kernel_half, kernel_half):
    #        left_eq+=left[v,u]
    #        right_eq+=right[v,u]

    #left_eq=left_eq/(kernel*kernel)
    #right_eq=right_eq/(kernel*kernel)
    #---------------MY CODE-------------------------------
    for y in range(kernel_half, h - kernel_half):      
        i=int(100*(y-kernel_half)/(h-2*kernel_half))
        k = i + 1
        str ="[KING-ZNCC]" + '■'*(i//2)+' '*((100-k)//2)
        sys.stdout.write('\r'+str+'[%s%%]'%(i+1))
        sys.stdout.flush()
        time.sleep(0.1)
        #print (100*y/(h-2*kernel_half),"%")  # let the user know that something is happening (slowly!)
    #--------------PRINT THE PROCESS-------------------------
        
        for x in range(kernel_half, w - kernel_half):#和28行构成对基准图像的遍历
            best_offset = 0 #最佳偏移为0
            prev_ncc = -1 #不相关
            
            for offset in range(max_offset):  #极线搜索           
                zncc_up_temp = 0
                zncc_up = 0
                zncc_down_temp1 = 0
                zncc_down_temp2 = 0
                zncc_down = 1
                zncc = 0                       
                
                # v and u are the x,y of our local window search, used to ensure a good 
                # match- going by the squared differences of two pixels alone is insufficient, 
                # we want to go by the squared differences of the neighbouring pixels too
                for v in range(-kernel_half, kernel_half):
                    for u in range(-kernel_half, kernel_half): #局部窗口搜索
                        # iteratively sum the sum of squared differences value for this block
                        # left[] and right[] are arrays of uint8, so converting them to int saves
                        # potential overflow, and executes a lot faster 
                
                #------------------------MY CODE-------------------------------------
                        zncc_up_temp = int((left[y+v, x+u])-left_eq) * int((right[y+v, (x+u) - offset])-right_eq)  
                        zncc_up += zncc_up_temp
                        zncc_down_temp1 += int((left[y+v, x+u])-(left_eq))*int((left[y+v, x+u])-(left_eq))
                        zncc_down_temp2 += int((right[y+v, (x+u) - offset])-(right_eq))* int((right[y+v, (x+u) - offset])-(right_eq))
                        zncc_down = math.sqrt(zncc_down_temp1*zncc_down_temp2)
                        if zncc_down == 0:
                            zncc = 1
                        else:
                            zncc = (zncc_up/zncc_down)             
                        #这是ZNCC算法的公式
                #----------------------------------------------------------------------
                # if this value is smaller than the previous ssd at this block
                # then it's theoretically a closer match. Store this value against
                # this block..
                if zncc > prev_ncc: #取最大值
                    prev_ncc = zncc
                    best_offset = offset
                    #寻找最小offset
            # set depth output for this x,y location to the best match
            depth[y, x] = best_offset * offset_adjust #深度图像矩阵形成
                                
    # Convert to PIL and save it
    Image.fromarray(depth).save('depth_zncc.png')
    print('\n')
    print ("[KING-ZNCC]The depth image is done!!!")

if __name__ == '__main__':
    stereo_match("view0.png", "view1.png", 6, 30)  # 6x6 local search kernel, 30 pixel search range

