# The full list of layers and styles can be requested with one of the following:
# https://api.wx.spire.com/ows/wms?service=WMS&request=GetCapabilities&product=sof-d&bundle=basic
# https://api.wx.spire.com/ows/wms?service=WMS&request=GetCapabilities&product=sof-d&bundle=maritime
# https://api.wx.spire.com/ows/wms?service=WMS&request=GetCapabilities&product=sof-d&bundle=maritime-wave
# https://api.wx.spire.com/ows/wms?service=WMS&request=GetCapabilities&product=sof-d&bundle=precipitation

BASIC_LAYERS = {
    "t2m:K",  # temp
    "t2m:C",
    "t2m:F",
    "2d:K",
    "2d:C",
    "2d:F",
    "pmsl:hPa",
    "r",
    "tp:mm",
    "10u:ms",
    "10u:kt",
    "10v:ms",
    "10v:kt",
    "sfcwind:ms",
    "sfcwind:kt",
    "gust:ms",
    "gust:kt",
    "t2mmin:K",
    "t2mmin:C",
    "t2mmin:F",
    "t2mmax:K",
    "t2mmax:C",
    "t2mmax:F",
    "Total Cloud Cover (%)": {
        "layer": "tcc",
        "style": "cc"
    }
}

MARITIME_LAYERS = [
    "wvdir",
    "swh:m",
    "swh:ft",
    "mwp",
    "sst:K",
    "sst:C",
    "sst:F",
    "ocu:ms",
    "ocu:kt",
    "ocv:ms",
    "ocv:kt",
    "oc:ms",
    "oc:kt",
]

STYLES = [
    "/nearest",
    "-contours-w/nearestcontour",
    "-contours-bk/nearestcontour",
    "-arrows-w/vector",
    "-arrows-bk/vector",
    "-barbs-w/barb",
    "-barbs-bk/barb",
]
