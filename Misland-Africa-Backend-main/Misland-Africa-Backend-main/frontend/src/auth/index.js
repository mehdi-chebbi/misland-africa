const isAuthenticated = () => {    
    let user = JSON.parse(localStorage.getItem('user'));
    return user;
}

const logout = async () => {
    // remove user from local storage to log user out
    localStorage.removeItem('user');
}

export default {
    isAuthenticated,
    logout
};