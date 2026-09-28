require('dotenv').config()

export const SERVER_URL = process.env.SERVER_URL;
export const SERVER_PORT = process.env.SERVER_PORT;

export default {
    SERVER_PORT,
    SERVER_URL
}