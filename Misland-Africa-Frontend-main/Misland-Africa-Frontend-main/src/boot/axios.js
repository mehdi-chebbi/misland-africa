import { boot } from 'quasar/wrappers'
import axios from 'axios'
import { Loading, QSpinnerGears } from "quasar";

// Quasar embeds this value at build time. Production builds must set
// API_BASE_URL to the public backend URL, including a trailing slash.
const baseURL = process.env.API_BASE_URL || '/'

const api = axios.create({ baseURL })

export default boot(({ app }) => {
  app.config.globalProperties.$axios = axios
  app.config.globalProperties.$api = api;

  //check request
  let pending_requests = 0;
  api.interceptors.request.use((config) => {

    const hide_loading_progress = config?.hide_loading_progress; //check if loader is shown or hidden
    console.log(" hide_loading_progress =========== ", hide_loading_progress);
    pending_requests++;
    if (!hide_loading_progress) Loading.show({
      spinner: QSpinnerGears,
      message: "Requesting ...",
      spinnerColor: "primary"
    });
    return config;
  }, (error) => {
    pending_requests--;
    setTimeout(() => {
      Loading.hide();
    }, 1000)
    return Promise.reject(error);
  });
  //check response
  api.interceptors.response.use((config) => {
    pending_requests--;
    if (pending_requests <= 0) {
      setTimeout(() => {
        Loading.hide();
      }, 1000)
    }
    return config;
  }, (error) => {

    pending_requests--;
    if (pending_requests <= 0) {
      setTimeout(() => {
        Loading.hide();
      }, 1000)
    }
    return Promise.reject(error);
  });


})

export { api, baseURL }
