from fastapi import HTTPException
from requests import get, post
from app import settings
from app.core.utils import load_error_json

def get_course(course_id: int, token: str):
    course_request = get(f"{settings.EDUCATIONAL_PROGRAM_URL}/api/v1/course/{course_id}",
                            headers={"Authorization": f"Bearer {token}"}
                            )
    if course_request.status_code == 200:
        return course_request.json()
    raise HTTPException(status_code=course_request.status_code, detail=load_error_json(course_request))

def get_current_user(token: str):
    url = f"{settings.AUTH_SERVER_URL}/api/v1/users/me"
    headers = {"Authorization": f"Bearer {token}"}
    response = get(url, headers=headers)

    print( "AUTHENTICATED_USER_DATA" ,response.json())

    if response.status_code == 200:
        return response.json()
    
    raise HTTPException(status_code=response.status_code, detail=load_error_json(response))

def login_for_access_token(form_data):
    url = f"{settings.AUTH_SERVER_URL}/api/v1/login/access-token"
    data = {
        "username": form_data.username,
        "password": form_data.password
    }
    response = post(url, data=data)

    if response.status_code == 200:
        return response.json()
    
    raise HTTPException(status_code=response.status_code, detail=load_error_json(response))