import React from "react";
import API from "../utils/api";
import Select from './form/Select';

export default class ShapeFileDDL extends React.Component {
    constructor(props) {
        super(props);
        this.state = {'isLoading': true, msg: 'Loading shapefiles...', shapefiles: []}
    }

    render() {
        return (
            <Select
                title={'Shapefile'}
                name={this.props.name}
                valuefield={'id'}
                displayfield={'filename'}
                options={this.state.shapefiles}                    
                placeholder={this.state.msg}
                handleChange={this.props.handleChange} 
            />
        );
    }

    componentDidMount(){    
        /*fetch(API.get_api_endpoint('shapefiles'))
        .then(res => res.json())
        .then(data => {                        
            this.setState({shapefiles: data, msg: 'Select Shapefile...', isLoading: false})
        });*/
    }
}