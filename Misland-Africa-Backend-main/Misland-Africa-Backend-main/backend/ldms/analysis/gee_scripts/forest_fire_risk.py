import ee
import json

# import geemap
from common_gis.utils.gee import download_image
import datetime

ROI = None  # ee.FeatureCollection('USDOS/LSIB_SIMPLE/2017')
START_DATE = "2021-08-01"
END_DATE = "2021-08-30"
COUNTRY_NAME = "Algeria"
COUNTRY_VECTOR = None
IN_COLAB_CONTEXT = False
SCALE = 300


def entrypoint(aoi, country_name, analysis_start, analysis_end, scale):
    """Entry point for this script. variables will be overridden at this point

    Due to GEE limitations, we will restrict computation at country level
    Args:
            aoi (geojson): Area of interest. This will be country coords
            country_name (string): Name of country whose alerts you want to compute
            analysis_start (string): Analysis period start date string of the format 'YYYY-mm-dd'
            analysis_end (string): Analysis period end date string of the format 'YYYY-mm-dd'
            scale (int): Scale to use when generating alerts
    """

    global START_DATE, END_DATE, COUNTRY_NAME, COUNTRY_VECTOR, ROI, SCALE
    # geometry = ee.Geometry.Polygon(coords[0])

    # ee.Geometry.Polygon(json.loads(vector)['coordinates'][0])
    # geom = ee.Geometry.Polygon(json.loads(aoi)['coordinates'][0])
    # geometry = ee.Geometry.Polygon([[[3.112174255057627, 36.73874167162853],[3.112174255057627, 36.19094855897513],[5.067740661307627, 36.19094855897513],[5.067740661307627, 36.73874167162853]]])
    COUNTRY_VECTOR = aoi
    START_DATE = analysis_start
    END_DATE = analysis_end
    COUNTRY_NAME = country_name
    ROI = ee.FeatureCollection("USDOS/LSIB_SIMPLE/2017")
    SCALE = scale


def _get_alerts(country_name, use_map_id=False):
    """Compute forest fire risk alerts

    Args:
            country_name (string): Country of computation
            use_map_id (bool): Should we use GEE mapID as is or should we download the raster and generate our own rasterfile

    Returns:
            [obj, list[], []]: Returns a tuple of [merged_tiff_url, list_of_individual_daily_tiff, daily_stats]
    """
    # Load country boundary form International Boundary dataset.
    country = filter_region(country_name)

    # Elevation data - Posibility fo spread
    dem_dataset = ee.Image("USGS/SRTMGL1_003").select("elevation").clip(country)

    # Land surface temperature MOD11A2
    datasetMOD11A2 = ee.ImageCollection("MODIS/061/MOD11A2").filter(
        ee.Filter.date(START_DATE, END_DATE)
    )
    modisLST = datasetMOD11A2.select(["LST_Day_1km"], ["ST"]).mean().clip(country)

    # Map.addLayer(modisLST, landSurfaceTemperatureVis,'Land Surface Temperature')

    # Land Cover Urban class - Anthropogenic Influence
    # LC_dataset = ee.Image("COPERNICUS/Landcover/100m/Proba-V-C3/Global/2019").select('urban-coverfraction')
    # Map.addLayer(LC_dataset.gte(10).clip(country), {}, "Land Cover")

    # Start with an image collection for a 1 month period.
    # and mask out areas that were not observed.
    collection_MODIS = (
        ee.ImageCollection("MODIS/061/MOD09GA")
        .filterDate(START_DATE, END_DATE)
        .map(maskEmptyPixels)
    )

    # Map the cloud masking function over the collection.
    collectionCloudMasked = collection_MODIS.map(maskClouds)
    modis_image = collectionCloudMasked.mean().clip(country)

    computedIndices = indexComputations(modis_image)
    image_MNDFI = computedIndices[0]  # Modified Normalized Diference Fire Index
    image_PMI = computedIndices[1]  # Perpendicular Moisture Index
    image_NDMI = computedIndices[2]  # Normalized Multiband Drought index
    pst = pst_caclulation(modisLST, dem_dataset)  # Potential Surface Tempe

    if IN_COLAB_CONTEXT:
        # FIRMS DATA- Posibility of ignition
        dataset = (
            ee.ImageCollection("FIRMS")
            .filter(ee.Filter.date(START_DATE, END_DATE))
            .filter(ee.Filter.bounds(country))
        )
    else:
        # FIRMS DATA- Posibility of ignition
        dataset = (
            ee.ImageCollection("FIRMS")
            .filter(ee.Filter.date(START_DATE, END_DATE))
            .filter(ee.Filter.geometry(country))
        )  # python API has no ee.Filter.bounds

    fires = dataset.select("T21")

    latLong = fires.map(func_sth)

    # print(latLong.getInfo())

    fire_mosaic = latLong.mosaic()
    merged_url = None
    img_array = None
    merged_url = download_image(img=fire_mosaic, scale=SCALE, region=get_country())
    print(merged_url)

    # Map.addLayer(latLong, {}, 'Alerts')
    # Map
    # urls = download_collection(latLong)
    # dailystats = [{'day': '2021-08-01', 'count': 115}, {'day': '2021-08-02', 'count': 122}]
    dailystats = date_pixel_count(latLong)
    return merged_url, [], dailystats


def compute_fire_risk(start_date, end_date, region):
    # Set parameters
    scale = SCALE
    # year = 2019

    # force format the dates
    if isinstance(start_date, datetime.date):
        start_date = start_date.strftime("%Y-%m-%d")
    if isinstance(end_date, datetime.date):
        end_date = end_date.strftime("%Y-%m-%d")

    def require_images(collection, dataset_name):
        """Fail with a useful message instead of operating on a zero-band image."""
        if collection.size().getInfo() == 0:
            raise ValueError(
                "No {0} imagery is available for {1} through {2}. "
                "Choose a period covered by that Earth Engine dataset.".format(
                    dataset_name, start_date, end_date
                )
            )
        return collection

    # Load datasets
    LC_dataset = (
        ee.Image("COPERNICUS/Landcover/100m/Proba-V-C3/Global/2019")
        .select("tree-coverfraction")
        .clip(region)
    )

    dem_dataset = ee.Image("USGS/SRTMGL1_003").select("elevation").clip(region)

    slope = ee.Terrain.slope(dem_dataset)
    sinImage = (
        slope.divide(180).multiply(3.14159265359).tan().multiply(100).rename("SLOPE")
    )
    aspect = ee.Terrain.aspect(dem_dataset).rename("ASPECT")

    datasetMOD11A2 = require_images(
        ee.ImageCollection("MODIS/061/MOD11A2").filter(
            ee.Filter.date(start_date, end_date)
        ),
        "MODIS land-surface temperature",
    )
    modisLST = (
        datasetMOD11A2.select(["LST_Day_1km"], ["ST"])
        .mean()
        .multiply(0.02)
        .subtract(273)
        .clip(region)
        .rename("LST")
    )

    # TerraClimate images are timestamped monthly. Include every calendar month
    # touched by the requested daily interval, even when neither input date is
    # the first day of a month.
    period_start = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    period_end = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    climate_start = period_start.replace(day=1)
    if period_end.month == 12:
        climate_end = datetime.date(period_end.year + 1, 1, 1)
    else:
        climate_end = datetime.date(period_end.year, period_end.month + 1, 1)

    terraClimateCollection = require_images(
        ee.ImageCollection("IDAHO_EPSCOR/TERRACLIMATE").filter(
            ee.Filter.date(climate_start.isoformat(), climate_end.isoformat())
        ),
        "TerraClimate monthly climate",
    )
    terraClimate = terraClimateCollection.min().multiply(0.001)
    p = terraClimate.select("vap").clip(region)
    windspeed = terraClimate.select("vs").clip(region)

    # dataset = ee.ImageCollection('FIRMS') \
    # 			.filter(ee.Filter.date(f'{year}-01-01', f'{year}-03-30')) \
    # 			.filter(ee.Filter.bounds(region))

    dataset = (
        ee.ImageCollection("FIRMS")
        .filter(ee.Filter.date(f"{start_date}", f"{end_date}"))
        .filter(ee.Filter.bounds(region))
    )

    fires = dataset.select("T21")
    # No detected fires is a valid result. Avoid calling first() on an empty
    # collection and represent that case with a zero-valued band.
    totalFires = ee.Image(
        ee.Algorithms.If(
            fires.size().gt(0),
            fires.reduce(ee.Reducer.count()).rename("FIRES"),
            ee.Image.constant(0).rename("FIRES"),
        )
    ).clip(region)

    def maskEmptyPixels(image):
        return image.updateMask(image.select("num_observations_1km").gt(0))

    def maskClouds(image):
        QA = image.select("state_1km")
        bitMask = 1 << 10
        return image.updateMask(QA.bitwiseAnd(bitMask).eq(0))

    collection_MODIS = require_images(
        ee.ImageCollection("MODIS/061/MOD09GA")
        .filterDate(start_date, end_date),
        "MODIS surface reflectance",
    )
    collection_MODIS = collection_MODIS.map(maskEmptyPixels).map(maskClouds)

    modis_image = collection_MODIS.mean().clip(region)

    def indexComputations(Image):
        mndfi = Image.expression(
            "((B7 - B2) - 0.05) / ((B7 + B2) + 0.05)",
            {"B7": Image.select("sur_refl_b07"), "B2": Image.select("sur_refl_b02")},
        ).rename("MNDFI")

        pmi = Image.expression(
            "-0.73 * ((B5 - 0.94) * (B2 - 0.028))",
            {"B5": Image.select("sur_refl_b05"), "B2": Image.select("sur_refl_b02")},
        ).rename("PMI")

        nmdi = Image.expression(
            "(B2 - (B6 - B7)) / (B2 + (B6 - B7))",
            {
                "B6": Image.select("sur_refl_b06"),
                "B7": Image.select("sur_refl_b07"),
                "B2": Image.select("sur_refl_b02"),
            },
        ).rename("NMDI")

        return Image.addBands(mndfi).addBands(pmi).addBands(nmdi)

    computedIndices = (
        indexComputations(modis_image)
        .addBands(modisLST)
        .addBands(totalFires)
        .addBands(sinImage)
        .addBands(aspect)
        .addBands(windspeed)
        .select(["MNDFI", "PMI", "NMDI", "LST", "FIRES", "SLOPE", "ASPECT", "vs"])
    )

    def Standardization(image, region, scale):
        mean_std = image.reduceRegion(
            reducer=ee.Reducer.mean().combine(ee.Reducer.stdDev(), "", True),
            geometry=region,
            scale=scale,
            maxPixels=1e13,
        )

        band_names = image.bandNames()

        def standardize_band(name):
            name = ee.String(name)
            band = image.select(name)
            mean = ee.Number(mean_std.get(name.cat("_mean")))
            std = ee.Number(mean_std.get(name.cat("_stdDev")))

            mean = ee.Algorithms.If(mean, mean, 0)
            std = ee.Algorithms.If(std, std, 1)

            min_val = ee.Number(mean).subtract(ee.Number(std).multiply(3))
            max_val = ee.Number(mean).add(ee.Number(std).multiply(3))

            band1 = (
                ee.Image(min_val)
                .multiply(band.lt(min_val))
                .add(ee.Image(max_val).multiply(band.gt(max_val)))
                .add(
                    band.multiply(
                        ee.Image(1)
                        .subtract(band.lt(min_val))
                        .subtract(band.gt(max_val))
                    )
                )
            )

            result_band = band1.subtract(min_val).divide(max_val.subtract(min_val))
            return result_band.rename(name)

        standardized_band_list = band_names.map(standardize_band)
        standardized_bands = (
            ee.ImageCollection(standardized_band_list).toBands().rename(band_names)
        )

        return standardized_bands.multiply(100)

    Std_Images = Standardization(computedIndices, region, 30)

    # Reclassification functions
    def slope_reclass(image):
        return (
            image.where(image.gte(85.5397), 1)
            .where(image.gte(71.0794266).And(image.lt(85.5397)), 2)
            .where(image.gte(56.6191398).And(image.lt(71.0794266)), 3)
            .where(image.gte(42.1589).And(image.lt(56.6191398)), 4)
            .where(image.gte(0).And(image.lte(42.1589)), 5)
        )

    def pst_reclass(image):
        return (
            image.where(image.gte(70), 5)
            .where(image.gte(60).And(image.lt(70)), 4)
            .where(image.gte(50).And(image.lt(60)), 3)
            .where(image.gte(40).And(image.lt(50)), 2)
            .where(image.gte(0).And(image.lt(40)), 1)
        )

    def pmi_reclass(image):
        return (
            image.where(image.gte(78.42399), 1)
            .where(image.gte(69.71021).And(image.lt(78.42399)), 2)
            .where(image.gte(60.99643).And(image.lt(69.71021)), 4)
            .where(image.gte(52.28266).And(image.lt(60.99643)), 5)
            .where(image.gte(0).And(image.lte(52.28266)), 5)
        )

    def nmdi_reclass(image):
        return (
            image.where(image.gte(80), 1)
            .where(image.gte(60).And(image.lt(80)), 2)
            .where(image.gte(40).And(image.lt(60)), 3)
            .where(image.gte(20).And(image.lt(40)), 4)
            .where(image.gte(0).And(image.lte(20)), 5)
        )

    def mndfi_reclass(image):
        return (
            image.where(image.gte(90.7964), 1)
            .where(image.gte(81.5928).And(image.lt(90.7964)), 2)
            .where(image.gte(72.3892).And(image.lt(81.5928)), 4)
            .where(image.gte(53.9819).And(image.lt(72.3892)), 5)
            .where(image.gte(0).And(image.lte(53.9819)), 3)
        )

    MNDFI_reclass = mndfi_reclass(Std_Images.select("MNDFI"))
    NMDI_reclass = nmdi_reclass(Std_Images.select("NMDI"))
    PMI_reclass = pmi_reclass(Std_Images.select("PMI"))
    PST_reclass = pst_reclass(Std_Images.select("LST"))
    SLOPE_reclass = slope_reclass(Std_Images.select("SLOPE"))

    # Weights
    MNDFI_weight = 30.85514486
    PMI_weight = 18.28471528
    NMDI_weight = 20.78721279
    PST_weight = 18.08191808
    SLOPE_weight = 6.991008991

    fire_risk = (
        MNDFI_reclass.multiply(MNDFI_weight)
        .add(PMI_reclass.multiply(PMI_weight))
        .add(NMDI_reclass.multiply(NMDI_weight))
        .add(PST_reclass.multiply(PST_weight))
        .add(SLOPE_reclass.multiply(SLOPE_weight))
        .divide(100)
        .rename("Fire Risk")
    )

    reclassified = ee.Image(0)  # Initialize with zeros

    reclassified = (
        reclassified.where(fire_risk.gte(3.5093), 5)
        .where(fire_risk.gte(3.3384).And(fire_risk.lt(3.5093)), 4)
        .where(fire_risk.gte(3.1886).And(fire_risk.lt(3.3384)), 3)
        .where(fire_risk.gte(3.0777).And(fire_risk.lt(3.1886)), 2)
        .where(fire_risk.lt(3.0777), 1)
        .rename("Fire Risk Class")
    )

    return reclassified


def generate_file_name(country_name, activity):
    return "%s_to_%s_%s_%s.tif" % (START_DATE, END_DATE, country_name, "forest_risk")


def filter_region(country_name):
    """Filter regional vector by country"""
    if IN_COLAB_CONTEXT:
        return ROI.filter(ee.Filter.eq("country_na", country_name.upper()))
    else:
        return COUNTRY_VECTOR


def get_country():
    return COUNTRY_VECTOR.geometry() if IN_COLAB_CONTEXT else COUNTRY_VECTOR


def get_results(use_map_id=False):
    """This is the main function to be called aside from entry_point.
    Will return the results of the computation

    Args:
            use_map_id (bool): Should we use GEE mapID as is or should we download the raster and generate our own rasterfile

    Returns:
            list: List of tuples of the form (alert, loss_url, gain_url)
    """
    # Get alerts for the countries of interest
    country_alerts = []
    for i, cntry in enumerate([COUNTRY_NAME]):
        country_alerts.append(
            _get_alerts(cntry, use_map_id)
        )  # Appends a tuple of ((loss, gain), loss_url, gain_url)

    # print ("Urls: ", [list(x)[1:] for x in country_alerts])
    return country_alerts
