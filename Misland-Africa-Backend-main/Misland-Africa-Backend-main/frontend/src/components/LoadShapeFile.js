import React from "react";

class LoadShapeFile extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            data: [],
            loaded: false,
            placeholder: "Loading..."
        };
    }

    componentDidMount() {
        fetch("api/shapefiles", { mode: 'no-cors' })
        .then(response => {
            if(response.status > 400) {
                return this.setState(() => {
                    return { placeholder: "Something went wrong!"}
                });
            }
            return response.json();
        })
        .then(data => {
            this.setState(() => {
                return {
                    data,
                    loaded: true
                };
            });
        });
    }

    render() {
        return (
            <ul>
                {this.state.data.map(shp => {
                    return (
                        <li key={shp.id}>
                            {shp.filename}
                        </li>
                    )
                })}
            </ul>
        )
    }
}

export default LoadShapeFile;