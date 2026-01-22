#Creating a pygame window and responding to user input

import sys
import pygame


class AlienInvasion:
    """Overall Class to manage game assest and behavior"""
    def __init__(self):
        """Initialize the game and create the game resources"""
        pygame.init() #initializes the background settings that pygame needs to work properly.
        self.clock=pygame.time.Clock() #Controlling the frame rate

        self.screen=pygame.display.set_mode((1200,800)) #to create display window
        pygame.display.set_caption("Alien Invasion") 

        #set the background color
        self.bgcolor = (230,230,230)

    def run_game(self): #game ins controller by run_game() method
        """Start the main loop for the game"""
        while True:
            #Watch for keyboard and mouse events.
            for event in pygame.event.get(): ##event is an action that user performance while playing the game, such as pressing keys
                if event.type == pygame.QUIT: 
                    sys.exit()
            
            # Redraw the screen during each pass through the loop
            self.screen.fill(self.bg_color)

            # Make the most recently draw screen visible
            pygame.display.flip()
            self.clock.tick(60)

if __name__=='__main__':
    #make a game instance, and run the game.
    ai = AlienInvasion()
    ai.run_game()        

        