import React from "react";

/**
 * The <Select /> component displays a list of drop-down items. Usually, there will be a placeholder text or a default value for the drop-down. Here are the props for the <Select />:

 *  * title — The value of the title prop be displayed as label of the <select> element.
 *  * name — The name attribute for the <select> element.
 *  * options — An array of available options. For instance, we are using the <select /> to display a drop-down list of gender options. 
 *  * valuefield — The field for the option to be used as the value field
 *  * displayfield — The field for the option to be used as the label for each option
 *  * value — The value prop can be used to set the default value of the field.
 *  * placeholder — A short string that populates the first <option> tag.
 *  * handleChange — A control function that gets triggered when the input control element's value changes. The function then updates the state of the parent component and passes the new value through the value prop.
 */
export default class Select extends React.Component {   
    render() {
        return (
            <div className="form-group">
                <label htmlFor={this.props.name}>{this.props.title}</label>
                <select className="form-control"
                    id={this.props.name}
                    name={this.props.name}
                    value={this.props.value}
                    onChange={this.props.handleChange}
                    defaultValue={this.props.placeholder}
                    required
                    >
                    {/* <option value="" selected disabled>{this.props.placeholder || 'Select'} </option> */}
                    <option value={this.props.placeholder} disabled>{this.props.placeholder}</option>
                    {
                        this.props.options.map((option, i) => {
                            return (
                                <option
                                    key={i}
                                    value={option[this.props.valuefield]}
                                    label={option[this.props.displayfield]}
                                ></option>
                            );
                        })
                    }
                </select>
            </div>
        );
    }

    reloadItems(options) {
        debugger;
    }
}