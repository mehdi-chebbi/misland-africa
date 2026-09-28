# oss-ldms

Backend server for OSS Land Degradation Monitoring Service (LDNS). The system provides API endpoints to facilitate interaction

## Loading Sample Vector data

#### Assumptions:

- That you have set up a DJango environment
- That you have this code repository in your local computer
- That you have extracted the shapefiles into your local disk

#### To import the data:

- Activate the virtual env
- cd to the directory containing this repo
- Run <pre> pip install -r requirements.txt </pre>
- Run <pre> python manage.py shell </pre>
- Navigate to ldms/load.py and set **tunisia_imported** and
  **algeria_imported** variables appropriately. Set True if data for the respectively country has been imported, else set it to False

- Run

```ruby
        from ldms import load
        load.import_level_zero_shape_files()
        load.import_level_one_shape_files()
        load.import_level_two_shape_files()
```

- The shapefile data is successfully loaded and can be viewed with DJango admin

## 1. Vector data APIs

**NB:** For more details about the API, go to http://SERVER_URL/api-docs/

### 1.1 Listing APIs

The Listing API retrieves basic information about an admin **BUT** excludes the geo data

- Retrieve list of **Regional Level** admins
<pre> SERVER_URL/api/vectregional/ </pre>

- Retrieve list of **Level Zero** admins
<pre> SERVER_URL/api/vect0/ </pre>

- Retrieve list of **Level One** admins
<pre> SERVER_URL/api/vect1/ </pre>

- Retrieve list of **Level Two** admins
<pre> SERVER_URL/api/vect2/ </pre>

### 1.2 Detail APIs

The detail API retrieves a specific object together with its geo data

- Retrieve a specific **Regional Level** admin
<pre> SERVER_URL/api/vectregional/ADMIN_ID/ </pre>

- Retrieve a specific **Level Zero** admin
<pre> SERVER_URL/api/vect0/ADMIN_ID/ </pre>

- Retrieve a specific **Level One** admin
<pre> SERVER_URL/api/vect1/ADMIN_ID/ </pre>

- Retrieve a specific **Level Two** admin
<pre> SERVER_URL/api/vect2/ADMIN_ID/ </pre>

### 1.3 Filtering APIs

The Listing API filters and retrieves a list of admins based on the parent level. For example, get the list of Admin Level One given the Admin Level Zero Id, or get the list of Admin Level Two given Admin Level One Id. These APIs retrieve basic information about an admin **BUT** excludes the geo data

- For admin level zero, the system by default returns the published countries as specified in the **.env** file. If you need a list of all countries, please do the following
<pre> SERVER_URL/api/vect1/?include=all </pre>

- Retrieve list of **Level One** admins
<pre> SERVER_URL/api/vect1/?pid=PARENT_ADMIN_ID </pre>

- Retrieve list of **Level Two** admins
<pre> SERVER_URL/api/vect2/?pid=PARENT_ADMIN_ID </pre>

## 2. Raster data APIs

- To get a list of rasters
<pre> SERVER_URL/api/rasters/ </pre>

- Retrieve list of **Raster Types**
<pre> SERVER_URL/api/rastertype/ </pre>

- Retrieve a specific **Raster Type**
<pre> SERVER_URL/api/rastertype/RASTER_TYPE_ID/ </pre>

- Retrieve a specific raster
<pre> SERVER_URL/api/rasters/RASTER_ID/ </pre>

- Retrieve rasters by raster_type
<pre> SERVER_URL/api/rasters/?type=RASTER_TYPE_ID</pre>

- To load a raster by tiles
<pre> SERVER_URL/tiles/tiles/RASTER_ID/{z}/{x}/{y}.png </pre>

## 3. Visualization APIs

- For more details, see https://gitlab.com/locateit/oss-land-degradation-monitoring-service/oss-ldms/-/issues/3

- The backend allows calculation of raster statics based on vector geometries. In other words, we provide a shapefile upon which the raster is overlaid for statistics computation. To perform the computations, call make a **POST** request to the API endpoints listed herewith.

### Land Use Land Cover (LULC)

#### Introduction

> **API Endpoint**: <pre> SERVER_URL/api/lulc/
> **Request Type**: POST
> **Purpose**: Estimate land use land cover
> **Sub-indicators**: - LULC computes the LULC for one single year

                      - LULC_CHANGE computes the LULC for two periods

#### Parameters

- **vector (int)**: Either the ID of an existing shapefile.
- **admin_level (int)**: The administrative level for the polygon to be used in case a shapefile id has been provided for the parameter **vector**.
- **raster_type (int)**: The type of raster files to be used
- **start_year (int)**: Starting year for which raster files should be used.
- **end_year (int)**: End year for which raster files should be used.
- **show_change (int)**: When it is 0, LULC will be calculated, when it is 1, LULC_CHANGE will be computed. When this parameter is set as 1, the API will return a url to a raster containing the transition map
- **custom_coords (GeoJSON, or GEOSGeometry)**: Coordinates which may be as a result of a custom drawn polygon or a Geometry object in form of GeoJSON. An example of a polygon is <pre>MULTIPOLYGON((( 1 1, 1 2, 2 2, 1 1))) </pre>

**NB**: Where time series computations are to be performed, provide both **start_year** and **end_year** parameters need to be provided.

- A quick way to test the API is to run this command:

<pre> curl -H "Content-Type: application/json" --data  '{"start_year":2002,"end_year":20,"raster_type":1,"transform":"area", "level":2, "vector":2}' 'http://172.105.246.124/api/visual/'
</pre>

## Authentication

### Introduction

See https://simpleisbetterthancomplex.com/tutorial/2018/12/19/how-to-use-jwt-authentication-with-django-rest-framework.html for more details

We are using JWT for authentication. The JWT is just an authorization token that should be included in all requests. For example

<pre>
curl http://127.0.0.1:8000/hello/ -H 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNTQzODI4NDMxLCJqdGkiOiI3ZjU5OTdiNzE1MGQ0NjU3OWRjMmI0OTE2NzA5N2U3YiIsInVzZXJfaWQiOjF9.Ju70kdcaHKn1Qaz8H42zrOYk0Jx9kIckTn9Xx7vhikY'
</pre>

### Register a new user

- Make a POST request to SERVER_URL/api/signup/. The payload should be similar to

<pre> 
{
    "first_name": "Dummy first name",
	"last_name": "Dummy last name",
	"email": "humptydumpty@monkey.com",
	"password": "password",
    "password2": "password",
    "profile": {
        "profession": "I.T",
	    "institution": "IAT",
	    "title": "Dr."
    }
}
</pre>

- `password2` holds the value of "Confirm password field"
- If the request is successful, an object containing the user of the following form will be returned. Otherwise an error will be returned
<pre>
{
    "success": "true",
    "status_code": 201,
    "message": "User registered successfully"
}
</pre>

### Log in

- First step is to authenticate and obtain the token. The endpoint is **/api/login/** and it only accepts POST requests.

- To obtain token, make a POST request to **/api/login/** and pass valid values as shown by this object

<pre> 
 {
    "email": "admin@admin.com",
    "password": "123"
 }
</pre>

Example is:

<pre>http post SERVER_URL/api/login/ email=admin@admin.com password=123</pre>

The response will be of the form

<pre>
{
    "success": "true",
    "status_code": 200,
    "message": "User logged in successfully",
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImFkbWluQGFkbWluLmNvbSIsImV4cCI6MTYwNDY1NTYyOSwiZW1haWwiOiJhZG1pbkBhZG1pbi5jb20ifQ.E0jHx5QHYevc2HaLOJo8-kHaOTaJ7oUCu5QeQIhalow"
}
</pre>

- After that you are going to store both the access token on the client side, usually in the localStorage.

- In order to access the protected views on the backend (i.e., the API endpoints that require authentication), you should include the access token in the header of all requests, like this:

<pre>
curl http://127.0.0.1:8000/hello/ "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNTQ1MjI0MjAwLCJqdGkiOiJlMGQxZDY2MjE5ODc0ZTY3OWY0NjM0ZWU2NTQ2YTIwMCIsInVzZXJfaWQiOjF9.9eHat3CvRQYnb5EdcgYFzUyMobXzxlAVh_IAgqyvzCE"
</pre>

### Update existing user details

- Make a POST request to SERVER_URL/api/updateuser/. The payload should be similar to

<pre> 
{
    "email": "humptydumpty@monkey.com",
    "first_name": "Dummy first name",
    "last_name": "Dummy last name",
    "is_active": 1,
    "is_admin": 1,
	"profile": {
        "profession": "Support",
        "institution": "Twitter",
        "title": "Professor.",
        "can_upload_custom_shapefile": 0, 
        "can_upload_standard_raster": 1
    }
}

</pre>

- If the request is successful, an object containing the user of the following form will be returned. Otherwise an error will be returned

<pre>
{
    "success": "true",
    "status_code": 200,
    "message": "User details updated successfully"
}
</pre>

**NB**: This endpoint will be used to make any form of change to the registered users including activating or deactivating a user. However, the username will not be updated since
it forms the unique key

### Change User Password

- Make a POST request to **/api/changepwd/** and pass valid values as shown by this object

<pre> 
{
    "email": "admin@admin.com",
    "old_password": "123",
    "new_password": "456",
    "confirm_password": "456"
}
</pre>

### Get a list of existing users

- Make a GET request to SERVER_URL/api/users/
- You need to be authenticated to retrieve a user's details. Pass the authentication token when making the request
- Only admin users can make this query
- The call returns an object of this form

<pre>
[
    {
        "email": "humptydumpty@monkey.com",
        "first_name": "",
        "last_name": "",
        "is_admin": false,
        "profile": {
            "institution": "IAT",
            "profession": "I.T",
            "title": "Dr.",
            "can_upload_custom_shapefile": false,
            "can_upload_standard_raster": false
        }
    },
    {
        "email": "stevenyaga@gmail.com",
        "first_name": "Steve",
        "last_name": "Nyaga",
        "is_admin": false,
        "profile": {
            "institution": "Maps Inc.",
            "profession": "Accountant",
            "title": "Surveyor",
            "can_upload_custom_shapefile": true,
            "can_upload_standard_raster": true
        }
    }
]
</pre>

### Delete User

- Make a POST request to **/api/requestuserdelete/** and pass the email address of the user that wishes to delete their account

<pre> 
{
    "email": "admin@admin.com", 
}
</pre>

- An email will be sent to the email address specified with a link to confirm account deletion. The link comes in this format: http://localhost:8000/#/dashboard/deleteuser/MTEx/csk6e0-9d7944fac499eef9359f1d201c1ed6e3/
- When a user clicks this link, the front will extract the parameters portion of this url i.e deleteuser/MTEx/csk6e0-9d7944fac499eef9359f1d201c1ed6e3/ for the above sample url
- Make a POST call to the deleteuser backend API for the deletion of user account to be completed. This logic is similar to user account activation

### Get details of the current user

- Make a GET request to SERVER_URL/api/user/
- You need to be authenticated to retrieve a user's details. Pass the authentication token when making the request
- This will return the details of the currently logged in user
- The query returns data in this form:

<pre>
{
    "success": "true",
    "status_code": 200,
    "message": "User profile fetched successfully",
    "data": [
        {
            "email": "admin@admin.com",
            "first_name": "Admin",
            "last_name": "Admin",
            "profession": "Support",
            "institution": "Twitter",
            "title": "Prof",
            "is_active": 1,
            "is_admin": 1,
            "can_upload_custom_shapefile": 0,
            "can_upload_standard_raster": 1
        }
    ]
}
</pre>

### Get details of another user

- Make a GET request to SERVER_URL/api/user/?email=USER_EMAIL
- You need to be authenticated to retrieve a user's details. Pass the authentication token when making the request
- This will return the details of the user matching the specified email address

### Get List of years that have data

- This endpoint returns data in **Published Computation** table that indicates years that have data for different computation types
- Make a **GET** request to **SERVER_URL/api/computationyears/**

### Get List of precomputations

- This endpoint returns precomputations that have been scheduled and succeeded for the purposes of the dashboard
- Make a **GET** request to **SERVER_URL/api/precomputations/**
- Sample data is as below:

<pre>
[
    {
        "computation_type": "LULC",
        "start_year": 2020,
        "end_year": 2020,
        "admin_zero": 1
    },
    {
        "computation_type": "LULC",
        "start_year": 2020,
        "end_year": 2020,
        "admin_zero": 2
    },
    {
        "computation_type": "LULC Change",
        "start_year": 2020,
        "end_year": 2021,
        "admin_zero": 1
    },
    {
        "computation_type": "LULC Change",
        "start_year": 2020,
        "end_year": 2021,
        "admin_zero": 3
    }
]
