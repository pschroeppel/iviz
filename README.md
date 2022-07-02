# iViz

## Overview 

iViz is a super handy interactive tool visualize any kind of 2D image sequences with image, 
optical flow and general floating point data. The
tool allows to arrange views in a grid and scroll through the sequence of data. 
Inspection is possible with cursor working simultaneously in multiple views. Visualization ranges can be adapted 
can be adjusted interactively for optical flow and floating point data. 

___Tutorials and YouTube videos will be made available in the second
half of 2022.___

iViz Pro will be available in the second half of 2022. iViz Pro features drag and drop, browsing
N-dimensional tensors as well as an advanced renderer with zoom and pan. 

## Installation 

Prerequisites: 
* Install [iUtils](https://github.com/eddy-ilg/iutils.git).
* Install [iMetrics](https://github.com/eddy-ilg/imetrics.git).
* Install [iTypes](https://github.com/eddy-ilg/itypes.git).

Instructions: 

    cd /my/code
    git clone https://github.com/eddy-ilg/itypes
    cd itypes 
 
    # Install dependencies 
    pip3 install --user -r requirements.txt 

    # Install optional dependencies (recommended)
    pip3 install --user -r optional.txt 

    # Add to your ~/.bashrc:
    # (this will configure PATH and PYTHONPATH)
    source /my/code/itypes/bashrc 

Please note that with all the packages installed you should have the following lines in your ~/.bashrc:

    source ~/code/iutils/bashrc 
    source ~/code/imetrics/bashrc 
    source ~/code/itypes/bashrc 
    source ~/code/iviz/bashrc

## License and Contributions 

The code is licensed under the Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License.
Any kind of redistribution or commercial use is prohibited. 

If you are interested contributing and partnering up please contact [Eddy Ilg](mailto:me@eddy-ilg.net)
for questions.
Contributions are welcome. 
