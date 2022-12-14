from fastapi import APIRouter
from fastapi import HTTPException,Depends
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from tortoise.models import Model
from passlib.hash import bcrypt
from tortoise import fields
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator
import jwt



router = APIRouter(prefix="/users",
    tags=["users"])

oauth2_scheme_user=OAuth2PasswordBearer(tokenUrl='http://127.0.0.1:8000/users/token',scheme_name='oauth2_scheme_user') # this is the url that the frontend would use to generate the token

JWT_SECRET='myjwtsecret'


class User(Model):
    id = fields.IntField(pk=True) 
    username=fields.CharField(50,unique=True)
    password=fields.CharField(128)

    def verify_password(self,password):
        return bcrypt.verify(password,self.password) # to verify the passwordd

User_Pydantic=pydantic_model_creator(User,name='User') # user object for our application operations
UserIn_Pydantic=pydantic_model_creator(User,name='UserIn',exclude_readonly=True) # user object for taking input

async def authenticate(username : str,password : str):
    user_obj= await User.get(username=username) #returns user obj or null
    if not user_obj:
        return False
    if not user_obj.verify_password(password):
        return False
  
    return user_obj

async def get_current_user(token : str = Depends(oauth2_scheme_user)):
    try:
    
        payload=jwt.decode(token,JWT_SECRET,algorithms=['HS256'])
        if payload.get('user_type')!='user':
            return {'Invalid User'}
            #     raise HTTPException(
            #     status_code=401,
            #     detail='Invalid Username or Password'
            # )
        print(payload.get('user_type'))
        user=await User.get(username=payload.get('username'))
    except:
        raise HTTPException(
            status_code=401,
            detail='Invalid Username or Password'
        )
    return await User_Pydantic.from_tortoise_orm(user)

@router.post('/token')
async def generate_token(form_data : OAuth2PasswordRequestForm = Depends()):
    user=await authenticate(form_data.username,form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail='Invalid Username or Password'
        )
    user_obj=await User_Pydantic.from_tortoise_orm(user)
    payload={'user_type':'user',
    'username':user_obj.username}
    token=jwt.encode(payload,JWT_SECRET)
    return {'access_token':token,'token_type':'bearer'}

@router.post('/user',response_model=User_Pydantic) # api to create users
async def add_User(user : UserIn_Pydantic):
    user_obj=User(username=user.username,password=bcrypt.hash(user.password))
    await user_obj.save()
    return await User_Pydantic.from_tortoise_orm(user_obj) # to convert user object into the user_pydantic

@router.get('/user/me',response_model=User_Pydantic) # user trying to access the url is first authenticated
async def get_user(user : User_Pydantic = Depends(get_current_user)):
    return user


register_tortoise(
    router,
    db_url='sqlite://db.sqlite3', # specifying the database to work with
    modules={'models':['myrootlib.routers.users']},
    generate_schemas=True # if the mentioned database or tables don't exsist it would just create it for us
    # add_exception_handlers=True
)
