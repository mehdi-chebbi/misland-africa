import React from "react";
//import config from "../../server/config";
import API from "../utils/api";
import Select from './form/Select';

export default class FeatureDDL extends React.Component {
    constructor(props) {
        super(props);
        this.state = {'isLoading': true, msg: 'Loading features...', features: []}
    }

    render() {
        return (
            <Select
                title={'Shapefile Features'}
                name={this.props.name}
                valuefield={'id'}
                displayfield={'feature_name'}
                options={this.state.features}                    
                placeholder={this.state.msg}
                handleChange={this.props.handleChange} 
            />
        );
    }

    loadFeatures(options) {
        //Assumption is that options will have the same structure as the earlier options
        //You need to pass displayfield and valuefield as props when creating the control
        var displayfield = 'feature_name';
        var valuefield = 'id';
        var id = this.props.name;
        var ddl = document.getElementById(id);
        var count = ddl.options.length;
        for(var i=0; i<count; i++){
            ddl.removeChild(ddl.options[0]);
        }
        for(var i=0; i<options.length; i++){
            var itm = options[i];
            var opt = document.createElement("option");
            opt.text = itm[displayfield];
            opt.value = itm[valuefield];
            ddl.appendChild(opt)
        }      
    }
    componentDidMount(){    
        // fetch(API.get_api_endpoint('shapefiles'))
        // .then(res => res.json())
        // .then(data => {                        
        //     this.setState({shapefiles: data, msg: 'Select Shapefile...', isLoading: false})
        // });
    }
}