# 南京眼案例图的来源与读法

| 图片 | 作者、来源与处理 |
| --- | --- |
| [桥梁构件与桥面细节](bridge-details.jpg) | 左上为钉钉拍摄的 [Nanjing Eye Footbridge 1](https://commons.wikimedia.org/wiki/File:Nanjing_Eye_Footbridge_1.jpg)，实拍面板沿用 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)。右上为使用本技能的整桥交付版，下排依次为直接使用 Codex 的第一份局部终稿与传统参数化拟合的局部终稿。 |
| [塔冠开口](tower-opening.png) | 桥面摄影为钉钉的 [Nanjing Eye Footbridge 1](https://commons.wikimedia.org/wiki/File:Nanjing_Eye_Footbridge_1.jpg)。图像按 960 × 720 的工作坐标取局部，叠加标点，并排绘制截线。此衍生图按 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) 分享。 |
| [岛端引桥叠图](approach-alignment.jpg) | 航拍摄影为 [Jiang Yu](https://unsplash.com/photos/an-aerial-view-of-a-city-with-a-river-running-through-it-mLigzKBe62g)，适用 [Unsplash License](https://unsplash.com/license)。原片缩放至 960 × 640，再叠加标点、模型投影与图例。红色为初稿中心线，蓝色为修订中心线，青色为桥面边缘，黄色为照片标点。 |
| [三视角对照](three-views.jpg) | 左列从上到下是 [Uyiliu2 的岸侧实拍](https://commons.wikimedia.org/wiki/File:Full_view_of_Nanjing_Eye_Pedestrian_Bridge.jpg)、[钉钉的桥面实拍](https://commons.wikimedia.org/wiki/File:Nanjing_Eye_Footbridge_1.jpg)、[Jiang Yu 的航拍](https://unsplash.com/photos/an-aerial-view-of-a-city-with-a-river-running-through-it-mLigzKBe62g)。前两幅等比缩放排版，按 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) 分享；第三幅按 [Unsplash License](https://unsplash.com/license) 使用。右列是本项目模型在近似对应机位下的渲染。 |

三幅模型图共用按左上实拍估计的桥面透视相机。右上沿用整桥交付时的桥面渲染，下排将两份已经冻结的 GLB 分别载入同一摄影场景，沿用相机的位置、朝向、30.13 毫米虚拟焦距（36 毫米传感器宽度）、光照和江岸示意配景。三幅模型画面均为 960 × 720 像素，排版时将四格完整画面等比缩放。两份局部模型原任务的范围是环塔和桥带。

[塔冠截线表](tower-sections.csv)记录对照图中的横截行、实拍左右内缘，以及可取得的初稿与终稿测量。空白表示该位置没有初稿测量存档。项目介绍中的四条留出截线来自同一幅照片，终稿偏差按左右内缘横坐标的绝对差计算。

[引桥标点表](approach-points.csv)列出照片上的标点，以及每个标点到两版中心线投影的最近距离。逐点距离保留两位小数，README 的均值使用未取整记录。两版使用同一个依据桥塔估计的相机。照片未作测绘标定。
