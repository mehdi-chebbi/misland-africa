import AUTH from '../auth/index';
import API from "../utils/api";

const getLoggedInUser = () => {
    return AUTH.isAuthenticated();
}

const getSubjects = async () => {    
    let subjects = await doRequest('user_subjects', {})
    return subjects;
}

const getStreams = async () => {    
    let streams = await doRequest('user_streams', {})
    return streams;
}

const getSubjectStreamsPairs = async () => {
    let pairs = await doRequest('getstaffallowedobjects');
    return pairs;
}
/**
 * Checks if the current user teaches the subject in a selected stream
 * @param {*} stream 
 * @param {*} subject 
 */
const isStreamSubjectCombinationValid = async (stream, subject) => {    
    let res = await doRequest('validate_stream_subject_combination', {'subject': subject, 'stream': stream});
    return res.valid === true;
}

const doRequest = async (route, params) => {
    let user = getLoggedInUser();
    if(!user){
        return [];
    }
    params = params || {};
    params['user'] = user.username;
    params['staff_id'] = user.username;
    let r = await fetch(API.get_api_endpoint(`${route}`), {
        method: 'post',
        body: JSON.stringify(params),
        headers: {"Content-Type": "application/json; charset=utf-8"}
    });
    return r.json();
}

export default {
    getLoggedInUser,
    getSubjects,
    getStreams,
    isStreamSubjectCombinationValid,
    getSubjectStreamsPairs
}