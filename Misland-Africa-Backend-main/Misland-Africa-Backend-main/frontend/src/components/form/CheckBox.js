import React from "react";

//See https://www.codementor.io/blizzerand/building-forms-using-react-everything-you-need-to-know-iz3eyoq4y
/**
 * Checkboxes might appear a bit more complicated because arrays are involved. But both <CheckBox> and <Select> are similar in terms of props. The major difference lies in how the state is updated. The props are.

 * title — Already covered.
 * name — Already covered.
 * options — An array of available options. The array is usually composed of strings that end up being the label and the value of each checkbox.
 * selectedOptions — An array of selected values. If the user had selected certain choices beforehand, the selectedOptions array would be populated with those values. This is synonymous to the <Select /> component's value prop.
 * handleChange — handleChange — A control function that gets triggered when the input control element's value changes. The function then updates the state of the parent component and passes the new value through the value prop.

 */
export default class Checkbox extends React.Component{
    render(){
        return (
            <div>
                <label htmlFor={this.props.name} className="form-label">{this.props.title}</label>
                <div className="checkbox-group">
                    {
                        this.props.options.map(option => {
                            return (
                                <label key={option[this.props.valuefield]}>
                                    <input 
                                        className="form-checkbox"
                                        id={this.props.name}
                                        name={this.props.name}
                                        onChange={this.props.handleChange}
                                        value={option[this.props.valuefield]}
                                        checked={this.props.selectedOptions.indexOf(option[this.props.valuefield]) > -1 }
                                        type="checkbox"
                                    /> {option[this.props.displayfield]}
                                </label>
                            );
                        })
                    }
                </div>
            </div>
        );
    }
}