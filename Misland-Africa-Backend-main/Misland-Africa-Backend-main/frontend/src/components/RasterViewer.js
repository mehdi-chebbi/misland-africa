import React from "react";
import API from "../utils/api";
import FeatureDDL from "./FeatureDDL";
import RasterDDL from "./RasterDDL";
import FileUpload from "./FileUpload";
import Button from "./form/Button";
import 'leaflet/dist/leaflet.css';
import  * as L from 'leaflet/dist/leaflet.js'; 

export default class RasterViewer extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            rasterfile: '',
            data: {},
            mapInitialized: false
        }
        this.fileInput = React.createRef();
        this.handleRasterFileChange = this.handleRasterFileChange.bind(this);
    }

    handleRasterFileChange(evt) {
        this.setState({ rasterfile: evt.target.value }, () => this.getRaster());   
    }

    getRaster() {
        if(this.state.mapInitialized === false){
            this.initializeMap();
        }     
        var file = this.state.rasterfile;         
        fetch(API.get_api_endpoint(`rasters/${file}`), {
            method: 'get',
            headers: {"Content-Type": "application/json; charset=utf-8"}
        })
        .then(res => res.json())
        .then(data => {
            this.setState({ data: data });   
        //extract the features from loaded shape file            
        //  var feats = []
        //  data.features.features.map((feat, i) => {
        //      feats.push({ 'id': feat.id, "feature_name": feat.feature_name || feat.id })
        //  });
        //  this.setState({ features: feats }); 
        //  this.loadFeatures();
        });
    }

    uploadRasterFile = (evt) => {
        evt.preventDefault();
        const data = new FormData();
        var file = this.fileInput.current.getSelectedFile();
        data.append('raster', file);
        fetch(API.get_api_endpoint("rasters/upload/"), {
            method: 'PUT',            
            body: data
        }).then((response) =>  {
           return response.text();
        })
    }

    componentDidMount() {
    }

    initializeMap () {
        // initialize the map
        var map = L.map('raster-map').setView([42.35, -71.08], 13);

        // load a tile layer
        // L.tileLayer('http://tiles.mapc.org/basemap/{z}/{x}/{y}.png',
        // {
        //     attribution: 'Tiles by <a href="http://mapc.org">MAPC</a>, Data by <a href="http://mass.gov/mgis">MassGIS</a>',
        //     maxZoom: 17,
        //     minZoom: 9
        // }).addTo(map);

        // base map
        L.tileLayer('http://tiles.mapc.org/basemap/{z}/{x}/{y}.png',
        {
            attribution: 'Tiles by <a href="http://mapc.org">MAPC</a>, Data by <a href="http://mass.gov/mgis">MassGIS</a>',
            maxZoom: 17,
            minZoom: 9
        }).addTo(map);

        // // bike lanes
        // L.tileLayer('http://tiles.mapc.org/trailmap-onroad/{z}/{x}/{y}.png',
        // {
        //     maxZoom: 17,
        //     minZoom: 9
        // }).addTo(map); 
        
        /***Load OSS Tiles */
        var path = API.get_api_endpoint("tiles/tiles/4/{z}/{x}/{y}.png");
        path = path.replace("/api", "");
        //path = "http://0.0.0.0:8000/tiles/tiles/4/6/38/27.png";
        // var TopoLayer = L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
        var TopoLayer = L.tileLayer(path, {
            // attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
            // maxZoom: 18,
            // id: 'mapbox/streets-v11',
            // tileSize: 512,
            // zoomOffset: -1,
            // accessToken: 'your.mapbox.access.token'
            attribution: 'Tiles by <a href="http://mapc.org">MAPC</a>, Data by <a href="http://mass.gov/mgis">MassGIS</a>',
            maxZoom: 17,
            minZoom: 9

        }).addTo(map);

        /*
        var map = L.map('raster-map').setView([51.505, -0.09], 13);

        var path = API.get_api_endpoint("tiles/tiles/4/{z}/{x}/{y}.png");
        path = path.replace("/api", "");
        //path = "http://0.0.0.0:8000/tiles/tiles/4/6/38/27.png";
        // var TopoLayer = L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
        var TopoLayer = L.tileLayer(path, {
            attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
            maxZoom: 18,
            id: 'mapbox/streets-v11',
            tileSize: 512,
            zoomOffset: -1,
            accessToken: 'your.mapbox.access.token'
        }).addTo(map);
        /*
        var path = API.get_api_endpoint("tiles/tiles/{z}/{x}/{y}.png");
        var path = "http://0.0.0.0:8000/tiles/tiles/4/6/38/27.png";
        var TopoLayer = L.tileLayer(path, 
                { 
                    maxZoom: 16 
                });    
        map.addLayer(TopoLayer);
        */
        this.setState({mapInitialized: true})
    }

    render () {
        return (
            <div className="container">
                <div className="row">                     
                    <div className="col-sm-12">
                        <FileUpload name={'shapefile'} 
                        handleChange={this.handleRasterFileChange}
                        ref={this.fileInput} />
                        <Button 
                                disabled={this.state.disabled}
                                cls={'btn btn-primary btn btn-primary'}
                                title={'Upload Raster'}
                                action={this.uploadRasterFile}
                                type={'submit'}
                                />
                    </div>   
                </div>
                
                <div className="row">
                    <div className="col-sm-12">
                        <RasterDDL name={'rasterfile'} 
                                handleChange={this.handleRasterFileChange}/>
                    </div>
                </div>

                <div className="row">
                    <div className="col-sm-12">
                        <div id="raster-map" style={{ height: 400 }}>
                        </div>
                    </div>
                </div>
            </div>
        )
    }
}