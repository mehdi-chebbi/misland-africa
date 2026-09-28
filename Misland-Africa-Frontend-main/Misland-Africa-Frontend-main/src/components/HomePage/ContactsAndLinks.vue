<template>
  <div class="flex justify-between q-px-md">
    <!-- logos -->
    <div class="col-md-3 col-xs-12  misland-oss-logo">
      <div class="flex items-center col-xs-6">
        <img src="~assets/png/misland.png" style=" width:70px;object-fit: contain;">
        <div class="misland-name">Misland</div>
      </div>
      <div class="q-my-sm col-xs-6"> <img src="~assets/png/core_team_logos/OSS.png"
          style=" width:120px;object-fit: contain;">
      </div>
    </div>
    <!-- contacts -->
    <div class="col-md-3 col-xs-12">
      <div class="contacts-title">Observatoire du Sahara et du Sahel</div>
      <div class="q-my-xs contacts-text">Boulevard du Leader Yasser Arafat</div>
      <div class="q-my-xs contacts-text">(+216) 71 206 633/634</div>
      <div class="q-my-xs contacts-text">(+216) 71 206 636</div>
      <div class="q-my-xs contacts-text">boc@oss.org.tn</div>
    </div>
    <!-- resources -->
    <div class="col-md-3">
      <div class="contacts-title">{{ $t("contacts_and_links.resources.title")}}</div>
      <div class="q-my-xs ">
        <a href="https://plugins.qgis.org/plugins/MISLAND/#plugin-about" target="_blank" class="contacts-text no-link-decoration">{{ $t("contacts_and_links.resources.qgis_link")}}</a>
      </div>
      <div class="q-my-xs ">
        <a href="http://" target="_blank" class="contacts-text no-link-decoration"> {{ $t("contacts_and_links.resources.video_recording")}}</a>
      </div>
      <div class="q-my-xs ">
        <a href="https://misland.readthedocs.io/en/latest/index.html" target="_blank" class="contacts-text no-link-decoration"> {{ $t("contacts_and_links.resources.documentation")}}</a>
      </div>
    </div>
    <!-- resources -->
    <div class="col-md-3">
      <div class="contacts-title">{{ $t("contacts_and_links.community.title")}}</div>
      <div class="q-my-xs ">
        <a href="https://www.oss-online.org/" target="_blank" class="contacts-text no-link-decoration"> {{ $t("contacts_and_links.community.oss_line")}} </a>
      </div>
      <div class="q-my-xs ">
        <a href="https://locateit.co.ke/" target="_blank" class="contacts-text no-link-decoration"> {{ $t("contacts_and_links.community.locate_it")}}</a>
      </div>

    </div>

  </div>
</template>
<script>
export default {

}
</script>
<style lang="scss" scoped>
.misland-name {
  color: #697523;
  font-weight: 900;
  font-size: 20px;
}

.misland-oss-logo {
  @media (min-width: $breakpoint-md-min) {}

  @media (max-width: $breakpoint-sm-max) {
    width: 100%;
    display: flex;
    justify-content: space-between;
    margin: 20px 0px;

  }
}

.contacts-title {
  color: #697523;
  font-weight: 700;
  font-size: 20px;
}

.contacts-text {
  color: #4A5219;
  font-weight: 500;
  font-size: 16px;
}
</style>
