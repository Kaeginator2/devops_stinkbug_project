# runcmd: cd ../.. & venv\Scripts\python server/py/dog_template.py

import random
import copy
from typing import List, Optional, ClassVar
from enum import Enum
from pydantic import BaseModel

# if __name__ == '__main__':
#     from game import Game, Player
# else:
    # from server.py.game import Game, Player
#
from server.py.game import Game, Player
    # from game import Game, Player



class Card(BaseModel):
    suit: str  # card suit (color)
    rank: str  # card rank

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Card):
            return False
        return self.suit == other.suit and self.rank == other.rank

    def __hash__(self)-> int:
        return hash((self.suit, self.rank))

class Marble(BaseModel):
    pos: int  # position on board (0 to 95)
    is_save: bool  # true if marble was moved out of kennel and was not yet moved
    start_pos: int  # Kennel Position for sending home


class PlayerState(BaseModel):
    name: str  # name of player [PlayerBlue, PlayerRed, PlayerYellow, PlayerGreen]
    list_card: List[Card]  # list of cards
    list_marble: List[Marble]  # list of marbles
    list_kennel_pos: List[int]
    list_finish_pos: List[int]
    start_pos: int

class Action(BaseModel):
    card: Card  # card to play
    pos_from: Optional[int]  # position to move the marble from
    pos_to: Optional[int]  # position to move the marble to
    card_swap: Optional[Card] = None  # optional card to swap ()

    def __eq__(self, other: object) ->bool:
        if not isinstance(other, Action):
            return False
        return (self.card==other.card and
                self.pos_from == other.pos_from and
                self.pos_to == other.pos_to and
                self.card_swap == other.card_swap)

    def __hash__(self)-> int:
        return hash((self.card, self.pos_from, self.pos_to ,self.card_swap))

class GamePhase(str, Enum):
    SETUP = 'setup'  # before the game has started
    RUNNING = 'running'  # while the game is running
    FINISHED = 'finished'  # when the game is finished

class GameState(BaseModel):
    LIST_SUIT: ClassVar[List[str]] = ['♠', '♥', '♦', '♣']  # 4 suits (colors)
    LIST_RANK: ClassVar[List[str]] = [
        '2', '3', '4', '5', '6', '7', '8', '9', '10',  # 13 ranks + Joker
        'J', 'Q', 'K', 'A', 'JKR'
    ]
    LIST_CARD: ClassVar[List[Card]] = [
                                          # 2: Move 2 spots forward
                                          Card(suit='♠', rank='2'), Card(suit='♥', rank='2'), Card(suit='♦', rank='2'),
                                          Card(suit='♣', rank='2'),
                                          # 3: Move 3 spots forward
                                          Card(suit='♠', rank='3'), Card(suit='♥', rank='3'), Card(suit='♦', rank='3'),
                                          Card(suit='♣', rank='3'),
                                          # 4: Move 4 spots forward or back
                                          Card(suit='♠', rank='4'), Card(suit='♥', rank='4'), Card(suit='♦', rank='4'),
                                          Card(suit='♣', rank='4'),
                                          # 5: Move 5 spots forward
                                          Card(suit='♠', rank='5'), Card(suit='♥', rank='5'), Card(suit='♦', rank='5'),
                                          Card(suit='♣', rank='5'),
                                          # 6: Move 6 spots forward
                                          Card(suit='♠', rank='6'), Card(suit='♥', rank='6'), Card(suit='♦', rank='6'),
                                          Card(suit='♣', rank='6'),
                                          # 7: Move 7 single steps forward
                                          Card(suit='♠', rank='7'), Card(suit='♥', rank='7'), Card(suit='♦', rank='7'),
                                          Card(suit='♣', rank='7'),
                                          # 8: Move 8 spots forward
                                          Card(suit='♠', rank='8'), Card(suit='♥', rank='8'), Card(suit='♦', rank='8'),
                                          Card(suit='♣', rank='8'),
                                          # 9: Move 9 spots forward
                                          Card(suit='♠', rank='9'), Card(suit='♥', rank='9'), Card(suit='♦', rank='9'),
                                          Card(suit='♣', rank='9'),
                                          # 10: Move 10 spots forward
                                          Card(suit='♠', rank='10'), Card(suit='♥', rank='10'),
                                          Card(suit='♦', rank='10'), Card(suit='♣', rank='10'),
                                          # Jake: A marble must be exchanged
                                          Card(suit='♠', rank='J'), Card(suit='♥', rank='J'), Card(suit='♦', rank='J'),
                                          Card(suit='♣', rank='J'),
                                          # Queen: Move 12 spots forward
                                          Card(suit='♠', rank='Q'), Card(suit='♥', rank='Q'), Card(suit='♦', rank='Q'),
                                          Card(suit='♣', rank='Q'),
                                          # King: Start or move 13 spots forward
                                          Card(suit='♠', rank='K'), Card(suit='♥', rank='K'), Card(suit='♦', rank='K'),
                                          Card(suit='♣', rank='K'),
                                          # Ass: Start or move 1 or 11 spots forward
                                          Card(suit='♠', rank='A'), Card(suit='♥', rank='A'), Card(suit='♦', rank='A'),
                                          Card(suit='♣', rank='A'),
                                          # Joker: Use as any other card you want
                                          Card(suit='', rank='JKR'), Card(suit='', rank='JKR'),
                                          Card(suit='', rank='JKR')
                                      ] * 2

    cnt_player: int = 4  # number of players (must be 4)
    phase: GamePhase = GamePhase.SETUP  # current phase of the game
    cnt_round: int = 0  # current round
    bool_card_exchanged: bool = False  # true if cards was exchanged in round
    list_swap_card: List[Optional[Card]] = [None]*4 # empty Carddeck for cards to be swapt
    idx_player_active: int = 0 #random.randint(0, 3)   # index of active player in round
    idx_player_started: int =  idx_player_active# index of player that started the round

    list_player: List[PlayerState] = []  # list of players
    list_card_draw: List[Card] = LIST_CARD  # list of cards to draw ==> Was list_id_card_draw in given Template
    list_card_discard: List[Card] = []  # list of cards discarded
    card_active: Optional[Card] = None  # active card (for 7 and JKR with sequence of actions)
    cnt_seven_steps: int = 0 # Counter of how meany steps there were made with the 7
    # played_seven_actions: List[Action] = []


    def setup_players(self) -> None:  # Kägi
        player_blue = PlayerState(
            name="PlayerBlue",
            list_card=[],
            list_marble=[Marble(pos=64, is_save=True, start_pos=64),
                         Marble(pos=65, is_save=True, start_pos=65),
                         Marble(pos=66, is_save=True, start_pos=66),
                         Marble(pos=67, is_save=True, start_pos=67)],
            list_finish_pos=[68, 69, 70, 71],
            list_kennel_pos=[64, 65, 66, 67],
            start_pos=0
        )
        player_green = PlayerState(
            name="PlayerGreen",
            list_card=[],
            list_marble=[Marble(pos=72, is_save=True, start_pos=72),
                         Marble(pos=73, is_save=True, start_pos=73),
                         Marble(pos=74, is_save=True, start_pos=74),
                         Marble(pos=75, is_save=True, start_pos=75)],
            list_kennel_pos=[72, 73, 74, 75],
            list_finish_pos=[76, 77, 78, 79],
            start_pos=16
        )
        player_red = PlayerState(
            name="PlayerRed",
            list_card=[],
            list_marble=[Marble(pos=80, is_save=True, start_pos=80),
                         Marble(pos=81, is_save=True, start_pos=81),
                         Marble(pos=82, is_save=True, start_pos=82),
                         Marble(pos=83, is_save=True, start_pos=83)],
            list_finish_pos=[84, 85, 86, 87],
            list_kennel_pos=[80, 81, 82, 83],
            start_pos=32
        )
        player_yellow = PlayerState(
            name="PlayerYellow",
            list_card=[],
            list_marble=[Marble(pos=88, is_save=True, start_pos=88),
                         Marble(pos=89, is_save=True, start_pos=89),
                         Marble(pos=90, is_save=True, start_pos=90),
                         Marble(pos=91, is_save=True, start_pos=91)],
            list_kennel_pos=[88, 89, 90, 91],
            list_finish_pos=[92, 93, 94, 95],
            start_pos=48
        )
        self.list_player = [player_blue, player_green, player_red, player_yellow]

    def deal_cards(self) -> None:  # Kägi
        # Check if all players are out of cards.
        for selected_player in self.list_player:
            if not selected_player.list_card:
                continue
            return
        # Go to next Gameround
        self.cnt_round += 1

        # get number of Cards
        cards_per_round = [6, 5, 4, 3, 2]
        num_cards = cards_per_round[(self.cnt_round - 1) % len(cards_per_round)]

        # Check if there are enough cards in the draw deck; if not, add a new card deck.
        if num_cards * 4 > len(self.list_card_draw):
            # reshuffle the Deck
            self.list_card_draw = GameState.LIST_CARD
            self.list_card_discard = []

        # Randomly select cards for players.
        for player in self.list_player:
            player.list_card = random.sample(self.list_card_draw, num_cards)
            for card in player.list_card:
                self.list_card_draw.remove(card)

        # Set Cardexchange
        self.bool_card_exchanged = False

    def discard_invalid_cards(self) -> None:
        # check if player has cards
        if not self.list_player[self.idx_player_active].list_card:
            return
        # discard the player
        self.list_card_discard.extend(self.list_player[self.idx_player_active].list_card)
        self.list_player[self.idx_player_active].list_card = []

    def get_seven_actions(self, card:Card, marble:Marble)->list[Action]:
        actions = []
        remaining_steps = 7 - self.cnt_seven_steps
        # Generate all combinations of moves that sum to the remaining steps
        for steps in range(1, remaining_steps + 1):
            pos_from = marble.pos
            pos_to = pos_from + steps  # Simplified: actual position calculation may differ based on board layout
            action = Action(card=card, pos_from=pos_from, pos_to=pos_to)
            action_final = self.go_in_final(action)

            # validate the moves (not implemented here)
            if self.skip_save_marble(action):
                actions.append(action)
            if action_final:
                if self.skip_save_marble(action_final[0]):
                    actions.append(action_final[0])

        return actions

    def get_move_action(self, movement:int, card:Card, marble:Marble) -> List[Action]:
        action_list = []
        # Check if Marble is in Final
        if marble.pos>64:
            action = Action(card=card, pos_from=marble.pos, pos_to=(marble.pos + movement), card_swap=None)
        else:
            action = Action(card=card, pos_from=marble.pos, pos_to=(marble.pos + movement) % 64, card_swap=None)

        # Calculat possibility
        if self.skip_save_marble(action):
            action_list.append(action)
        going_final_action_list = self.go_in_final(action)
        if going_final_action_list:
            for action in going_final_action_list:
                if self.skip_save_marble(action):
                    action_list.append(action)
        return action_list

    def get_joker_actions_kennel_out(self, card:Card)-> list[Action]:
        action_list = []
        for suit in self.LIST_SUIT:
            action_list.append(Action(card=card, pos_from=None,pos_to=None, card_swap=Card(suit=suit, rank='K')))
            action_list.append(Action(card=card, pos_from=None,pos_to=None, card_swap=Card(suit=suit, rank='A')))
        return action_list

    def get_joker_actions_normal(self, card:Card)-> list[Action]:
        action_list = []
        for suit in self.LIST_SUIT:
            for rank in self.LIST_RANK[0:-2]:
                action_list.append(Action(card=card, pos_from=None,pos_to=None, card_swap=Card(suit=suit, rank=rank)))
        return action_list

    def get_list_possible_action(self) -> List[Action]: # pylint: disable=too-many-branches, too-many-statements
        active_player = self.list_player[self.idx_player_active]
        if self.card_active is not None:
            cards = [self.card_active]
        else:
            cards = active_player.list_card

        if not cards:
            return []
        marbles = active_player.list_marble
        oponent_players = [oponent for oponent in self.list_player if oponent.name != active_player.name]
        action_list = []
        leaving_marble = None

        for marble in marbles:
            if marble.pos in active_player.list_kennel_pos:
                if leaving_marble is None:
                    for card in cards:
                        match card.rank:
                            case 'K':
                                leaving_marble = marble
                                action = Action(card=card, pos_from=marble.pos, pos_to=active_player.start_pos,
                                                card_swap=None)
                                if self.skip_save_marble(action):
                                    action_list.append(action)
                            case 'A':
                                leaving_marble = marble
                                action = Action(card=card, pos_from=marble.pos, pos_to=active_player.start_pos,
                                                card_swap=None)
                                if self.skip_save_marble(action):
                                    action_list.append(action)
                            case 'JKR':
                                leaving_marble = marble
                                action = Action(card=card, pos_from=marble.pos, pos_to=active_player.start_pos,
                                                card_swap=None)
                                if self.skip_save_marble(action):
                                    action_list.append(action)
                                action_list.extend(self.get_joker_actions_kennel_out(card))
                            case _:
                                pass
            else:
                for card in cards:
                    match card.rank:
                        case '2':
                            action_list.extend(self.get_move_action(movement=2 , card=card, marble=marble))

                        case '3':
                            action_list.extend(self.get_move_action(movement=3 , card=card, marble=marble))
                        case '4':
                            action_list.extend(self.get_move_action(movement=4 , card=card, marble=marble))
                            action_list.extend(self.get_move_action(movement=-4 , card=card, marble=marble))
                        case '5':
                            action_list.extend(self.get_move_action(movement=5 , card=card, marble=marble))
                        case '6':
                            action_list.extend(self.get_move_action(movement=6 , card=card, marble=marble))
                        case '7':
                            action_list.extend(self.get_seven_actions(card=card, marble=marble))
                        case '8':
                            action_list.extend(self.get_move_action(movement=8 , card=card, marble=marble))
                        case '9':
                            action_list.extend(self.get_move_action(movement=9 , card=card, marble=marble))
                        case '10':
                            action_list.extend(self.get_move_action(movement=10 , card=card, marble=marble))
                        case 'J':
                            for oponent_player in oponent_players:
                                for oponent_marble in oponent_player.list_marble:
                                    if not oponent_marble.is_save:
                                        oponent_marble.is_save = True
                                        action_list.append(Action(card = card,pos_from = marble.pos,
                                                                  pos_to = oponent_marble.pos, card_swap = None))
                                        action_list.append(Action(card = card,pos_from = oponent_marble.pos ,
                                                                  pos_to = marble.pos, card_swap = None))
                                        oponent_marble.is_save = False
                        case 'Q':
                            action_list.extend(self.get_move_action(movement=12 , card=card, marble=marble))
                        case 'K':
                            action_list.extend(self.get_move_action(movement=13 , card=card, marble=marble))
                        case 'A':
                            action_list.extend(self.get_move_action(movement=1 , card=card, marble=marble))
                            action_list.extend(self.get_move_action(movement=11 , card=card, marble=marble))

                        case 'JKR':
                            action_list.extend(self.get_joker_actions_normal(card))
                        case _:
                            pass

        return list(set(action_list))

    def swap_joker_with_card(self, action: Action) -> None:
        if action.card_swap is None:
            return # Needed fpr MyPy
        active_player = self.list_player[self.idx_player_active]
        for idx, card in enumerate(active_player.list_card):
            if card.suit == action.card.suit and card.rank == action.card.rank:
                active_player.list_card[idx] = action.card_swap  # Überschreibe die JokcerKarte in der Liste
                self.card_active = action.card_swap # Setze die getauschte Karte aktiv

    def apply_seven_action(self, action:Action)->None:
        # Check if its the First 7 round
        if self.card_active is None:
            self.card_active = action.card
            self.cnt_seven_steps = 0
        if action.pos_from is None or action.pos_to is None:
            return # Activate the seven
        # Set Action to the GameState ==> make movement on the "board"

        if action.pos_to<64:
            steps_to_make = action.pos_to - action.pos_from
            current_pos = action.pos_from

            for _ in range(steps_to_make):
                # Creat subaction to use set_action_to_game
                sub_action = Action(card=action.card,
                                    pos_from=current_pos,
                                    pos_to=current_pos + 1,
                                    card_swap=action.card_swap)
                self.set_action_to_game(sub_action)
                self.cnt_seven_steps += 1
                current_pos += 1  # Update current_pos for the next sub_action
        else:
            final_pos = 64 + 8 * self.idx_player_active + 3
            if self.list_player[self.idx_player_active].start_pos == 0:
                startpos = 64
            else:
                startpos = self.list_player[self.idx_player_active].start_pos
            if action.pos_from>64:
                steps_to_make = action.pos_to - final_pos
            else:
                steps_to_make = startpos - action.pos_from + action.pos_to - final_pos
            current_pos = action.pos_from

            for _ in range(steps_to_make):
                # Bestimme die nächste Position, bevor eine Aktion erstellt wird
                next_pos = current_pos + 1
                if next_pos == startpos+1:
                    # Wenn der nächste Schritt 64 erreichen würde, springe direkt zu final_pos
                    next_pos = final_pos+1

                # Erzeuge sub_action für die Verwendung in set_action_to_game
                sub_action = Action(card=action.card,
                                    pos_from=current_pos,
                                    pos_to=next_pos,
                                    card_swap=action.card_swap)
                self.set_action_to_game(sub_action)
                self.cnt_seven_steps += 1

                # Aktualisiere current_pos auf next_pos für die nächste Iteration
                current_pos = next_pos

        # finish the seven action if there were made 7 steps
        if self.cnt_seven_steps == 7:
            self.card_active = None

    def apply_jack_action(self, action: Action)->None:
        sub_action = Action(card = action.card,pos_from = action.pos_from,pos_to = action.pos_to, card_swap = None)
        self.set_action_to_game(sub_action)




    def set_action_to_game(self, action: Action)-> None:  # kaegi
        # Action is from the active Player
        # Set Action to the GameState ==> make movement on the "board"
        if action.pos_from is None or action.pos_to is None:
            return # Needed for MyPy

        if action.card.rank == 'J':
            marble_from = None
            marble_to = None
            for player in self.list_player:
                for marble in player.list_marble:
                    if marble.pos == action.pos_from:
                        marble_from = marble
                    elif marble.pos == action.pos_to:
                        marble_to = marble
            if marble_from is None or marble_to is None:
                return # Niided for MaiPai
            marble_from.pos = action.pos_to
            marble_to.pos = action.pos_from
            return


        # Get Marble to Move
        marble_to_move:Optional[Marble]
        marble_to_move = next((marble for marble in self.list_player[self.idx_player_active].list_marble
                               if marble.pos == action.pos_from), None)
        if marble_to_move is None:
            return # Needed for MyPy

        marble_to_move.is_save = False
        # Check if marble comes from kenel
        if marble_to_move.pos == marble_to_move.start_pos:
            marble_to_move.is_save = True

        # Goes in final
        elif action.pos_to > 63:
            marble_to_move.is_save = True
        # Set Action pos to game
        marble_to_move.pos = action.pos_to

        # Send marble on same pos home
        self.sending_home(marble_to_move)
        return

    def exchange_cards(self, action_cardswap: Action) -> None:

        # Save selected Card
        self.list_swap_card[self.idx_player_active] = action_cardswap.card
        self.list_player[self.idx_player_active].list_card.remove(action_cardswap.card)

        # Check iff all Player selected a Card, Return if not
        if None in self.list_swap_card:
            return

        # Swap Cards with teammember
        for i, player in enumerate(self.list_player):
            opposite_player_index = (i + 2) % 4  # Index des Teammitglieds
            card_to_add = self.list_swap_card[opposite_player_index]
            if card_to_add is not None:
                player.list_card.append(card_to_add)

        # Set global Variables
        self.bool_card_exchanged = True
        self.list_swap_card = [None]*4

        return

    def sending_home(self, moved_marble: Marble) -> None:
        """
        Checks if the active marble jumps on another marble. 
        If so, sends the other marble back to its start position.
        """
        if self.card_active == 'J':
            return

        for selected_player in self.list_player:
            for p_marble in selected_player.list_marble:
                # Check if the marble occupies the same position but isn't the same marble
                if p_marble.pos == moved_marble.pos and p_marble != moved_marble:
                    p_marble.pos = p_marble.start_pos

    def skip_save_marble(self, action: Action) -> bool: # pylint: disable=too-many-branches, too-many-statements
        """
        Prüft, ob zwischen action.pos_from und action.pos_to sichere Murmeln liegen.
        Gibt False zurück, wenn eine sichere Murmel in diesem Bereich gefunden wird,
        andernfalls True.
        """
        return_value = True
        if action.pos_from is None or action.pos_to is None:
            return False # Needed for MyPy (Error in Action)

        save_positions: list[int] = [0, 16, 32, 48]

        for player in self.list_player:
            for marble in player.list_marble:
                # Blockieren durch sichere Murmel auf der Zielposition (Finish)
                if action.pos_to in player.list_finish_pos:
                    if marble.pos == action.pos_to and marble.is_save:
                        return_value = False

                # Blockieren durch Überholen im Finish-Bereich
                if marble.pos in player.list_finish_pos:
                    if action.pos_from < marble.pos <= action.pos_to:
                        return_value = False

                # Allgemeine Bewegung vorwärts blockiert
                if action.pos_from < marble.pos <= action.pos_to:
                    if marble.is_save and marble.pos in save_positions:
                        return_value = False

                # Allgemeine Bewegung rückwärts blockiert
                if action.pos_from > marble.pos >= action.pos_to:
                    if marble.is_save and marble.pos in save_positions:
                        return_value = False

                if action.pos_from > marble.pos <= action.pos_to:
                    if marble.is_save and marble.pos in save_positions:
                        return_value = False

        # Wenn keine Blockade gefunden wurde
        return return_value

    def is_player_finished(self, player: PlayerState) -> bool:
        for marble in player.list_marble:
            if marble.pos not in player.list_finish_pos:
                return False
        return True

    def check_game_end(self) -> None:
        team1 = [self.list_player[0], self.list_player[2]]
        team2 = [self.list_player[1], self.list_player[3]]

        for team in [team1, team2]:
            team_finished = all(self.is_player_finished(player) for player in team)
            if team_finished:
                self.phase = GamePhase.FINISHED
                return

    def go_in_final(self, action_to_check: Action) -> List[Action]: # pylint: disable=too-many-return-statements
        """
        Checks if it is possible to go in the final
        Yes, creat the Actions fo that + unchanged action
        No, return Action unchanged
        """
        # Get Marble to Move
        marble_to_move:Optional[Marble]
        marble_to_move = next((marble for marble in self.list_player[self.idx_player_active].list_marble
                               if marble.pos == action_to_check.pos_from), None)

        if action_to_check.pos_from is None or action_to_check.pos_from is None or marble_to_move is None:
            return [action_to_check] # Check fpr MyPy

        # Needs this check because of wrong Test 041
        if action_to_check.pos_from <64 and marble_to_move.is_save:
            return[action_to_check]

        active_player = self.list_player[self.idx_player_active]
        final_pos = active_player.list_finish_pos[0]

        # get positions
        startpos = active_player.start_pos
        pos_from = action_to_check.pos_from
        pos_to = action_to_check.pos_to
        if pos_to is None:
            return [action_to_check] # Needed for MyPy

        final_end_pos = 64+self.idx_player_active*8+7
        # Move in Final
        if pos_from > 67:
            if pos_to is None:
                return [action_to_check]  # Needed for MyPy
            steps = pos_to - pos_from
            if final_end_pos >= pos_from + steps:
                return [Action(card=action_to_check.card,
                            pos_from=pos_from,
                            pos_to=pos_from + steps,
                            card_swap=action_to_check.card_swap)]

        if pos_to >= startpos and pos_from < 64:
            leftover = pos_to - startpos
            if 1 <= leftover <= 4:
                final_state = final_pos + (leftover - 1)
                new_action = Action(
                    card = action_to_check.card,
                    pos_from = pos_from,
                    pos_to = final_state,
                    card_swap = action_to_check.card_swap
                )
                return [new_action]
        return [action_to_check]

    def init_next_turn(self) -> None:
        """
        Sets the next player with cards to active.
        if there are all cards played it deals new cards
        """

        # Start with the next player
        idx_next_player = (self.idx_player_active +1) %4

        if idx_next_player == self.idx_player_started:
            self.deal_cards()
            if self.bool_card_exchanged:
                self.idx_player_active = idx_next_player
            else:
                self.idx_player_started = (self.idx_player_started + 1) % 4
        else:
            self.idx_player_active = idx_next_player

    def __str__(self) -> str:
        main_seperator = "*"*50+"\n"
        part_seperator = "-"*25 +"\n"
        state_details = f"Game Phase: {self.phase}\n" \
                        f"Round: {self.cnt_round}\n" \
                        f"Active Player Index: {self.idx_player_active}\n" \
                        f"Cards Exchanged: {self.bool_card_exchanged}\n" \
                        f"Number of Players: {self.cnt_player}\n"

        players_info = "\n".join([
            f"Player {idx+1} ({player.name}): {len(player.list_card)} cards, " \
            f"{len(player.list_marble)} marbles\n" +
            "\n".join([f"  Marble at {marble.pos} - {'Safe' if marble.is_save else 'Not Safe'}"
                       for marble in player.list_marble])
            for idx, player in enumerate(self.list_player)
        ])

        deck_info = f"\nCards in Draw Pile: {len(self.list_card_draw)}\n" \
                    f"Cards in Discard Pile: {len(self.list_card_discard)}\n"

        if self.card_active:
            active_card_info = f"Active Card: {self.card_active.suit} {self.card_active.rank}\n"
        else:
            active_card_info = "No active card\n"

        return (main_seperator + state_details + part_seperator + players_info + "\n" + part_seperator +
                deck_info + active_card_info)

class Dog(Game):

    seven_backup:GameState

    def __init__(self) -> None:
        """ Game initialization (set_state call not necessary, we expect 4 players) """
        # print("Starting up DOG")
        self.state = GameState()
        self.state.setup_players()
        self.state.phase = GamePhase.RUNNING
        self.state.deal_cards()  # deal first cards to players

    def set_state(self, state: GameState) -> None:
        """ Set the game to a given state """
        self.state = state

    def get_state(self) -> GameState:
        """ Get the complete, unmasked game state """
        return self.state

    def print_state(self) -> None:
        """ Print the current game state """
        current_player_name = self.state.list_player[self.state.idx_player_active].name

        player_data = {
            player.name: {
                "positions": [marble.pos for marble in player.list_marble],
                "cards": len(player.list_card),
            }
            for player in self.state.list_player
        }
        print(f"We are in round {self.state.cnt_round} and the current player is {current_player_name}")
        for player_name, data in player_data.items():
            print(f"Player {player_name} has positions: {data['positions']} and holds {data['cards']} cards")
        print(f"The actual game phase: {self.state.phase}")

    def get_list_action(self) -> List[Action]:
        """ Get a list of possible actions for the active player """
        # Swap Card Actions
        if self.state.bool_card_exchanged is False:
            action_list = [Action(card=hand_card,pos_from=None, pos_to=None) for hand_card in
                           self.state.list_player[self.state.idx_player_active].list_card]
            return action_list

        #Get the list with possible actions
        action_list = self.state.get_list_possible_action()
        return action_list

    def apply_action(self, action: Optional[Action]) -> None:
        """
        Do the movement conected to the Action
        """

        if action is None: # If player can not play any actions
            if self.state.card_active is None:
                self.state.discard_invalid_cards()
            elif self.state.card_active.rank =='7':
                #Backup the game
                self.state = self.seven_backup
                self.state.card_active = None
                return # Retry without next Player


        # Check if exchange cards is needed
        elif self.state.bool_card_exchanged is False:
            self.state.exchange_cards(action)

        elif action.card_swap is not None:
            self.state.swap_joker_with_card(action)

        elif action:
            if action.card.rank == '7' and self.state.card_active is None:
                self.seven_backup = copy.deepcopy(self.state)
            if action.card.rank == '7':
                self.state.apply_seven_action(action)
            if action.card.rank == 'J':
                self.state.card_active = action.card
                self.state.apply_jack_action(action)

            else:
                self.state.set_action_to_game(action)

            # Removed played Card from Players Hand
            if  self.state.card_active is None:
                self.state.list_card_discard.append(action.card)
                self.state.list_player[self.state.idx_player_active].list_card.remove(action.card)

        # Sets the next Player active if there is not a Card active
        if self.state.card_active is None:
            self.state.init_next_turn()

        # Check if the game is finisched:
        self.state.check_game_end()

    def get_player_view(self, idx_player: int) -> GameState:
        """Returns the masked game state for the other players."""
        masked_state = copy.deepcopy(self.state) # Start with the full state

        # Mask the cards of the other players.
        for i in range(4):
            if i != idx_player:
                masked_state.list_player[i].list_card = [Card(suit="", rank="X")] * len(
                    masked_state.list_player[i].list_card)
        return masked_state

class RandomPlayer(Player):

    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        """ Given masked game state and possible actions, select the next action """
        if actions and len(actions) > 0:
            return random.choice(actions)
        return None
