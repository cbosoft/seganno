# Segmentation Annotation Tool
Tool for annotating images for image segmentation tasks.

Similar, more mature, tools:
- [CVAT](https://cvat.ai)
- [labelImg](https://github.com/heartexlabs/labelImg)

![screenshot of annot in action](https://github.com/cbosoft/seganno/blob/master/screenshots/seganno_screenshot_1.png?raw=true)
[image src](https://cmac.ac.uk/case-study-database/exquisite-particles-towards-predicting-agglomeration-in-apis)

# Motivation
Instance segmentation is typically encoded as a polygon - a list of points. If we're doing this manually, you'll typically end up with a dozen or so points on the border of a particle. These will be well spaced, and naturally will be higher density around fiddly areas of the object. This process is slow and tedious (can't emphasise this enough). We can speed things up by leveraging a model to annotate images automatically!

These images may need cleaning up, which can be done with some human intervention. However, the machine-generated annotations tend to be more density (>50 points per object) and thus are **very time consuming to edit**. We can accept/reject these annotations quickly, but it would be greatly beneficial to quickly edit the annotations too.

That's where `seganno` comes in.

My main motivation was creating custom "brushes" for moving groups of many points around the screen to speed up the editing of automatic annotations. In addition, we can add other nice features like brightness and contras adjustment, edge detection filters, and even apply ML models direct in the app to assist the manual annotation process.

# Installation
Download; install requirements; done.

```
git clone git@github.com:cbosoft/seganno
cd seganno
pip install -r requirements
# pip install torch torchvision  # for DL operations
python -m annot
```

# Usage
## Datasets
Before I get into how to use the annotation tool, I want to touch on how datasets are described. `seganno` follows the COCO dataset json scheme. This means that a dataset is a dictionary, containing keys:
- `images` - a list of dictionaries defining images. Contains keys like `file_name`, `width`, `height`, and so on.
- `annotations` - a list of dictionaries defining annotations.

The paths of the images are *not absolute paths* - they are **relative to the json file**. This means that the images should be in a folder beneath the one containing the dataset json file. The images and dataset file need to be kept in sync, so it is best to move them together, as if they were one file. If you know the image data and folder structure is the same in two locations, it is safe to copy the json file between the locations. Typically, in `seganno`, the dataset json file will have the same name as the subdirectory containing the images.

An example dataset layout:
```
root_folder
  |- A_Dataset.json
  +- A_Dataset
       |- image1.png
       |- image2.png
       |- ...
       +- imageX.png
```

## User interface
Once `seganno` is open, you're presented with a central area, and panels to the left and right. The central area is where images will be loaded and where you'll draw and edit annotations.

The left panel contains the tool box, where you can choose between different tools to use to change annotations, such as the polygon tool (which draws, well, polygons). Below the tool box is the particle class selector. This changes the class you assign to new annotations. (Classes can be subsequently changed at any time in the annotation list box on the right.) Below the class selector are the image augmentation options. These options can be used to enhance visibility of structures in the images. Finally, the zoom controls are on the bottom left. Clicking reset will reset the zoom level and also the position. Handy if the image is out of view and can't be panned back!

The right panel contains the annotation list, showing information on annotations in the current image and has options like edit an existing annotation, delete the annotation, or change its shape class. Below this is the dataset contents box. This has options for opening and saving a dataset, as well as allowing you to select the image that is being worked on.

## Opening a dataset
Click on "open" in the dataset browser box, navigate to the **directory of images** you want to open. If a corresponding json file is found, image information will be read from here. Otherwise, images will be read from the directory.

When a dataset opens, you'll be shown a list of images in the dataset browser (bottom right). Click on a row to see the image and any annotations.

## Moving and zooming
You can pan the image by shift-clicking and dragging. Zooming in and out of the image is done by pressing the "+" or "-" buttons in the zoom control box respectively. Clicking "Reset" in the zoom control box will reset the zoom level and also the position. Handy if the image is out of view and can't be panned back!

## Creating an annotation
1. Select the polygon tool (top left).
2. Double click somewhere on the *edge of an object* to start an annotation.
3. Click around the border of the object to define a polygon.
4. Double click on the last point of the polygon to finish the annotation. (Or, click "stop annotating" in the tool box in the top left.)

That's one object annotation complete, repeat for as many objects as you see in the image!

## Saving the dataset
Just click "save" to write out the dataset contents to json file. This file will be located in the same directory as the images that were loaded.

# Tools
## Polygon Tool
A tool which allows you to annotated the edge of an object point-by-point. Workhorse of the annotator, most objects will be manually annotated using this tool.

## Sweeping Brush Tool
This tool moves points on a polygon away from the painting point so that they stay a radius away. Useful for editing densely defined polygons, such as might result from automatic annotation.