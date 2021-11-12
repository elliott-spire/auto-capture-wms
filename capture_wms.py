# https://pypi.org/project/OWSLib/
from owslib.wms import WebMapService
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import multiprocessing
import urllib.request
import argparse
import time
import sys

# DPI is an acronym for "dots per inch".
# A high DPI value such as 200 or more results in a high resolution image,
# while a low DPI value such as 10 results in a low resolution image.
# The higher the resolution, the more processsing power this script requires.
DPI = 400  # 400
# If `STD_FREQ` is set to True, only 6-hourly updates will be captured.
STD_FREQ = True
# Flag for orthographic projection
ORTHOGRAPHIC = True


def generate_all_images(configs):
    with multiprocessing.Pool(len(configs), initializer=None) as pool:
        pool.map(generate_image, configs)


# https://scitools.org.uk/cartopy/docs/v0.13/matplotlib/advanced_plotting.html
def add_wms_layer(token, ax, bundle, layer, style, ftime):
    print("Requesting {} for WMS layer: {} ...".format(ftime, layer))
    # https://scitools.org.uk/cartopy/docs/v0.13/matplotlib/geoaxes.html#cartopy.mpl.geoaxes.GeoAxes.add_wms
    ax.add_wms(
        wms="https://api.wx.spire.com/ows/wms?spire-api-key="
        + token
        + "&bundle="
        + bundle,
        layers=[layer],
        wms_kwargs={
            "spire-api-key": token,
            "transparent": "true",
            "bundle": bundle,
            "time": ftime,
            # `styles` and `layers` list length must match
            "styles": [style]
            # 'version': '1.3.0',
            # 'format': 'image/png',
            # 'crs': 'EPSG:4326',
        },
    )


def generate_image(config):
    token = config[0]
    ax = config[1]
    layer1 = config[2]
    layer2 = config[3]
    # add a WMS layer with the colour style
    bundle = layer1["bundle"]
    layer = layer1["layer"]
    style = layer1["style"]
    ftime = layer1["time"]
    add_wms_layer(token, ax, bundle, layer, style, ftime)
    # add another WMS layer
    if layer2 != None:
        bundle = layer2["bundle"]
        layer = layer2["layer"]
        style = layer2["style"]
        ftime = layer2["time"]
        time = ftime
        add_wms_layer(token, ax, bundle, layer, style, ftime)
    # use the time as the filename
    output_file = "output/{}.png".format(ftime)
    proc_name = multiprocessing.current_process().name
    print("Saving figure for {}: {} ...".format(proc_name, ftime))
    # save the figure to an image file
    plt.savefig(
        output_file,
        # Dots Per Inch (resolution)
        dpi=DPI,
        # Border padding for the figure:
        bbox_inches="tight",
        pad_inches=0,
        # Transparent background (saves as PNG)
        transparent=True,
    )
    print("Figure for {} saved to: {}".format(proc_name, output_file))
    print()
    # Display the figure:
    # plt.show()


def visualize(token, bbox, layers):
    print()
    obj1 = layers[0]
    obj2 = None
    if len(layers) > 1:
        obj2 = layers[1]
    # Cartopy projections: https://scitools.org.uk/cartopy/docs/latest/crs/projections.html
    if ORTHOGRAPHIC is True:
        # Specify center point for orthographic projection: (lon, lat)
        # ax = plt.axes(projection=ccrs.Orthographic(-40, 30)) # middle of atlantic
        ax = plt.axes(projection=ccrs.Orthographic(-99, 36))  # middle of US
        # ax = plt.axes(projection=ccrs.Orthographic(21, 10))  # middle of Africa
        # ax = plt.axes(projection=ccrs.Orthographic(0, 90))  # North Pole
        # ax = plt.axes(projection=ccrs.Orthographic(0, -90))  # South Pole
    else:
        ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=0))
        # Crop the view
        ax.set_extent(bbox, crs=ccrs.PlateCarree())

    # Include contour lines for global coastlines
    # to provide "basemap" context for the WMS layers
    ax.coastlines()
    # ax.gridlines()
    # ax.add_feature(cartopy.feature.OCEAN, zorder=0)
    # ax.add_feature(cartopy.feature.LAND, zorder=0, edgecolor='black')

    # # Mark a location on the map
    # ax.plot(-117.1625, 32.715, 'wo', markersize=5, transform=ccrs.PlateCarree())
    # ax.text(-117, 33, 'San Diego', transform=ccrs.PlateCarree())

    # Set the lead times
    # NOTE: this assumes the same timepositions exist for both layers
    times = obj1["wms"].timepositions
    # Exit early if our assumption fails
    if len(times) < 54:
        print("Number of times:", len(times))
        print(times)
        # The provided issuance time is not a complete forecast
        # which means the latest forecast is still updating in the API
        print(
            "Latest forecast issuance is not complete. Please choose an earlier issuance."
        )
        sys.exit()
    # Ensure the time strings are ordered
    times.sort()
    # total cloud cover is empty for first lead time
    # so we need to ignore the first lead time
    # which requires us to first set a flag indicating we should do this
    cloud_cover = False
    if "cc/nearest" in obj1["style"]["title"]:
        cloud_cover = True
    if obj2 is not None and "cc/nearest" in obj2["style"]["title"]:
        cloud_cover = True

    print("Times:", times)
    print()
    # Check if we should only get 6-hourly updates
    if STD_FREQ is True:
        # For the first 5 days, get only the 6-hourly updates
        indices = [
            0,
            6,
            12,
            18,
            24,
            30,
            36,
            42,
            48,
            50,
            52,
            54,
            56,
            58,
            60,
            62,
            64,
            66,
            68,
            70,
        ]
        if cloud_cover:
            # ignore 0h lead time for cloud cover
            indices = indices[1:]
        viz_times = []
        for i in indices:
            viz_times.append(times[i])
        # The remaining items in the list are already in 6-hourly increments
        viz_times += times[72:]
        # viz_times += times[72:81]
        # Reset the `times` list
        times = viz_times
        print("Total times: {} \n".format(len(times)))
        print(times, "\n")
    # elif HOURLY is True:
    #     t = times[0:48]
    # Init list of configs
    configs = []
    # Add times to all the things
    for t in times:
        # Specify a WMS layer with the colour style
        layer1 = {
            "layer": obj1["wms"].name,
            "bundle": obj1["bundle"],
            "style": obj1["style"]["title"],
            "legend": obj1["style"]["legend"],
            "time": t,
        }
        config = [token, ax, layer1]
        if obj2 is not None:
            # Specify another WMS layer with a different style
            layer2 = {
                "layer": obj2["wms"].name,
                "bundle": obj2["bundle"],
                "style": obj2["style"]["title"],
                "legend": obj2["style"]["legend"],
                "time": t,
            }
            config.append(layer2)
        else:
            config.append(None)
        configs.append(config)
    # Generate WMS output images concurrently
    # with multiprocessing
    generate_all_images(configs)
    # Download legend images
    legend1 = obj1["style"]["legend"] + "&spire-api-key=" + token
    urllib.request.urlretrieve(legend1, "output/legend_1.png")
    if obj2 is not None:
        legend2 = obj2["style"]["legend"] + "&spire-api-key=" + token
        urllib.request.urlretrieve(legend2, "output/legend_2.png")
    # Inform the script user that it ran successfully
    print("All done!")


def get_layer_metadata(token, bundle, date, issuance, cfg1, cfg2):
    # Get WMS capabilities
    url = "https://api.wx.spire.com/ows/wms?bundle={}&spire-api-key={}".format(
        bundle, token
    )
    wms = WebMapService(url)  # , version="1.3.0")
    # Parse the available layer names and associated styles
    contents = list(wms.contents)
    layers = {}
    for x in contents:
        layer_name = x.split("/")[-1]
        display_name = wms[x].title
        styles = list(wms[x].styles.keys())
        layers[display_name] = {
            "name": layer_name,
            "styles": styles,
        }
        print(layer_name)
    #     print(display_name)
    #     for s in styles:
    #         print("\t{}".format(s))
    # print(len(list(layers.keys())))
    # Build the layer names
    if bundle == "maritime":
        prefix = "sof-d.maritime"
    else:
        prefix = "sof-d"
    ln1 = "{}/{}/{}/{}".format(prefix, date, issuance, cfg1["name"])
    # Build the layer metadata object
    layer1 = {
        "wms": wms[ln1],
        "style": wms[ln1].styles[cfg1["stylename"] + cfg1["style"]],
        "bundle": bundle,
    }
    # Create the list of layers
    layers = [layer1]
    # Check for a second/overlay layer
    if cfg2 is not None:
        ln2 = "{}/{}/{}/{}".format(prefix, date, issuance, cfg2["name"])
        layer2 = {
            "wms": wms[ln2],
            "style": wms[ln2].styles[cfg2["stylename"] + cfg2["style"]],
            "bundle": bundle,
        }
        layers.append(layer2)
    # Return the list of layers
    return layers


if __name__ == "__main__":
    print()
    START = datetime.now()
    print("Script started at: {}".format(START))
    print()

    parser = argparse.ArgumentParser()
    parser.add_argument("--token", help="Spire API Token", required=True)
    parser.add_argument(
        "--bundle",
        type=str,
        default="basic",
        choices=["basic", "maritime"],
        help="The name of the Spire data bundle",
    )
    parser.add_argument(
        "--issuance",
        type=str,
        default="00",
        choices=["00", "06", "12", "18"],
        help="The forecast issuance time (UTC)",
    )
    parser.add_argument(
        "--bbox",
        nargs="+",
        default=[-90, 90, -180, 180],  # min_lat max_lat min_lon max_lon
        help="The bounding box used to crop the data, specified as minimum/maximum latitudes and longitudes",
    )
    args = parser.parse_args()
    token = args.token
    bundle = args.bundle
    issuance = args.issuance
    bbox = args.bbox
    # Get today's date in YYYYmmdd format
    # today = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    today = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    # Specify the layers we are interested in
    # See `consts.py` for more options and docs
    # cfg1 = {
    #     "name": "tcc",
    #     "stylename": "cc",
    #     "style": "/nearest",
    # }
    # cfg1 = {
    #     "name": "sst:C",
    #     "stylename": "sst:C",
    #     "style": "/nearest",
    # }
    # cfg1 = {
    #     "name": "sfcwind:ms",
    #     "stylename": "sfcwind:ms",
    #     "style": "/nearest",
    # }
    # cfg1 = {
    #     "name": "swh:m",
    #     "stylename": "swh:m",
    #     "style": "-bwr/nearest",  # "-deep/nearest"
    # }
    cfg1 = {
        "name": "t2m:F",
        "stylename": "temp:F",
        "style": "/nearest",
    }
    cfg2 = None
    # cfg2 = {
    #     "name": "sfcwind:kt",
    #     "stylename": "sfcwind",
    #     "style": "-barbs-bk/barb",
    # }
    # Get the WMS metadata
    layers = get_layer_metadata(token, bundle, today, issuance, cfg1, cfg2)
    # Request and build the WMS composite images
    visualize(token, bbox, layers)
    # Print out how long this script run took
    END = datetime.now()
    print()
    print("Duration of Script Run: {}".format(END - START))
