<template>
  <div class="geometry-selection-container flex  items-center">
    <!-- continental region selection -->
    <!-- <q-select borderless v-model="selected_continental_region" :options="continental_regions" use-input clearable
      :placeholder="selected_continental_region ? '' : 'Continental region'" popup-content-class="geometry-popup-class"
      behavior="menu" class="geometry-selection">
    </q-select> -->

    <!-- country selection -->
    <q-select borderless v-model="selected_country" :options="countries" use-input clearable
      :placeholder="selected_country ? '' : 'Country'" @update:model-value="handleSelectedCountry"
      popup-content-class="geometry-popup-class" behavior="menu" class="geometry-selection">
    </q-select>

    <!-- region within a country selection -->
    <q-select borderless v-model="selected_region" :options="regions" use-input clearable
      :placeholder="selected_region ? '' : 'Region'" @update:model-value="handleSelectedRegion"
      popup-content-class="geometry-popup-class" behavior="menu" class="geometry-selection">
    </q-select>

    <!-- sub region within a country selection -->
    <q-select borderless v-model="selected_sub_region" :options="sub_regions" use-input clearable
      :placeholder="selected_sub_region ? '' : 'Sub Region'" @update:model-value="handleSelectedSubRegion"
      popup-content-class="geometry-popup-class" behavior="menu" class="geometry-selection">
    </q-select>

  </div>
</template>

<script>
import { storeToRefs } from "pinia";
import { useGeometryStore } from "src/stores/geometry_store";
const { setGeometryData } = useGeometryStore();
export default {
  data() {
    return {
      selected_continental_region: "", //
      selected_country: "",//
      selected_region: "",//
      selected_sub_region: "", //
      current_geometry_selection: "", // holds the currently selected
      continental_regions: [], // holds list of continental regions
      countries: [], // holds list  of countries
      regions: [], // holds list of regions
      sub_regions: [], // holds list of sub regions
    }
  },
  computed: {
  },
  mounted() {
    this.fetchCountries()
    this.handleDefaults();
  },
  methods: {
    //set default values
    handleDefaults() {
      this.selected_country =
      // {
      //   "label": "Mauritania",
      //   "value": 7,
      //   "id": 7,
      //   "gid_0": "MRT",
      //   "name_0": "Mauritania",
      //   "level": 0
      // }
      {
        "label": "Tunisia",
        "value": 1,
        "id": 1,
        "gid_0": "TUN",
        "name_0": "Tunisia",
        "level": 0
      }
      this.selected_region =
      // {
      //   "label": "Nouakchott",
      //   "value": 157,
      //   "id": 157,
      //   "admin_zero_id": 7,
      //   "name_1": "Nouakchott",
      //   "level": 1
      // };
      {
        "label": "Ariana",
        "value": 8,
        "id": 8,
        "admin_zero_id": 1,
        "admin_0": 1,
        "name_1": "Ariana",
        "level": 1
      }
      this.fetchRegions()
      this.handleSelectedRegion(this.selected_region)
    },
    // fetch all counties list
    async fetchCountries() {
      try {
        const response = await this.$api.get("/api/vect0/", {
          params: {
            include: 'all'
          }
        });
        this.countries = response.data?.map(country => {
          return {
            label: country.name_0,
            value: country.id,
            ...country,
            level: 0
          }
        })
        if (process.env.DEV) console.log("dashboard countries african countries ", this.countries);
      } catch (error) {
        if (process.env.DEV) console.log("ERROR: could not get countries list in dashboard", error);
      }
    },
    // fetch all regions within a country
    async fetchRegions() {
      try {
        const response = await this.$api.get("/api/vect1/",
          {
            params: {
              pid: this.selected_country.value,
            },
          }
        );
        this.regions = response.data?.map(region => {
          return {
            label: region.name_1,
            value: region.id,
            ...region,
            level: 1
          }
        })
        if (process.env.DEV) console.log("Regions ", this.regions);
      } catch (error) {
        if (process.env.DEV) console.log("ERROR: could not get region list", error);
      }
    },
    // fetch all subregions within a region
    async fetchSubregions() {
      try {
        const response = await this.$api.get("/api/vect2/",
          {
            params: {
              pid: this.selected_region.value,
            },
          });
        this.sub_regions = response.data?.map(sub_region => {
          return {
            label: sub_region.name_2,
            value: sub_region.id,
            ...sub_region,
            level: 2
          }
        })
        if (process.env.DEV) console.log("sub regions ", this.sub_regions);
      } catch (error) {
        if (process.env.DEV) console.log("ERROR: could not get sub region list", error);
      }
    },
    // handle the selected country
    handleSelectedCountry(val) {
      if (!val) {

        return
      }
      this.fetchRegions()
      this.current_geometry_selection = val
      this.selected_region = null
      this.fetchGeoJson();
    },
    // handle the selected region within a country
    handleSelectedRegion(val) {
      if (!val) {
        this.current_geometry_selection = this.selected_country
        this.fetchGeoJson();
        return
      }
      this.fetchSubregions()
      this.selected_sub_region = null
      this.current_geometry_selection = val
      this.fetchGeoJson();
    },
    // handle the selected sub region within the selected region
    handleSelectedSubRegion(val) {
      if (!val) {
        this.current_geometry_selection = this.selected_region
        this.fetchGeoJson();
        return
      }
      this.current_geometry_selection = val
      this.fetchGeoJson();
    },
    //  method to transform level to vector
    adminLevel(level) {
      if (level === 0) return 'vect0';
      if (level === 1) return 'vect1';
      if (level === 2) return 'vect2';
    },
    //fetch the geometry
    async fetchGeoJson() {
      try {
        if (!this.current_geometry_selection) return;
        if (process.env.DEV) console.log("current geometry selection ", this.current_geometry_selection);
        const level = this.current_geometry_selection.level;
        const geometry_response = await this.$api.get(
          `/api/${this.adminLevel(level)}/${this.current_geometry_selection?.id}`
        );
        // store the geometry in the store
        setGeometryData({
          geojson: geometry_response.data,
          ...this.current_geometry_selection,
          admin_level: level,
          admin_0: this.selected_country?.id ,
          name: this.current_geometry_selection?.label,
          vector: this.current_geometry_selection.id
        })

      } catch (error) {
        if (process.env.DEV) console.log("error fetching geoJson  ", error);
      }
    },
  },
}
</script>

<style lang="scss" scoped>
.geometry-selection-container {
  background: #F8F9F4;
  border-radius: 12px;
  padding: 0px 10px 0px 10px;
  color: #A8AF7F;
  // flex-wrap: nowrap;

  width: 100%;

}
</style>

<style lang="scss" >
.geometry-popup-class {
  color: #A8AF7F;
  font-family: 'Inter';
  font-style: normal;
  font-size: 16px;
}

.geometry-selection {
  flex: 1;
  padding: 0px 0px;
}

.selected-geomery-class {
  color: #A8AF7F;
  font-family: 'Inter';
  font-style: normal;
  font-weight: 500;
  font-size: 16px;
}
</style>
