import React from "react";
import API from "../utils/api";
import FeatureDDL from "./FeatureDDL";
import ShapeFileDDL from "./ShapeFileDDL";
import FileUpload from "./FileUpload";
import Button from "./form/Button";

export default class ShapeFileViewer extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            shapefile: '',
            data: {},
            features: [],
            feature_attributes: [],
            selected_feature_id: "",
            selected_feature: {}
        }
        this.fileInput = React.createRef();
        this.handleFeatureChange = this.handleFeatureChange.bind(this);
        this.handleShapeFileChange = this.handleShapeFileChange.bind(this);
    }
    componentDidMount() {

    }

    showFeatureAttributes() {
        this.state.feature_attributes.map((itm, i) => {
            console.log(itm.value)
        });
    }

    handleFeatureChange = (event) => {        
        this.setState({ selected_feature: {} });
        this.setState({ selected_feature_id: event.target.value });   
        this.state.data.features.features.map((feat, i) => {
            if(feat.id == event.target.value){
                this.setState({ feature_attributes: feat.properties.feature_attributes});
                this.setState({ selected_feature: feat }, ()=> {
                    this.showFeatureAttributes();                    
                });
            }
        }); 
    }

    loadFeatures = () => { 
        this.refs.feature_ddl.loadFeatures(this.state.features);  
    }

    getShapeFile(params){
        params = params || {};   
        this.setState({ shapefile: params.shapefile });
        var sh_file = this.state.shapefile;         
        fetch(API.get_api_endpoint(`shapefiles/${sh_file}`), {
            method: 'get',
            headers: {"Content-Type": "application/json; charset=utf-8"}
        })
        .then(res => res.json())
        .then(data => {
            this.setState({ data: data });   
            //extract the features from loaded shape file            
            var feats = []
            data.features.features.map((feat, i) => {
                feats.push({ 'id': feat.id, "feature_name": feat.feature_name || feat.id })
            });
            this.setState({ features: feats }); 
            this.loadFeatures();
        });
    }
    handleShapeFileChange = (event) => {
        this.setState({ shapefile: event.target.value }, () => this.getShapeFile());   
    }

    uploadShapeFile = (evt) => {
        evt.preventDefault();
        const data = new FormData();
        var file = this.fileInput.current.getSelectedFile();
        data.append('shapefile', file);
        fetch(API.get_api_endpoint("shapefiles/upload/"), {
            method: 'PUT',            
            body: data
        }).then((response) =>  {
           return response.text();
        })
    }

    render() {
        return (
            <div className="container">
                <div className="row">                     
                    <div className="col-sm-12">
                        <FileUpload name={'shapefile'} 
                        handleChange={this.handleShapeFileChange}
                        ref={this.fileInput} />
                        <Button 
                                disabled={this.state.disabled}
                                cls={'btn btn-primary btn btn-primary'}
                                title={'Upload Shapefile'}
                                action={this.uploadShapeFile}
                                type={'submit'}
                                />
                    </div>   
                </div>

                <div className="row">
                    <div className="col-sm-12">
                        <ShapeFileDDL name={'shapefile'} handleChange={this.handleShapeFileChange} />
                    </div> 
                </div>

                <div className="row">
                    <div className="col-sm-12">
                        {
                            !this.state.data && 
                            <h2>Page to preview a shapefile content</h2>
                        }   
                        {
                            // this.state.data && 
                            // <h4 className="hidden">Shapefile : {this.state.data.filename}</h4>
                        }   
                    </div>
                    <div className="col-sm-6">
                        {/* Empty div */}
                    </div>
                </div>
                
                <div className="row">
                    <div className="col-sm-12">
                        <FeatureDDL name="features_ddl" 
                            options={this.state.features} 
                            ref="feature_ddl"
                            handleChange={this.handleFeatureChange} />                         
                        {/* <span> Feature GeoJSON : 
                        { 
                            JSON.stringify(this.state.feature_attributes) 
                        } 
                        </span> */}
                        {
                        this.state.selected_feature &&
                        this.state.feature_attributes && 
                        <div>
                            <h3> Feature { this.state.selected_feature.id }  attributes
                            </h3>
                            <table className="table-bordered .table-dark">
                                <thead className="thead-dark">
                                    <tr>
                                        <th>
                                        Sr
                                        </th>
                                        <th>
                                        Attribute
                                        </th>
                                        <th>
                                        Value
                                        </th>
                                    </tr>
                                </thead>
                                <tbody>
                                {
                                    this.state.feature_attributes.map((attrib, i) => {
                                        return (
                                            <tr>
                                                <td>
                                                    { i+1 }
                                                </td> 
                                                <td>
                                                    { attrib.attribute }
                                                </td>                                                
                                                <td>
                                                    { attrib.value }
                                                </td>
                                            </tr>                                        
                                        );
                                    })
                                }
                                </tbody>
                            </table>
                        </div> 
                    }                    
                    </div>
                </div>
        </div>
        )
    }
} 
                