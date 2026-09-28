import React from "react";

/**
 * Buttons are easiest of the lot. You can keep the <Button /> component fairly simple and easy. Here is are the list of props that a button requires:

 * * title — Text for the button.
 * * action — Callback function
 * * style — Style objects can be passed as props.

 */
export default class Button extends React.Component {
    render() {
        return (
            <button 
                disabled={this.props.disabled}
                className={this.props.cls}
                onClick={this.props.action}
            >{this.props.title}
            </button>
        );
    }
}