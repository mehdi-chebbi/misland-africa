//see https://www.codementor.io/blizzerand/building-forms-using-react-everything-you-need-to-know-iz3eyoq4y
import React from "react";

/**
 * This is fairly similar to the <Input /> component that we created earlier. 
 * The <textarea /> element should accept additional props for rows and columns.

 */

export default class TextArea extends React.Component{
    render() {
        return (
            <div className="form-group"> 
                <label htmlFor={this.props.name} className="form-label">{this.props.title} : </label>
                <textarea 
                    rows={this.props.rows} 
                    cols={this.props.cols}                
                    className="form-input"
                    id={this.props.name}
                    name={this.props.name}
                    type={this.props.type}
                    value={this.props.value}
                    onChange={this.props.handleChange}
                    placeholder={this.props.placeholder}>
                 </textarea> 
            </div>
        );
    }
}