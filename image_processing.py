import numpy as np
import tensorflow as tf
import imutils
import cv2
from imutils.contours import sort_contours

class ImageProcessing:
    def __init__(self):
        pass


    def image_to_array(self, input_img, img_width=32, img_height=32):
        # img = Image.open(input_img)
        img = input_img.resize((img_width, img_height), resample=0, box=None)
        # img = ImageOps.grayscale(img)
        img = img.convert('RGB')
        img = np.array(img)
        img = img / 255.0
        #img = tf.image.rgb_to_grayscale(img)
        return img[np.newaxis]

    #separates characters using list of bounding boxes
    def separate_chars(self, input_img, rects, resize=False):
        chars = []
        i = input_img
        for rect in rects:
            (x, y, w, h) = rect
            img = i.copy()
            cropped = img.crop((x, y, x + w, y + h))
            chars.append(cropped)

        if resize:
            a_img = [self.image_to_array(img, 300, 40) for img in chars]
            return a_img

        a_img = [self.image_to_array(img) for img in chars]
        return a_img

    #gets all bounding boxes
    def get_rect(self, input_img):
        #src = cv2.imread(input_img)
        pil2cv2 = input_img.convert('RGB')
        pil = np.array(pil2cv2)
        src = pil[:, :, ::-1].copy()

        gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blurred, 30, 150)
        cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        cnts = sort_contours(cnts, method="left-to-right")[0]
        rects = []
        height, width, channel = src.shape

        # adjust threshold sensitivity, larger values than 0.5 mean less sensitivity
        tConst = 0.5

        # adjust width threshold by pixel.
        w_threshold = 8

        for i, c in enumerate(cnts):
            (x, y, w, h) = cv2.boundingRect(c)

            if i > 0:
                (tX, tY, tW, tH) = rects[-1]

                # compute center of current and previous bounding box
                tCenter = (tW / 2) + tX
                center = (w / 2) + x

                threshold = (tW * tConst) if tW >= w else (w * tConst)

                if abs(center - tCenter) < threshold:
                    # print(f'Within threshold{threshold}')
                    if y < tY:
                        new_y = y
                        new_h = h + tH + (y - tY + tH)
                    else:
                        new_y = tY
                        new_h = h + tH + (y - tY + tH)

                    if new_h > height:
                        new_h = height - new_y
                    rects[-1] = (tX, new_y, tW, new_h)

                    continue

            rects.append((x, y, w, h))

        for i, r in enumerate(rects):
            # pop bounding box with less pixels than the threshold
            if r[2] <= w_threshold:
                # print(rects)
                rects.pop(i)

        return rects

