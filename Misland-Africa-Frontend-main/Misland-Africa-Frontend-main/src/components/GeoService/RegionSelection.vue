<template>
  <SelectionForm>
    <!-- country -->
    <div class="q-my-sm">
      <div class="">Country</div>
      <q-select v-model="selected_country" dense outlined :options="countries" clearable @clear="handleSelectedCountry"
        @update:model-value="handleSelectedCountry"></q-select>
    </div>
    <!-- region -->
    <div class="q-my-sm">
      <div class="">Region</div>
      <q-select v-model="selected_region" dense outlined :options="regions" clearable @clear="handleSelectedRegion"
        @update:model-value="handleSelectedRegion"></q-select>
    </div>
    <!-- sub region -->
    <div class="q-my-sm">
      <div class="">Sub region</div>
      <q-select v-model="selected_sub_region" dense outlined :options="sub_regions" clearable
        @clear="handleSelectedSubRegion" @update:model-value="handleSelectedSubRegion"></q-select>
    </div>
    <div class="q-mt-md flex justify-end">
      <q-btn unelevated color="primary" style="border-radius: 4px;" no-caps @click="fetchGeoJson">Load geometry</q-btn>
    </div>
  </SelectionForm>
</template>
<script>
import { defineAsyncComponent } from "vue";
import { storeToRefs } from "pinia";
import { useGeometryStore } from "src/stores/geometry_store";
const { setGeometryData } = useGeometryStore();
export default {
  data() {
    return {
      selected_country: "",
      selected_region: "",
      selected_sub_region: "",
      countries: [], // holds list  of countries
      regions: [], // holds list of regions
      sub_regions: [], // holds list of sub regions
      current_geometry_selection: "", // holds the currently selected
    }
  },
  components: {
    SelectionForm: defineAsyncComponent(() => import('src/components/Reusables/SelectionForm.vue')),
  },
  mounted() {
    this.fetchCountries()
  },
  methods: {
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
        if (process.env.DEV) console.log("countries african countries ", this.countries);
      } catch (error) {
        if (process.env.DEV) console.log("ERROR: could not get countries list", error);
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
        this.current_geometry_selection = null;
        this.selected_region = null
        this.selected_sub_region = null
        return
      }
      this.fetchRegions()
      this.current_geometry_selection = val
      this.selected_region = null;
    },
    // handle the selected region within a country
    handleSelectedRegion(val) {
      if (!val) {
        this.current_geometry_selection = this.selected_country;
        this.selected_sub_region = null
        return
      }
      this.fetchSubregions()
      this.selected_sub_region = null
      this.current_geometry_selection = val
    },
    // handle the selected sub region within the selected region
    handleSelectedSubRegion(val) {
      if (!val) {
        this.current_geometry_selection = this.selected_region
        return
      }
      this.current_geometry_selection = val
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
          admin_0: this.selected_country?.id,
          name: this.current_geometry_selection?.label,
          vector: this.current_geometry_selection.id
        })
        this.$emit('close_region_selection_filter', true)
      } catch (error) {
        if (process.env.DEV) console.log("error fetching geoJson  ", error);
      }
    },
    //  method to transform level to vector
    adminLevel(level) {
      if (level === 0) return 'vect0';
      if (level === 1) return 'vect1';
      if (level === 2) return 'vect2';
    },
  },
}
</script>
<style lang="">

</style>
