import React from "react";
//import config from "../../server/config";
import API from "../utils/api";
import Select from './form/Select';

export default class RasterDDL extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
                'isLoading': true, 
                 msg: 'Loading rasters...', 
                 rasters: []}
    }

    render() {
        return (
            <Select
                title={'Rasters'}
                name={this.props.name}
                valuefield={'id'}
                displayfield={'name'}
                options={this.state.rasters}                    
                placeholder={this.state.msg}
                handleChange={this.props.handleChange} 
            />
        );
    }

    componentDidMount(){    
        fetch(API.get_api_endpoint('rasters'))
        .then(res => res.json())
        .then(data => {                        
            this.setState({rasters: data, msg: 'Select raster...', isLoading: false})
        });
    }
}