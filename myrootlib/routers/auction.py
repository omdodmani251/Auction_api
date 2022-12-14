from fastapi import APIRouter
from datetime import datetime
from fastapi import HTTPException,Depends
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from tortoise.models import Model
from passlib.hash import bcrypt
from tortoise import fields
from .users import User,User_Pydantic,oauth2_scheme_user,get_current_user
from ..internal.admin import Admin,Admin_Pydantic,oauth2_scheme_admin
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator
import jwt

JWT_SECRET='myjwtsecret'


router = APIRouter(prefix="/auctions",
    tags=["auctions"])

oauth2_scheme=OAuth2PasswordBearer(tokenUrl='http://127.0.0.1:8000/admins/token') # this is the url that the frontend would use to generate the token

async def get_current_admin(token : str = Depends(oauth2_scheme_admin)):
    try:
        payload=jwt.decode(token,JWT_SECRET,algorithms=['HS256'])
        if payload.get('user_type')!='admin':
            raise HTTPException(
            status_code=401,
            detail='Invalid Username or Password'
        )
        user=await Admin.get(username=payload.get('username'))
    except:
        raise HTTPException(
            status_code=401,
            detail='Invalid Username or Password'
        )  
    return await Admin_Pydantic.from_tortoise_orm(user)     



class Auction(Model):
    start_time=fields.DatetimeField(auto_now=True)
    end_time=fields.DatetimeField()
    auction_id=fields.IntField(pk=True)
    start_price=fields.BigIntField()
    cur_highest_bid=fields.BigIntField()
    item_name=fields.CharField(50,unique=True)
    user_id=fields.IntField()
    status=fields.CharField(50)



Auction_Pydantic=pydantic_model_creator(Auction,name='Auction') # user object for our application operations
AuctionIn_Pydantic=pydantic_model_creator(Auction,name='AuctionIn',exclude_readonly=True) # user object for taking input

@router.post('/auction',response_model=Auction_Pydantic)
async def create_auction(auction : AuctionIn_Pydantic,admin : Admin_Pydantic= Depends(get_current_admin)):
    auction_obj=Auction(end_time=auction.end_time,start_price=auction.start_price,cur_highest_bid=auction.cur_highest_bid,item_name=auction.item_name,user_id=auction.user_id,status=auction.status)
    await auction_obj.save()
    return await Auction_Pydantic.from_tortoise_orm(auction_obj)

@router.put('/auction/update/{auction_id}',response_model=Auction_Pydantic)
async def update_auction(auction_id : int,auction : AuctionIn_Pydantic,admin : Admin_Pydantic= Depends(get_current_admin)):
    auction_obj=await Auction.get(auction_id=auction_id)
    updated_info=auction.dict(exclude_unset=True)
    updated_info['start_time']=auction_obj.start_time
    updated_info['auction_id']=auction_obj.auction_id
    await auction_obj.update_from_dict(updated_info)
    await auction_obj.save()
    return await Auction_Pydantic.from_tortoise_orm(auction_obj)

@router.delete('/auction/delete/{auction_id}')
async def delete_auction(auction_id : int,admin :Admin_Pydantic= Depends(get_current_admin)):
    obj=await Auction.get(auction_id=auction_id)
    await obj.delete()
    return {'delete':'Successfully'}

@router.get('/auction/get/all')
async def get_all_auctions(admin :Admin_Pydantic= Depends(get_current_admin)):
    response=await Auction.all()
    output=[]
    for auction in response:
        # return auction.start_time
        if auction.end_time.timestamp() < datetime.now().timestamp():
            auction.status='ended'
            await auction.save()
        output.append(await Auction_Pydantic.from_tortoise_orm(auction))
    return {'status':'Ok','response':output}

@router.post('/auction/bid/{auction_id},{amount}')
async def auction_bid(auction_id : int,amount : int,user : User_Pydantic = Depends(get_current_user)):
    try:
        auction=await Auction.get(auction_id=auction_id)
        auction_obj=await AuctionIn_Pydantic.from_tortoise_orm(auction)
        if auction_obj.status!='ongoing':
            return {'error':'Auction is not active'}
        if auction_obj.cur_highest_bid>amount and auction_obj.start_price>amount:
            return {'error':'amount is less than current highest bid or starting price'}

        auction_obj.cur_highest_bid=amount
        auction_obj.user_id=user.id 
        updated_info=auction_obj.dict(exclude_unset=True)
        await auction.update_from_dict(updated_info)
        await auction.save()
        return auction_obj
    except:
        raise HTTPException(
            status_code=401,
            detail='Error Occured'
        )

@router.get('/auction/user/ongoing')
async def get_ongoing_auction(user : User_Pydantic = Depends(get_current_user)):
    response=await Auction.all()
    ongoing=[]
    for auction in response:

        # return auction.start_time
        if auction.end_time.timestamp() < datetime.now().timestamp():
            auction.status='ended'
            await auction.save()
        else:
            ongoing.append(await Auction_Pydantic.from_tortoise_orm(auction))
    return {'status':'Ok','response':response}

register_tortoise(
    router,
    db_url='sqlite://db.sqlite3', # specifying the database to work with
    modules={'models':['myrootlib.routers.auction']},
    generate_schemas=True # if the mentioned database or tables don't exsist it would just create it for us
    # add_exception_handlers=True
)


