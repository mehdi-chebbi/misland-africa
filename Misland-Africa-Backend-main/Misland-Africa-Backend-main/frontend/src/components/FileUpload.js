import React from "react";

class FileUpload extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            data: [],
            loaded: false,
            placeholder: "Loading..."
        }
        this.fileInput = React.createRef();
    }

    componentDidMount() {

    }

    getSelectedFile() {
        return this.fileInput.current.files[0];
    }

    render() {
        return (
            <form className="form">
                <div className="form-group row">
                    <label htmlFor="fileControlFile1">Upload</label>
                    <input type="file" className="form-control-file btn btn-info btn-sm" 
                    id="fileControlFile1" ref={this.fileInput}  /> 
                </div>
                {/* <div classNam="form-group row text-left">
                    <input type="submit" className="btn btn-primary" value="Upload Shapefile" name="submit" />
                </div> */}
            </form>
        )
    }
}

export default FileUpload;