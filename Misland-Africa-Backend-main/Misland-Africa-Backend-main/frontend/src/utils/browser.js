const { detect } = require('detect-browser');

const is_browser_supported = () => {    
    const browser = detect();
    let is_supported = false;
    // handle the case where we don't detect the browser
    switch (browser && browser.name) {
        case 'chrome':
        // case 'firefox':
            console.log('supported');
            is_supported = true;
        break;
    
        case 'edge':
            console.log('kinda ok');
        break;
    
        default:
            console.log('not supported');
    }
    return is_supported;
}

export default {
    is_browser_supported
}