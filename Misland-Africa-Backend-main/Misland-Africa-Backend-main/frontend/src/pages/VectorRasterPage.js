import React from "react";

import RasterViewer from "../components/RasterViewer";
import ShapeFileViewer from "../components/ShapeFileViewer";
import NavBar from "../components/layout/NavBar";

import API from "../utils/api";

export default class VectorRasterPage extends React.Component{
    constructor(){
        super();
        this.state = {
            shapefile: null
        }
        this.shapeFileUpload = React.createRef(); 
        this.rasterFileUpload = React.createRef();          
    }    
    render() {
        return (
            <div>
                <div className="container-fluid">
                    <NavBar />
                </div>
                <div className="container">
                    <div className="row">
                        <div className="col-sm-6">
                            <ShapeFileViewer ref="shapefile_viewer"/>
                        </div>   
                        <div className="col-sm-6">
                            <RasterViewer ref="raster_viewer"/>
                        </div>                   
                    </div>
                </div>
            </div>
        );
    }   
}