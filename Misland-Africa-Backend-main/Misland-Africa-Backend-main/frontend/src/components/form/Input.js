//see https://www.codementor.io/blizzerand/building-forms-using-react-everything-you-need-to-know-iz3eyoq4y
import React from "react";

/**
 * General component description in JSDoc format. Markdown is *supported*.
 * The <Input /> component displays a one-line input field. The input type could be either text or number. Let's have a look at the props that we need to create an <Input /> component.
 
 *  * type — The type prop determines whether the input field rendered is of type, text, or number. For instance, if the value of type is equal to number, then <input type="number" /> will be rendered. Otherwise, <input type="text" /> gets rendered.
 *  * title — The value of the title prop will be displayed as a label of that particular field.
 *  * name — This is the name attribute for the input.
 *  * value — The value (either text or number) that should be displayed inside the input field. You can use this prop to give default value.
 *  * placeholder — An optional string that you can pass so that the input field displays a placeholder text.
 *  * handleChange — A control function that gets triggered when the input control element's value changes. The function then updates the state of the parent component and passes the new value through the value prop.

 */
export default class Input extends React.Component {
    render() {
        return (
            <div className="form-group"> 
                <label htmlFor={this.props.name} className="form-label">{this.props.title} </label>
                <input
                    className="form-input form-control"
                    id={this.props.name}
                    name={this.props.name}
                    type={this.props.type}
                    value={this.props.value}
                    onChange={this.props.handleChange}
                    placeholder={this.props.placeholder}
                />
            </div>
        );
    }
}