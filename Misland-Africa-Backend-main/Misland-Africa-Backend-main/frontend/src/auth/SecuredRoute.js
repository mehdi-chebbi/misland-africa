import React from 'react';
import {Route} from 'react-router-dom';
import AUTH from './index';
import Login from "../components/auth/Login";

/**
 * The goal of this component is to restrict access to whatever route you configure on it
 * It takes two properties: another Component, so it can render it in case the user is authenticated; and a path, so it can configure the default Route component provided by React Router
 * However, before rendering anything, this component checks if the user isAuthenticated. If they are not, this component triggers the signIn method to redirect users to the login page.
 * @param {*} props 
 */
function SecuredRoute(props) {
    const {component: Component, path } = props;    
    return (
        <Route path={path} render={() => {
            if(!AUTH.isAuthenticated()) {
                return <Login /> //{/*<div></div>*/}
            }
            return <Component />
        }} />
    );
}

export default SecuredRoute;