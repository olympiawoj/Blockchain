import requests

user = input('Enter a user ID: ')

def get_balance(userid):
    #get data for chain
    data = requests.get('http://localhost:5000/chain').json()
    #chain is an array of dicts
    chain = data['chain']
    
    total = 0
    #loop over each block in chain 
    for block in chain: 
        #each block as transactions which is an array 
        for t in block['transactions']:
            if t['recipient'] == user:
                total += int(t['amount'])
            if t['sender'] == user:
                total += int(t['amount'])
       
        # print('transactions', userTransations)
    return total 

print(get_balance(user))


# def history():
#     data = get_data(user)
#     print('Transaction History Sent:')
#     for i in data[1]:
#         print(f"{i[0]} ---- {i[1]}")
#     print('\n\n')
#     print('Transactions recived')
#     for i in data[2]:
#         print(f"{i[0]} ---- {i[1]}")

# def total():
#     data = get_data(user)
#     print(data[0])
# def chang_user():
#     user = input('enter user name: ')
#     return(user)


# while True:
#     command = input('Enter command: ')
#     try:
#         if command == 'change user':
#             user = chang_user()
#         else:
#             function = eval(command)
#             function()
#     except:
#         print('not valid command')

