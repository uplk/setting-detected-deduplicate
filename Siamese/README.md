# 数据去重

## 数据标记

将实验数据的图片进行标记，按照如下格式进行摆放

- image_backgroudd   
    - character01
        - 001.png
        - 002.png
    - character02
    ......

格式说明
image_backgroud是目录名字
character01是图片的场景名字，比如抖音所有视频流界面，所有的视频都是一个场景，这个目录下只放一种场景的图片

## 数据训练

1. train.py中train_own_data=True，表示训练自己的数据，
2. 将image_background整个目录放入datasets目录下
3. 运行tray.py进行训练