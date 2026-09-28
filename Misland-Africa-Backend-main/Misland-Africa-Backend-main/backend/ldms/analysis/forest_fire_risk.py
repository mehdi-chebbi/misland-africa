from common_gis.utils.gee import GEE, download_image
from ldms.enums import RasterSourceEnum, ForestFireRiskEnum, ForestChangeQuinaryEnum
from common.utils.common_util import return_with_error, cint
from common.utils.date_util import (
    parse_date,
    format_date,
    validate_years,
    validate_dates,
    days_between_dates,
)
import ee
import datetime
from django.utils.translation import gettext as _
import json
from ee.ee_exception import EEException
from ldms.analysis.gee_scripts import forest_risk_assessment, forest_fire_risk

# from ldms.utils.settings_util import get_settings
from common.utils import log_util
from common_gis.utils.vector_util import get_vector, get_vector_from_db
from common_gis.models import AdminLevelZero, RegionalAdminLevel
from common.utils.file_util import (
    download_and_unzip_file,
    get_download_url,
    unzip_file,
    get_absolute_media_path,
    copy_file,
    get_physical_file_path_from_url,
)
from common_gis.utils.settings_util import get_gis_settings
from ldms.utils.settings_util import get_ldms_settings
from common.utils.common_util import cint
from common_gis.utils.raster_util import (
    generate_tiles,
    get_raster_values,
    return_raster_with_stats,
)
from ldms.enums import GenericRasterBandEnum


class ForestFireRiskSettings:
    SUB_DIR = ""  # "forestloss" # Subdirectory to store rasters for forestloss
    DEFAULT_SCALE = 300


USE_MAP_ID = False  # Should we use GEE mapID to return the results or should we convert the results to array and create our own raster


class ForestFireRiskGEE:  # (GEE):
    """
    Class to auto-run scripts to detect Forest Fire on GEE
    """

    def __init__(self, **kwargs):
        """
        Args:
                **admin_level (int)**:
                        The administrative level for the polygon to be used in case a shapefile id has been provided for the parameter **vector**.
                **shapefile_id (int)**:
                        ID of an existing shapefile.
                **custom_coords (GeoJSON, or GEOSGeometry)**:
                        Coordinates which may be as a result of a custom drawn polygon or a Geometry object in form of GeoJSON.
                **start_date (date)**:
                        Analysis start date.
                **end_date (date)**:
                        Analysis end date.
                **raster_source (string)**:
                        Either Sentinel-2 or Landsat
                **country_name (string)**:
                        Country Name
                **request**:
                        WebRequest
        """
        self.admin_level = kwargs.get("admin_level", None)
        self.shapefile_id = kwargs.get("shapefile_id", None)
        self.custom_vector_coords = kwargs.get("custom_vector_coords", None)
        self.admin_0 = kwargs.get("admin_0", None)

        # Set start and end dates of a period BEFORE the fire. Make sure it is long enough for
        # Sentinel-2 to acquire an image (repetition rate = 5 days). Adjust these parameters, if
        # your ImageCollections (see Console) do not contain any elements.
        self.start_date = kwargs.get("start_date", None)  # '2017-02-20'
        self.end_date = kwargs.get("end_date", None)  # '2017-03-28'

        self.platform = kwargs.get("raster_source", RasterSourceEnum.SENTINEL2)  # "L8"
        self.error = ""
        self.request = kwargs.get("request", None)
        self.country_name = kwargs.get("country_name", None)
        self.geometry = None

    def get_country(self):
        vector_model = AdminLevelZero.objects.filter(id=self.admin_0).first()
        return vector_model, (
            "The admin_0 value of {} specified does not exist".format(self.admin_0)
            if not vector_model
            else None
        )

    def calculate_fire_risk(self):
        """Calculate forest fire risk"""
        self.start_date = parse_date(self.start_date)
        self.end_date = parse_date(self.end_date)

        self.start_date, self.end_date, period_error = self.validate_periods()
        if period_error:
            return self.return_with_error(period_error)

        days, error = self.validate_max_days()
        if error:
            return self.return_with_error(error)

        # validate vector
        vector, error = self.get_vector()  # self.get_country_vector() #
        # vector, error = self.get_vector()
        if error:
            return self.return_with_error(error)

        # regional_vector, error = self.get_regional_vector()
        # if error:
        # 	return self.return_with_error(error)

        # super(ForestFireRiskGEE, self).initialize()
        gee = GEE()  # initialize here
        # self.geometry = ee.Geometry.Polygon(json.loads(vector)['coordinates'][0])
        self.geometry = ee.Geometry(json.loads(vector))
        # self.roi = ee.Geometry(json.loads(regional_vector))
        # self.set_platform(self.platform)
        # self.filter_rasters()

        country_vect, error = self.get_country()
        if error:
            return self.return_with_error(error)

        forest_fire_risk.entrypoint(
            # roi=ee.Geometry.Polygon(json.loads(regional_vector)['coordinates'][0]),
            # roi=self.roi,
            aoi=self.geometry,
            country_name=country_vect.name_0,
            analysis_start=format_date(self.start_date),
            analysis_end=format_date(self.end_date),
            scale=ForestFireRiskSettings.DEFAULT_SCALE,  # get_settings().alert_scale
        )

        # results = forest_fire_risk.get_results()
        # for res in results:  # is of type [[x, [], []]]
        #     merged_tiff = res[0]
        #     daily_tiffs = res[1]
        #     daily_stats = res[2]
        #     # get stats on daily tiff

        merged_tiff = forest_fire_risk.compute_fire_risk(
            format_date(self.start_date), format_date(self.end_date), self.geometry
        )

        path = download_image(
            merged_tiff,
            scale=ForestFireRiskSettings.DEFAULT_SCALE,
            region=self.geometry,
        )
        if not path:
            self.error = _("No available forest fire data")
            return {"error": self.error}

        fl = download_and_unzip_file(path, dest_file=self.generate_file_name())
        # copy file from temp to media dir
        dest = get_absolute_media_path(
            file_path=None,
            is_random_file=True,
            random_file_prefix="forestfirerisk",
            random_file_ext=".tif",
        )
        out_file = copy_file(fl, dest)
        url = get_download_url(request=self.request, file=out_file.split("/")[-1])
        # self.results = results
        # wms_url, layer, legend = None, None, None
        # if get_gis_settings().enable_tiles:
        #     wms_url, layer, legend = generate_tiles(
        #         raster_file=out_file, nodata=0, change_enum=ForestFireRiskEnum
        #     )

        datasource = get_raster_values(
            self.get_file_path(url),
            band=GenericRasterBandEnum.HAS_SINGLE_BAND,
            raster_source=None,  # self.raster_source,
            windowed=False,
        )

        res = return_raster_with_stats(
            request=self.request,
            datasource=datasource,
            prefix="forestfirerisk",
            change_enum=ForestFireRiskEnum,
            metadata_raster_path=out_file,  # clipped_raster_paths[0], #clipped_rasters[0][1],
            nodata=0,
            resolution=ForestFireRiskSettings.DEFAULT_SCALE,
            start_year=None,
            end_year=None,
            subdir=None,  # ILSWESettings.SUB_DIR,
        )

        res.update(
            {
                "start": format_date(self.start_date),
                "end": format_date(self.end_date),
                "scale": ForestFireRiskSettings.DEFAULT_SCALE,
            }
        )
        # stats_obj = {
        #     "start": format_date(self.start_date),
        #     "end": format_date(self.end_date),
        #     "scale": ForestFireRiskSettings.DEFAULT_SCALE,
        #     "rasterfile": str(url),
        #     "nodata": 0,  # None, # nodata_count * (resolution or 1),
        #     "stats": daily_stats,
        #     "change_enum": str(ForestFireRiskEnum),
        #     "tiles": {"url": wms_url, "layer": layer},
        #     "legend": legend,
        # }

        # stats_obj = {
        #     "start": format_date(self.start_date),
        #     "end": format_date(self.end_date),
        #     "scale": ForestFireRiskSettings.DEFAULT_SCALE,
        #     "rasterfile": str(url),
        #     "nodata": 0,  # None, # nodata_count * (resolution or 1),
        #     "stats": daily_stats,
        #     "change_enum": str(ForestFireRiskEnum),
        #     "tiles": {"url": wms_url, "layer": layer},
        #     "legend": legend,
        # }
        # return stats_obj
        return res

    # def download_and_unzip_file(self, url, dest_file):
    # 	"""
    # 	Download file from the returned url
    # 	"""
    # 	#dest_file = self.generate_file_name()
    # 	fl = download_file(url, dest_file)
    # 	return unzip_file(file_path=fl,
    # 			use_temp_dir=True,
    # 			dest_dir=".",
    # 			return_full_path=True
    # 		)[0]

    def generate_file_name(self):
        """
        Generate random file name with a .zip extension
        """
        out_file = get_absolute_media_path(
            file_path=None,
            is_random_file=True,
            random_file_prefix="firerisk",
            random_file_ext=".zip",
            sub_dir=None,
            use_static_dir=False,
        )
        return out_file

    def get_file_path(self, url):
        return get_physical_file_path_from_url(self.request, url)

    def validate_periods(self):
        """
        Validate the start and end dates

        Returns:
                tuple (start_date, end_date, error)
        """
        start_date, end_date, error = validate_dates(
            start_date=self.start_date, end_date=self.end_date, both_valid=True
        )
        return (start_date, end_date, error)

    def validate_max_days(self):
        """
        Validate that the days specified are within range
        """
        days = days_between_dates(self.start_date, self.end_date)
        settings = get_ldms_settings()
        error = None
        if cint(days) > cint(settings.forest_fire_risk_max_days):
            error = _(
                "The maximum period you can assess fire risk is {0} days".format(
                    cint(settings.forest_fire_risk_max_days)
                )
            )
        return days, error

    def get_vector(self):
        return get_vector(
            admin_level=self.admin_level,
            shapefile_id=self.shapefile_id,
            custom_vector_coords=self.custom_vector_coords,
            admin_0=None,
            request=self.request,
        )

    def get_country_vector(self):
        return get_vector(
            admin_level=0,
            admin_0=self.admin_0,
            shapefile_id=self.admin_0,
            custom_vector_coords=None,  # self.custom_vector_coords,
            request=self.request,
        )

    def get_regional_vector(self):
        return get_vector(
            admin_level=-1,
            shapefile_id=RegionalAdminLevel.objects.first().id,
            custom_vector_coords=self.custom_vector_coords,
            admin_0=None,
            request=self.request,
        )

    def return_with_error(self, error):
        self.error = error
        return return_with_error(self.request, error)
