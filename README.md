# Requirements

inputs:
- bounding box or center point for Orthographic projection (currently hard-coded inside of `visualize()`)
- WMS parameters (forecast issuance, data bundle)

outputs:
- produce image files with background and WMS layers

# Changing Resolution

Increasing the `DPI` value at the top of the script will improve the output image resolution.

However, this can drastically increase the compute power necessary - so please be careful (especially with multi-processing).

# Running

`python capture_wms.py --token $SPIRETOKEN`

or for Maritime data variables:

`python capture_wms.py --token $SPIRETOKEN --bundle maritime`

See in-line code documentation for other arguments.

# Resources

https://rabernat.github.io/research_computing_2018/maps-with-cartopy.html