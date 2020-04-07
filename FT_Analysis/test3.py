from app.models import Player, Club, League, Transfer
nationality = 'England'
transfers = Transfer.query
transfers = transfers.join(Player).filter(Player.nationality == nationality)
transfers = transfers.filter(Player.age >= 40).filter(Player.position == 'Goalkeeper')
if transfers.count() == 0:
    print('asd')
else:
    for transfer in transfers:
        print(transfer)
