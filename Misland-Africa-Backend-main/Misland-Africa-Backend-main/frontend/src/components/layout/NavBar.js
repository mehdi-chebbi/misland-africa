import React from "react";
import {withRouter, Redirect} from "react-router-dom";
import AUTH from "../../auth/index";
// import SchoolBanner from "../SchoolBanner";

class NavBar extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            authenticated: false,
            user: null
        }
    }

    signOut = () => {
        //auth0Client.signOut();
        this.props.history.replace('/');
        console.log("Sign out");       
    }    

    componentDidMount(){       
        var user = AUTH.isAuthenticated();
        this.setState({user, authenticated: user !== null})
    }

    showUserProfile() {
        // this.props.history.push("/me");
        // return <Redirect to="/me" />
    }

    logout() {
        // AUTH.logout();
        // this.props.history.push("/login");
        // return <Redirect to="/login" />
    }

    showHomePage() {        
        // this.props.history.push('/');
        // return <Redirect to="/" />
    }

    render() {
        var user = null;// this.props.location.state ? this.props.location.state.user : null;
        if(user === null){
            user = AUTH.isAuthenticated();
        }
        const authenticated = user !== null;    
        if(!authenticated){
            return <Redirect to="/login" />
        }
        let hrefLink = '#';
        return (
            // <nav className="navbar navbar-dark bg-primary fixed-top">         
            <nav className="navbar navbar-dark bg-primary ">            
                <a className="navbar-brand nav-link" href={hrefLink} tabIndex="-1" aria-disabled="true" onClick={()=> this.showHomePage() }>
                    {                   
                        authenticated &&
                        <div>
                            {/* <SchoolBanner /> */}
                        </div>
                    }
                </a>
                <a className="navbar-brand nav-link" href={hrefLink} tabIndex="-1" aria-disabled="true" onClick={()=> this.showHomePage() }>
                    Manage vector and raster files
                </a>
                <div>
                    {/* <label className="mr-2 text-white">Steve Nyaga</label> */}
                    {                   
                        !authenticated &&
                        <div>
                            {/* <button className="btn btn-light" onClick={() => { AUTH.login() }}>Sign In</button> */}
                            {/* <BrowserRouter>
                                <Link to="/login" className="btn btn-light App-link">Login</Link>
                            </BrowserRouter>*/}
                        </div>
                    }                    
                    {   
                        authenticated &&
                        <div>
                            <div className="btn-group">
                                <button type="button" className="btn btn-primary dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                                    {user.name}
                                </button>
                                <div className="dropdown-menu">
                                    {/* <a className="dropdown-item" href="#">Change Password</a>*/}
                                    <a className="dropdown-item" href={hrefLink} onClick={()=>this.showUserProfile() }>View Settings</a>
                                    {/* <Link to="/me"> Me</Link> */}
                                    <div className="dropdown-divider"></div>
                                    <a className="dropdown-item" href={hrefLink} onClick={()=> this.logout()} >Log Out</a>
                                </div>
                            </div>
                            <button className="btn btn-light App-link" onClick={()=> {this.logout()}}>Log Out</button>
                        </div>
                    }
                </div>
            </nav>
         );
    }
}
/**withRouter is a component provided by React Router to enhance your component with navigation capabilities (e.g., access to the history object). */
//export default withRouter(NavBar);
export default NavBar;