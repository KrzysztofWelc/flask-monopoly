from typing import Union
from random import randint
from app.game.fields import *


class Player:
    colors = ['#ED553B', '#F6B55C', '#3CAEA3', '#20639B']

    def __init__(self, pid: int):
        self.money = 3000
        self.current_field_id = 0
        self.id = pid
        self.owned_fields = []
        self.color = self.colors[self.id]

    def move(self, steps: int):
        old_field_index = self.current_field_id
        if self.current_field_id + steps > len(FIELDS) - 1:
            self.current_field_id = self.current_field_id - len(FIELDS) - 2 + steps
        else:
            self.current_field_id += steps
        print(self.current_field_id)


        new_field_index = self.current_field_id
        if new_field_index < old_field_index:
            self.money += 300


class PlaceholderField:
    def __init__(self, data):
        self.id = data['id']
        self.label = data['label']
        self.type = data['type']

    def on_enter(self, player: Player, game):
        return 'field {} has been stepped on by player {}'.format(self.id, player.id)

class FineField:
    def __init__(self, data):
        self.id = data['id']
        self.label = data['label']
        self.type = data['type']

    def on_enter(self, player: Player, game):
        player.money -= 300
        return 'player {} has lost 300$'.format(player.id)


class CityField:
    def __init__(self, data):
        self.id = data['id']
        self.type = data['type']
        self.label = data['label']
        self.price = data['price']
        self.build_price = data['build_price']
        self.pricing = data['pricing']
        self.owner = None
        self.build = '0'

    def on_enter(self, player: Player, game):
        if not self.owner and player.money > self.price:
            game.can_buy = True
        if self.owner and self.owner != player:
            price = self.pricing[self.build]
            player.money -= price
            self.owner.money += price
        return 'field {} has been stepped on by player {}'.format(self.id, player.id)


class Game:
    def __init__(self, players_count: int):
        self.players = []
        self.current_player_index = 0
        self.board = []
        self.msgs = []
        self.can_buy = False
        self.winner = None

        for i, _ in enumerate(range(players_count)):
            self.players.append(Player(i))

        self._render_board()

    def next_turn(self, payload):
        print(payload)
        if payload['buy']:
            self._sell_field(self.players[self.current_player_index],
                             self.board[self.players[self.current_player_index].current_field_id])
        if payload['build']:
            for field_id in payload['build']:
                self._updated_field_build(field_id)
        self._next_player()
        move = randint(2, 12)
        player = self.players[self.current_player_index]
        player.move(move)
        msg = self.board[player.current_field_id].on_enter(player, self)
        self._add_message(msg)

        self._check_finish()


    def _check_finish(self):
        for player in self.players:
            if player.money < 0:
                self.winner = self.players[player.id-1]


    def _updated_field_build(self, field_id: str):
        field_id = int(field_id)
        for field in self.board:
            if field.id == field_id:
                if field.build == '4': field.build = 'h'
                if field.build == '3': field.build = '4'
                if field.build == '2': field.build = '3'
                if field.build == '1': field.build = '2'
                if field.build == '0': field.build = '1'

                field.owner.money -= field.build_price

    def _sell_field(self, player: Player, field: Union[CityField]):
        player.money -= field.price
        player.owned_fields.append(field)
        field.owner = player


    def _add_message(self, msg):
        self.msgs.append(msg)

    def _next_player(self):
        if self.current_player_index + 1 == len(self.players):
            self.current_player_index = 0
        else:
            self.current_player_index += 1
        self.can_buy = False

    def _render_board(self):
        for field in FIELDS:
            if field['type'] == CITY:
                f = CityField(field)
            elif field['type'] == FINE:
                f = FineField(field)
            else:
                f = PlaceholderField(field)

            self.board.append(f)
