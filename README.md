# Auction_api

myrootlib is the main library cointaing (main.py)

routers subpackage containing (users.py,auction.py)
users.py - All endpoints related to users
auction -All Endpoints related to auction

internal subpackage containing (admin.py)
admin.py - All endpoints relay=ted to admin

I have three entites Admin , User and Auction

For Table Creation I have used Tortoise ORM
For Token Generation I have used jwt
For Password Hash Generation I have used bcrypt

Admin Has Three Attributes (Id(PK),Username(Unique),Passowrd)
User Has Three Attributes (Id(PK),Username(Unique),Password)
Auction Has Eight Attributes (Auction_Id(PK),Item_name,Start_time,End_time,Status,Start_price,Cur_highest_bid,User)

FUNCTIONS :
1.To create Admin endpoint=('/admins/admin')
2.To create User endpoint=('/users/user')

ADMIN FUNCTIONS :
1.Admin Can CREATE Auction Items endpoint=('/auctions/auction')
2.Admin Can DELETE Auction Items endpoint=('/auctions/auction/delete/{auction_id}')
3.Admin Can UPDATE Auction Items endpoint=('/auctions/auction/update/{auction_id}')
4.Admin Can READ  All Auction Items endpoint=('/auctions/auction/get/all')


USER FUNCTION :
1.User Can BID On Auction Items endpoint=('/auction/bid/{auction_id},{amount}')
2.User Can READ Auction Items (Ongoing) =('/auctions/auction/user/ongoing')

Admin and Users are Authenticated by Tokens

1.User Token Generation endpoint=('/users/token')
2.Admin Token Generation endpoint=('/admins/token')

WORKING:
- We can create users and admins using above entioned endpoints
- We can create auction items using admin authentication
- Users can we ongoing auctions
- Users can bid on ongoing auctions
- User with highest bid stored in auction (user,cur_higest_bid) field
- After the end time user with highest bid wins and the auction status(status) is changed from ongoing to ended

