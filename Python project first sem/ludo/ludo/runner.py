from .game import Player, Game
from .painter import present_6_die_name
from os import linesep
class rungame():
    def __init__(self): 
        self.prompt_end = "> "
        self.game = Game()
        self.prompted_for_pawn = False
    
    def validate_input(self, prompt, desire_type, allawed_input=None,error_mess="Invalid Option!", str_len=None):
        prompt += linesep + self.prompt_end
        while True:
            choice = input(prompt)
            if not choice:
                print(linesep + error_mess)
                continue
            try:
                choice = desire_type(choice)
            except ValueError:
                print(linesep + error_mess)
                continue
            if allawed_input:
                if choice in allawed_input:
                    break
                else:
                    print("Invalid Option!")
                    continue
            elif str_len:
                min_len, max_len = str_len
                if min_len < len(choice) < max_len:
                    break
                else:
                    print(linesep + error_mess)
            else:
                break
        print()
        return choice

    def get_user_initial_choice(self):
        text = linesep.join(["Enter 0 to start new game"])
        choice = self.validate_input(text, int, (0))
        return choice

    def prompt_for_player(self):
        available_colours = self.game.get_available_colours()
        text = linesep.join(["choose type of player",
                             "0 - computer",
                             "1 - human"])
        choice = self.validate_input(text, int, (0, 1))

        if choice == 1:
            name = self.validate_input("Enter name for player",
                                       str, str_len=(1, 30))
            available_options = range(len(available_colours))
            if len(available_options) > 1:
                options = ["{} - {}".format(index, colour)
                           for index, colour in
                           zip(available_options,
                           available_colours)]
                text = "choose colour" + linesep
                text += linesep.join(options)
                choice = self.validate_input(text, int, available_options)
                colour = available_colours.pop(choice)
            else:
                colour = available_colours.pop()
            player = Player(colour, name, self.prompt_choose_pawn)
        elif choice == 0:
            colour = available_colours.pop()
            player = Player(colour)
        self.game.add_palyer(player)

    def prompt_for_players(self):
        counts = ("first", "second", "third", "fourth last")
        text_add = "Add {} player"
        for i in range(2):
            print(text_add.format(counts[i]))
            self.prompt_for_player()
            print("Player added")

        text = linesep.join(["Choose option:","0 - add player","1 - start game with {} players"])
        for i in range(2, 4):
            choice = self.validate_input(text.format(str(i)), int, (0, 1))
            if choice == 1:
                break
            elif choice == 0:
                print(text_add.format(counts[i]))
                self.prompt_for_player()
                print("Player added")

    def prompt_choose_pawn(self):
        text = present_6_die_name(self.game.rolled_value,
                                  str(self.game.curr_player))
        text += linesep + "has more than one possible pawns to move."
        text += " Choose pawn" + linesep
        pawn_options = ["{} - {}".format(index + 1, pawn.id)
                        for index, pawn
                        in enumerate(self.game.allowed_pawns)]
        text += linesep.join(pawn_options)
        index = self.validate_input(
            text, int, range(1, len(self.game.allowed_pawns) + 1))
        self.prompted_for_pawn = True
        return index - 1

    def prompt_to_continue(self):
        text = "press Enter to continue" + linesep
        input(text)

    def print_players_info(self):
        word = "start" if self.game.rolled_value is None else "continue"
        print("Game {} with {} players:".format(
              word,
              len(self.game.players)))
        for player in self.game.players:
            print(player)
        print()

    def print_info_after_turn(self):
        pawns_id = [pawn.id for pawn in self.game.allowed_pawns]
        message = present_6_die_name(self.game.rolled_value,
                                     str(self.game.curr_player))
        message += linesep
        if self.game.allowed_pawns:
            message_moved = "{} is moved. ".format(
                self.game.picked_pawn.id)
            if self.prompted_for_pawn:
                self.prompted_for_pawn = False
                print(message_moved)
                return
            message += "{} possible pawns to move.".format(
                " ".join(pawns_id))
            message += " " + message_moved
            if self.game.jog_pawns:
                message += "Jog pawn "
                message += " ".join([pawn.id for pawn in self.game.jog_pawns])
        else:
            message += "No possible pawns to move."
        print(message)

    def print_standing(self):
        standing_list = ["{} - {}".format(index + 1, player) for index, player in enumerate(self.game.standing)]
        message = "Standing:" + linesep + linesep.join(standing_list)
        print(message)

    def print_board(self):
        print(self.game.get_board_pic())

    def load_players_for_new_game(self):
        self.prompt_for_players()
        self.print_players_info()

    def play_game(self):
        try:
            while not self.game.finished:
                self.game.play_turn()
                self.print_info_after_turn()
                self.print_board()
                self.prompt_to_continue()
            print("Game finished")
            self.print_standing()
           
        except (KeyboardInterrupt, EOFError):
            print(linesep +
                  "Exiting game. ")
            raise

    def start(self):
        print()
        try:
            choice = self.get_user_initial_choice()
            if choice == 0:  # start new game
                self.load_players_for_new_game()
                self.play_game()
        except (KeyboardInterrupt, EOFError):
            print(linesep + "Exit Game")
if __name__ == '__main__':
    rungame().start()
