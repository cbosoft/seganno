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

# Usage
Download; install requirements; run.

```
git clone git@github.com:cbosoft/seganno
cd seganno
pip install -r requirements
# pip install torch torchvision  # for DL operations
python -m annot
```