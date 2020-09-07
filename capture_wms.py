# https://pypi.org/project/OWSLib/
from owslib.wms import WebMapService
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import sys
import time
import multiprocessing
from datetime import datetime

# local
# import consts

# A high dpi value such as 200 or more indicates a high resolution image,
# while a low dpi value such as 10 indicates a lower resolution image.
DPI = 600
# If `STD_FREQ` is set to True, only 6-hourly updates will be captured.
STD_FREQ = True
# Flag for orthographic projection
ORTHOGRAPHIC = False


def generate_all_images(configs):
    with multiprocessing.Pool(len(configs), initializer=None) as pool:
        pool.map(generate_image, configs)


# https://scitools.org.uk/cartopy/docs/v0.13/matplotlib/advanced_plotting.html
def add_wms_layer(token, ax, bundle, layer, style, ftime):
    print("Requesting {} for WMS layer: {} ...".format(ftime, layer))
    # https://scitools.org.uk/cartopy/docs/v0.13/matplotlib/geoaxes.html#cartopy.mpl.geoaxes.GeoAxes.add_wms
    ax.add_wms(
        wms="https://api.wx.spire.com/ows/wms?spire-api-key=" + token,
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
    output_file = "test_output/{}.png".format(ftime)
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


def visualize(token, bbox, obj1, obj2):
    print()
    # # Cartopy projections: https://scitools.org.uk/cartopy/docs/latest/crs/projections.html
    # # ccrs.epsg(3857) # ccrs.Mercator()
    if ORTHOGRAPHIC is True:
        ax = plt.axes(projection=ccrs.Orthographic(0, -90))  # (lon, lat)
    else:
        ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=0))
        # crop the view
        ax.set_extent(bbox, crs=ccrs.PlateCarree())

    # include contour lines for global coastlines
    # to provide "basemap" context for the WMS layers
    ax.coastlines()
    # ax.gridlines()
    # ax.add_feature(cartopy.feature.OCEAN, zorder=0)
    # ax.add_feature(cartopy.feature.LAND, zorder=0, edgecolor='black')

    # # mark a known place to help us geolocate ourselves
    # ax.plot(-117.1625, 32.715, 'wo', markersize=5, transform=ccrs.PlateCarree())
    # ax.text(-117, 33, 'San Diego', transform=ccrs.PlateCarree())

    # set the lead times
    # WARNING: this assumes same timepositions exist for both layers
    times = obj1["wms"].timepositions
    # exit early if our assumption fails
    if len(times) != 54:
        # the provided issuance time is not a complete forecast
        print("Latest forecast issuance is not complete. Please code better.")
        # TODO: handle this automatically
        sys.exit()
    # ensure time strings are ordered
    times.sort()
    # check if we should only get 6-hourly updates
    if STD_FREQ is True:
        # for the first day, get only the 6-hourly updates
        t = [times[0], times[6], times[12], times[18], times[24], times[30]]
        # the remaining items in the list are already in 6-hourly increments
        t += times[31:]
        # reset the `times` list
        times = t
    # init list of configs
    configs = []
    # add times to all the things
    for t in times:
        # specify a WMS layer with the colour style
        layer1 = {
            "layer": obj1["wms"].name,
            "bundle": obj1["bundle"],
            "style": obj1["style"]["title"],
            "legend": obj1["style"]["legend"],
            "time": t,
        }
        # specify another WMS layer with a different style
        layer2 = {
            "layer": obj2["wms"].name,
            "bundle": obj2["bundle"],
            "style": obj2["style"]["title"],
            "legend": obj2["style"]["legend"],
            "time": t,
        }
        configs.append([token, ax, layer1, layer2])
    # do all the stuff
    generate_all_images(configs)
    # inform the script user that it ran successfully
    print("All done!")


def get_layer_metadata(token, bundle, date, issuance, cfg1, cfg2):
    # get WMS capabilities
    url = "https://api.wx.spire.com/ows/wms?bundle={}&spire-api-key={}".format(
        bundle, token
    )
    wms = WebMapService(url, version="1.3.0")
    # list of all available layer names
    layers = list(wms.contents)
    # build the layer names
    ln1 = "sof-d/{}/{}/{}".format(date, issuance, cfg1["name"])
    ln2 = "sof-d/{}/{}/{}".format(date, issuance, cfg2["name"])
    # build the layer metadata objects
    return [
        {
            "wms": wms[ln1],
            "style": wms[ln1].styles[cfg1["name"] + cfg1["style"]],
            "bundle": bundle,
        },
        {
            "wms": wms[ln2],
            "style": wms[ln2].styles[cfg2["name"] + cfg2["style"]],
            "bundle": bundle,
        },
    ]


if __name__ == "__main__":
    print()
    START = datetime.now()
    print("Script started at: {}".format(START))
    print()
    # get token from script argument
    token = sys.argv[1]
    # get today's date in YYYYmmdd format
    today = datetime.now().strftime("%Y%m%d")
    # set the preferred forecast issuance time
    issuance = "00"
    # set the bounding box
    bbox = [-180, 180, -90, 90]
    # set the bundle
    bundle = "basic"
    # specify the layers we are interested in
    cfg1 = {"name": "gust:ms", "style": "/nearest"}
    cfg2 = {"name": "sfcwind:ms", "style": "-contours-bk/nearestcontour"}
    # get the WMS metadata
    layers = get_layer_metadata(token, bundle, today, issuance, cfg1, cfg2)
    # request and build the WMS composite images
    visualize(token, bbox, layers[0], layers[1])
    # print out how long this script run took
    END = datetime.now()
    print()
    print("Duration of Script Run: {}".format(END - START))
